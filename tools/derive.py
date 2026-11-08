"""Connection layer: compute what one model takes from the others and write it into the model JSON.

    python tools/derive.py place            Full matrix, Compact matrix, Content unit ↔ Recipe
    python tools/derive.py fit-maps         the 4 derived fit maps, composed from the 7 source maps and the space
    python tools/derive.py recipes          Possibilities: what fits each audience at each state
    python tools/derive.py transformations  Candidates, Content unit ↔ Transformation, Content unit ↔ Repurposing
    python tools/derive.py template         Template counts per state: recipes on the stage sheet, content units at the state
    python tools/derive.py all              all five, in that order
    add --dry-run to report what would change without writing

Source fit maps (Format State, Format Ownership, Channel State, Ownership State, Format Surface, Channel Surface,
Audience State) are inputs and are never written. The derived maps read only the source maps and columns of the space.
"""
import argparse
import json
import sys

import models
from atlas import load, split

SOURCE_MAPS = ["Format State Fit", "Format Ownership Fit", "Channel State Fit", "Ownership State Fit",
               "Format Surface Fit", "Channel Surface Fit", "Audience State Fit"]
LEAD = {"Key", "Format", "Format family", "Channel", "Channel family", "Surface family", "Typical funnel fit", "Audience group", "Buying role"}


# ---------- matrix ----------
def derive_matrix():
    import resolve as schema
    t = schema.tables()
    doc = models.read("place")
    full = models.sheet(doc, "Full matrix")
    derived = list(models.sheet(doc, "Full matrix")["derived"])
    changes = 0
    ids = [r["ID"] for r in models.sheet(doc, "Content Units")["rows"]]
    if [r["ID"] for r in full["rows"]] != ids:  # one Full matrix row per content unit, in content-unit order
        have = {r["ID"]: r for r in full["rows"]}
        full["rows"] = [have.get(i, {"ID": i}) for i in ids]
        changes += 1
        models.write("place", doc)  # tables() reads from disk: the new rows must be there before it resolves them
        t = schema.tables()
    resolved = {r.get("ID"): r for r in t["Full matrix"].rows}
    for row in full["rows"]:
        new = resolved[row["ID"]]
        for c in derived:
            if row.get(c) != new.get(c):
                row[c] = new.get(c)
                changes += 1
    compact = models.sheet(doc, "Compact matrix")
    rows = [{c: r.get(c) for c in compact["columns"]} for r in full["rows"]]  # each column is the Full matrix column of that name
    changes += sum(1 for a, b in zip(rows, compact["rows"]) if a != b) + abs(len(rows) - len(compact["rows"]))
    compact["rows"] = rows
    changes += _set_rows(doc, "Content unit ↔ Recipe", unit_recipe_rows(full["rows"]))
    return doc, changes


def _set_rows(doc, name, rows):
    """Replace a view sheet's rows; the number of changed rows."""
    s = models.sheet(doc, name)
    changes = sum(1 for a, b in zip(rows, s["rows"]) if a != b) + abs(len(rows) - len(s["rows"]))
    s["rows"] = rows
    return changes


def _key(o, k):
    return (o.get(k) or {}).get("key")


def unit_recipe_rows(units):
    """Content unit ↔ Recipe: recipe options that produce each unit as it is: same state, and the option's format, channel
    and surface (where named) equal the unit's."""
    recipes = models.recipes()
    out = []
    for u in units:
        want = {"format": u.get("Format"), "channel": u.get("Primary channel"), "surface": u.get("Primary surface")}
        for p in recipes:
            if u.get("State") not in p["states"]:
                continue
            for o in p["kit"]:
                named = {k: _key(o, k) for k in want if o.get(k)}
                if named and all(want[k] == v for k, v in named.items()):
                    out.append({"Content unit ID": u["ID"], "Content unit": u.get("Content unit name"), "Recipe ID": p["id"],
                                "Recipe": p["name"], "Option": o["option"], "Matches on": ", ".join(k for k in want if k in named)})
    return out


# ---------- transformation candidates ----------
CANDIDATE_COLUMNS = ["Source format", "Target format", "Marker", "Content units", "Recipes"]


def derive_candidates():
    """Candidates: format pairs not marked in Format transformations that the other verticals point at. Content units = units
    whose format repurposes into the target; Recipes = recipes with both formats as options. Marker = the direction the
    formats' Typical length gives. Nothing here is written into Format transformations."""
    doc = models.read("transformations")
    ft = models.sheet(doc, "Format transformations")
    marked = {(r["Key"], c) for r in ft["rows"] for c, v in r.items() if v in ("Down", "Up", "Across")}
    formats = {r["Key"]: r for r in models.sheet(models.read("space"), "Formats")["rows"]}
    size = {"Short": 1, "Medium": 2, "Long": 3}

    def marker(a, b):
        sa, sb = size[formats[a]["Typical length"]], size[formats[b]["Typical length"]]
        return "Down" if sa > sb else "Up" if sa < sb else "Across"

    units, recipes = {}, {}
    place = models.read("place")
    fmt = {r["ID"]: r.get("Format") for r in models.sheet(place, "Full matrix")["rows"]}
    for u in models.sheet(place, "Content Units")["rows"]:
        a = fmt.get(u["ID"])
        for b in split(u.get("Repurposes into")):
            if a and b != a and (a, b) not in marked:
                units.setdefault((a, b), []).append(u["ID"])
    for p in models.recipes():
        fs = list(dict.fromkeys(o["format"]["key"] for o in p["kit"] if o.get("format")))
        for a in fs:
            for b in fs:
                if a != b and (a, b) not in marked:
                    recipes.setdefault((a, b), []).append(p["id"])
    order = list(formats)
    pairs = sorted(set(units) | set(recipes), key=lambda ab: (order.index(ab[0]), order.index(ab[1])))
    rows = [{"Source format": a, "Target format": b, "Marker": marker(a, b),
             "Content units": ", ".join(units.get((a, b), [])) or None,
             "Recipes": ", ".join(dict.fromkeys(recipes.get((a, b), []))) or None} for a, b in pairs]
    names = [x["name"] for x in doc["sheets"]]
    if "Candidates" not in names:
        doc["sheets"].append({"name": "Candidates", "title": "Candidates", "description": None, "header_row": 3,
                              "columns": CANDIDATE_COLUMNS, "rows": []})
    c = models.sheet(doc, "Candidates")
    c["description"] = ("Format pairs not marked in Format transformations that content units or recipes point at: a unit whose "
                        "format repurposes into the target, or a recipe with both formats as options. Marker is the direction "
                        "Typical length gives. A pair moves into Format transformations only when it is marked there by hand; "
                        "a pair with Content units contradicts the matrix and is read first.")
    changes = (c["rows"] != rows) + abs(len(c["rows"]) - len(rows))
    c["columns"], c["rows"] = CANDIDATE_COLUMNS, rows
    # what each content unit's format becomes, and the transformation behind each Repurposes into
    tr = {r["Key"]: r for r in ft["rows"]}
    cu = {u["ID"]: u for u in models.sheet(place, "Content Units")["rows"]}
    derived_from = {}
    for u in cu.values():
        if u.get("Derived from"):
            derived_from.setdefault(u["Derived from"], []).append(u["ID"])
    trans, rep = [], []
    for u in models.sheet(place, "Full matrix")["rows"]:
        uid, name, f0 = u["ID"], u.get("Content unit name"), u.get("Format")
        for f, v in tr.get(f0, {}).items():
            if v in ("Down", "Up", "Across"):
                d = [i for i in derived_from.get(uid, []) if fmt.get(i) == f]
                trans.append({"Content unit ID": uid, "Content unit": name, "Format": f0, "Transformation": v, "To format": f,
                              "Derived units": ", ".join(d) or None})
        for f in split(cu[uid].get("Repurposes into")):
            rep.append({"Content unit ID": uid, "Content unit": name, "Format": f0, "Repurposes into": f,
                        "Transformation": "Same format" if f == f0 else tr.get(f0, {}).get(f)})
    changes += _set_rows(doc, "Content unit ↔ Transformation", trans) + _set_rows(doc, "Content unit ↔ Repurposing", rep)
    return doc, changes


# ---------- possibilities (compose) ----------
def derive_possibilities():
    """Possibilities: for each audience at each state where it is present (Audience State Fit), every recipe for that
    audience at that state, and every format, channel and surface that fits it, strongest first. A grade is the weaker of
    the audience's grade at the state and the value's grade there; recipes carry no grade."""
    doc = models.read("recipes")
    sp = {x["name"]: x for x in models.read("space")["sheets"]}
    fm = {x["name"]: {r["Key"]: r for r in x["rows"]} for x in models.read("fit_maps")["sheets"]}
    FSF, CSF, SXS = fm["Format State Fit"], fm["Channel State Fit"], fm["State Surface Fit"]
    AXS, AXC = fm["Audience State Fit"], fm["Audience Channel Fit"]
    RANK = {"Primary": 3, "Secondary": 2, "Fit": 1}
    GRADE = {v: k for k, v in RANK.items()}
    KINDS = ["Recipe", "Format", "Channel", "Surface"]
    recipes = models.recipes(doc)
    rows = []
    for au in sp["Audiences"]["rows"]:
        a = au["Audience"]
        for st in [r["State"] for r in sp["Customer States"]["rows"]]:
            ag = AXS.get(a, {}).get(st)
            if not ag:
                continue
            found = [("Recipe", f'{p["id"]} {p["name"]}', None) for p in recipes
                     if st in p["states"] and a in {x["name"] for x in p["audiences"]}]
            found += [("Format", f, GRADE[min(RANK[FSF[f][st]], RANK[ag])]) for f in FSF if FSF[f].get(st)]
            found += [("Channel", c, GRADE[min(RANK[CSF[c][st]], RANK[ag])]) for c in CSF
                      if CSF[c].get(st) and AXC.get(a, {}).get(c)]
            found += [("Surface", x, GRADE[min(RANK[SXS[x][st]], RANK[ag])]) for x in SXS if SXS[x].get(st)]
            found.sort(key=lambda t: (KINDS.index(t[0]), -RANK.get(t[2], 0)))
            rows += [{"State": st, "Audience": a, "Audience grade": ag, "Kind": k, "Value": v, "Grade": g} for k, v, g in found]
    return doc, _set_rows(doc, "Possibilities", rows)


# ---------- template ----------
TEMPLATE = "knowledge/model/compose/template.json"


def derive_template():
    """Template counts per state: Recipes defined (recipes on the stage sheet), Content units (units at the state)."""
    doc = json.loads((models.ROOT / TEMPLATE).read_text())
    on_sheet = {st["stage"]: len(st["recipes"]) for st in models.read("recipes")["stages"]}
    units = {}
    for r in models.sheet(models.read("place"), "Content Units")["rows"]:
        units[r.get("State")] = units.get(r.get("State"), 0) + 1
    changes = 0
    for r in doc["rows"]:
        new = {"Recipes defined": on_sheet.get(r["State"], 0), "Content units": units.get(r["State"], 0)}
        for c, v in new.items():
            if r.get(c) != v:
                r[c] = v
                changes += 1
    return doc, changes


# ---------- fit maps ----------
def derive_fit_maps():
    """The 4 derived maps, composed from the 7 source maps and the space; units and recipes never feed them."""
    m = load("space", sheets=["Customer States", "Formats", "Channels", "Surfaces", "Audiences"])
    STAGES = [r["State"] for r in m["Customer States"].rows]
    formats = {r["Key"]: r for r in m["Formats"].rows}
    channels = {r["Key"]: r for r in m["Channels"].rows}
    surfaces = {r["Surface"]: r for r in m["Surfaces"].rows}
    stage_rows = {r["State"]: r for r in m["Customer States"].rows}
    audiences = m["Audiences"].rows
    fdoc = models.read("fit_maps")

    def source(name):
        s = models.sheet(fdoc, name)
        lead = [c for c in s["columns"] if c in LEAD]
        return {r["Key"]: {c: r[c] for c in s["columns"] if c and c not in lead and r.get(c)} for r in s["rows"] if r.get("Key")}
    FSF, FOF, CSF, OSF, FXS, CXS, AXS = (source(n) for n in SOURCE_MAPS)
    FORMAT_ROWS, CHANNEL_ROWS, SURFACE_ROWS = list(FSF), list(CSF), list(surfaces)

    RANK = {"Primary": 3, "Secondary": 2, "Fit": 1}
    GRADE = {v: k for k, v in RANK.items()}

    def best(cands):  # strongest of several paths
        return GRADE[max(cands)] if cands else None

    # Format x Channel: a surface both reach, a state both fit, and a delivery under one of the channel's ownership
    # types. Grade = the weaker of: the format's grade on the strongest shared surface (Primary = its Best surface), and the
    # strongest shared state (the weaker of the format's and the channel's grade there).
    FXC = {}
    for f in FORMAT_ROWS:
        fsurf, fst, fown = FXS.get(f, {}), set(FSF.get(f, {})), set(FOF.get(f, {}))
        FXC[f] = {}
        for c in CHANNEL_ROWS:
            shared = set(fsurf) & set(CXS.get(c, {}))
            if not shared or not fst & set(CSF.get(c, {})):
                continue
            if fown and not {channels[c]["Ownership"], channels[c].get("Secondary ownership")} & fown:
                continue
            on_surface = max(RANK[fsurf[x]] for x in shared)
            at_state = max(min(RANK[FSF[f][st]], RANK[CSF[c][st]]) for st in fst & set(CSF[c]))
            FXC[f][c] = GRADE[min(on_surface, at_state)]

    # State x Surface: Primary = Customer States names the surface for the state; Secondary = the state is in the
    # surface's Typical funnel fit; Fit = a channel that is Primary at the state reaches the surface
    FUNNEL = {"Any": STAGES}  # funnel position -> states, from the Funnel column of Customer States
    for st, r in stage_rows.items():
        FUNNEL.setdefault(r["Funnel"], []).append(st)
    named = {st: {x.strip().lower() for x in str(r.get("Surface") or "").split(",")} for st, r in stage_rows.items()}
    SXS = {}
    for s in SURFACE_ROWS:
        typical = set(FUNNEL.get(surfaces[s]["Typical funnel fit"], STAGES))
        via = {x for c in CHANNEL_ROWS if s in CXS.get(c, {}) for x, v in CSF.get(c, {}).items() if v == "Primary"}
        SXS[s] = {}
        for st in STAGES:
            g = [3] * (s.lower() in named[st]) + [2] * (st in typical) + [1] * (st in via)
            if g:
                SXS[s][st] = best(g)

    # Audience x Format, x Channel: fits a state where the audience is present; grade = the weaker of the two cells at the
    # strongest shared state. A channel must also reach the audience group (Channels: Audience groups).
    def reaches(g, c):  # the audience groups a channel reaches: Channels, Audience groups
        return g in split(channels[c].get("Audience groups"))
    AXF, AXC = {}, {}
    for au in audiences:
        a, g, ast = au["Audience"], au["Audience group"], AXS.get(au["Audience"], {})
        AXF[a] = {f: best([min(RANK[FSF[f][st]], RANK[ast[st]]) for st in set(FSF.get(f, {})) & set(ast)]) for f in FORMAT_ROWS}
        AXC[a] = {}
        for c in CHANNEL_ROWS:
            if not reaches(g, c):
                continue
            AXC[a][c] = best([min(RANK[CSF[c][st]], RANK[ast[st]]) for st in set(CSF.get(c, {})) & set(ast)])
        AXF[a] = {k: v for k, v in AXF[a].items() if v}
        AXC[a] = {k: v for k, v in AXC[a].items() if v}

    fmt_lead = lambda f: {"Key": f, "Format": formats[f]["Name"], "Format family": formats[f]["Format family"]}
    au_lead = lambda au: {"Key": au["Audience"], "Audience group": au["Audience group"], "Buying role": au["Buying role"]}
    sheets = {
        "Format Channel Fit": (["Key", "Format", "Format family"], CHANNEL_ROWS, [(fmt_lead(f), FXC[f]) for f in FORMAT_ROWS]),
        "State Surface Fit": (["Key", "Surface family", "Typical funnel fit"], STAGES,
                              [({"Key": s, "Surface family": surfaces[s]["Surface family"], "Typical funnel fit": surfaces[s]["Typical funnel fit"]}, SXS[s]) for s in SURFACE_ROWS]),
        "Audience Format Fit": (["Key", "Audience group", "Buying role"], FORMAT_ROWS, [(au_lead(au), AXF[au["Audience"]]) for au in audiences]),
        "Audience Channel Fit": (["Key", "Audience group", "Buying role"], CHANNEL_ROWS, [(au_lead(au), AXC[au["Audience"]]) for au in audiences]),
    }
    changes = 0
    for name, (lead, labels, data) in sheets.items():
        s = models.sheet(fdoc, name)
        cols = lead + labels
        rows = [{c: ({**l, **cells}).get(c) for c in cols} for l, cells in data]
        if s["columns"] != cols or s["rows"] != rows:
            changes += 1 + sum(1 for a, b in zip(rows, s["rows"]) if a != b) + abs(len(rows) - len(s["rows"]))
        s["columns"], s["rows"] = cols, rows
    return fdoc, changes


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("what", choices=["place", "fit-maps", "recipes", "transformations", "template", "all"])
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    steps = [("place", derive_matrix), ("fit_maps", derive_fit_maps), ("recipes", derive_possibilities),
             ("transformations", derive_candidates),
             ("template", derive_template)]
    FILES = {"template": TEMPLATE}
    for key, fn in steps:
        if a.what not in ("all", key.replace("_", "-")):
            continue
        doc, changes = fn()
        if not a.dry_run:
            if key in FILES:
                (models.ROOT / FILES[key]).write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
            else:
                models.write(key, doc)
        print(f"{key}: {changes} changed {'(dry run, not written)' if a.dry_run else 'and written'}")


if __name__ == "__main__":
    sys.exit(main())
