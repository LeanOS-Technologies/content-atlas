"""Possibilities: the program side of the worker's skills (contracts/inputs.md, contracts/outputs.md).

    python tools/possibilities.py resolve REQUEST.json   steps and links reachable from the request's anchors
    python tools/possibilities.py map REQUEST.json       existing pieces placed and checked, then steps and links from them
    python tools/possibilities.py check DIR              check DIR/routes.json (composed routes) and add them to DIR's result
    python tools/possibilities.py filter DIR PARAMS.json narrow DIR's result by params into a new artifact
    python tools/possibilities.py export-xlsx DIR        render a finished result's workbook without recomputing it

Each writes artifacts/<name>/ (or --out): possibilities.json, possibilities.xlsx, summary.md, and keeps the request.
Use --no-xlsx for intermediate operations: JSON and summary are written, and any previous workbook is removed.
export-xlsx writes only the workbook and summary from the saved JSON. The default output is unchanged.
Nothing is ranked. resolve and map never cut by channel, ownership, format, track or grade; only filter does.
"""
import argparse
import json
import shutil
import sys
from collections import deque
from pathlib import Path

import models
from atlas import ROOT, split

RANK = {"Primary": 3, "Secondary": 2, "Fit": 1}
GRADE = {v: k for k, v in RANK.items()}
MAX_HOPS = 3  # a route has at most 4 steps
MAP_AXES = {"Format State Fit": ("Formats", "Customer States"), "Format Ownership Fit": ("Formats", "Ownership"),
            "Channel State Fit": ("Channels", "Customer States"), "Ownership State Fit": ("Ownership", "Customer States"),
            "Format Channel Fit": ("Formats", "Channels"), "Format Surface Fit": ("Formats", "Surfaces"),
            "Channel Surface Fit": ("Channels", "Surfaces"), "State Surface Fit": ("Surfaces", "Customer States"),
            "Audience State Fit": ("Audiences", "Customer States"), "Audience Format Fit": ("Audiences", "Formats"),
            "Audience Channel Fit": ("Audiences", "Channels")}
KEY = {"Customer States": "State", "Audiences": "Audience", "Formats": "Key", "Channels": "Key", "Ownership": "Type",
       "Surfaces": "Surface", "Metrics": "Metric name"}
AXIS = {"Customer States": "states", "Audiences": "audiences", "Formats": "formats", "Channels": "channels",
        "Ownership": "ownership", "Surfaces": "surfaces"}
STEP_COLS = ["Step ID", "Depth", "Kind", "Source", "Name", "State", "Format", "Channel", "Ownership", "Surface", "Audiences",
             "Track", "State grade", "Time to first result"]
LINK_COLS = ["From", "To", "Link", "Detail"]
ROUTE_COLS = ["Route ID", "Route", "Step", "Step ID", "State", "Format", "Channel", "Surface", "Link to next", "Check", "Why"]


# ---------- the model ----------
class Atlas:
    def __init__(self):
        self.space = {s["name"]: s for s in models.read("space")["sheets"]}
        self.fm = {s["name"]: s for s in models.read("fit_maps")["sheets"]}
        self.map = {n: {r["Key"]: r for r in s["rows"]} for n, s in self.fm.items()}
        self.keys = {n: [r[KEY[n]] for r in self.space[n]["rows"]] for n in KEY}
        self.channel = {r["Key"]: r for r in self.space["Channels"]["rows"]}
        self.states = self.keys["Customer States"]
        nxt = {r["State"]: r["Intended progression"] for r in self.space["Customer States"]["rows"]}
        self.next = {s: [x for x in self.states if x in str(v)] or (["Unaware"] if "Awareness" in str(v) else [])
                     for s, v in nxt.items()}
        self.rdoc = models.read("recipes")
        self.recipes = models.recipes(self.rdoc)
        self.place = models.read("place")
        self.units = models.sheet(self.place, "Full matrix")["rows"]
        self.tdoc = models.read("transformations")
        self.trans = {r["Key"]: r for r in models.sheet(self.tdoc, "Format transformations")["rows"]}
        self.cand = {(r["Source format"], r["Target format"]): r["Marker"] for r in models.sheet(self.tdoc, "Candidates")["rows"]}

    def grade(self, m, row, col):
        v = self.map[m].get(row, {}).get(col)
        return v if v in RANK else None

    def pairs(self, st, f, c, s, audiences):
        """Every fit-map pair of one construction: (pair, grade or None)."""
        out = [("Format × State", self.grade("Format State Fit", f, st)), ("Channel × State", self.grade("Channel State Fit", c, st)),
               ("State × Surface", self.grade("State Surface Fit", s, st)), ("Format × Channel", self.grade("Format Channel Fit", f, c)),
               ("Format × Surface", self.grade("Format Surface Fit", f, s)), ("Channel × Surface", self.grade("Channel Surface Fit", c, s))]
        for a in audiences:
            out += [(f"Audience × State ({a})", self.grade("Audience State Fit", a, st)),
                    (f"Audience × Format ({a})", self.grade("Audience Format Fit", a, f)),
                    (f"Audience × Channel ({a})", self.grade("Audience Channel Fit", a, c))]
        return out

    def weakest(self, st, f, c, s):
        """State grade: the weakest of the format's, the channel's and the surface's grade at the state."""
        g = [self.grade("Format State Fit", f, st), self.grade("Channel State Fit", c, st), self.grade("State Surface Fit", s, st)]
        return GRADE[min(RANK[x] for x in g)] if all(g) else None

    def link(self, f1, f2):
        if f1 == f2:
            return None
        v = self.trans.get(f1, {}).get(f2)
        if v in ("Down", "Up", "Across"):
            return f"Transformation: {v}"
        if (f1, f2) in self.cand:
            return f"Candidate: {self.cand[(f1, f2)]}"
        return None


# ---------- steps: every construction the atlas holds ----------
def atlas_steps(A):
    steps = []
    for p in A.recipes:
        for o in p["kit"]:
            f, c, s = o["format"]["key"], o["channel"]["key"], (o.get("surface") or {}).get("key")
            for st in p["states"]:
                steps.append({"Kind": "Recipe option", "Source": f"{p['id']} {o['option']}", "Name": p["name"], "State": st,
                              "Format": f, "Channel": c, "Ownership": A.channel[c]["Ownership"], "Surface": s,
                              "Audiences": [a["name"] for a in p["audiences"]], "Track": p["track"],
                              "State grade": A.weakest(st, f, c, s), "Time to first result": p["time_to_first_result"]})
    for u in A.units:
        f, c, s = u.get("Format"), u.get("Primary channel"), u.get("Primary surface")
        steps.append({"Kind": "Content unit", "Source": u["ID"], "Name": u.get("Content unit name"), "State": u.get("State"),
                      "Format": f, "Channel": c, "Ownership": A.channel.get(c, {}).get("Ownership"), "Surface": s,
                      "Audiences": split(u.get("Audience")), "Track": u.get("Track"),
                      "State grade": A.weakest(u.get("State"), f, c, s), "Time to first result": None})
    return steps


def graph(A, anchors, steps):
    """Breadth-first from the anchors: progression to the state's Intended progression, transformation (or candidate) to
    another format, sharing at least one audience. At most MAX_HOPS links from an anchor; a state appears once per path."""
    by_state = {}
    for i, s in enumerate(steps):
        by_state.setdefault(s["State"], []).append(i)
    by_format = {}
    for i, s in enumerate(steps):
        by_format.setdefault(s["Format"], []).append(i)
    depth = {i: 0 for i in anchors}
    links, seen = [], set()
    q = deque(anchors)
    while q:
        i = q.popleft()
        if depth[i] >= MAX_HOPS:
            continue
        a = steps[i]
        aud = set(a["Audiences"])
        targets = [(j, "Progression", f"{a['State']} → {steps[j]['State']}") for nst in A.next.get(a["State"], [])
                   for j in by_state.get(nst, [])]
        for f2 in set(A.trans.get(a["Format"], {})) | {t for (s1, t) in A.cand if s1 == a["Format"]}:
            kind = A.link(a["Format"], f2)
            if kind:
                targets += [(j, kind, f"{a['Format']} → {f2}") for j in by_format.get(f2, []) if steps[j]["State"] != a["State"]]
        for j, kind, detail in targets:
            b = steps[j]
            if aud and b["Audiences"] and not aud & set(b["Audiences"]):
                continue
            if (i, j) not in seen:
                seen.add((i, j))
                links.append((i, j, kind, detail))
            if j not in depth:
                depth[j] = depth[i] + 1
                q.append(j)
    return depth, links


# ---------- the result document ----------
def _sheet(name, rows, columns, description=None, **extra):
    return {"name": name, "title": name, "description": description, "header_row": extra.pop("header_row", 3),
            "columns": columns, "rows": rows, **extra}


def _row(s, sid, d):
    return {**{c: s.get(c) for c in STEP_COLS}, "Step ID": sid, "Depth": d, "Audiences": ", ".join(s["Audiences"]) or None}


def build(A, request, steps, depth, links, extra_sheets=()):
    order = sorted(depth, key=lambda i: (depth[i], A.states.index(steps[i]["State"]) if steps[i]["State"] in A.states else 99, i))
    sid = {i: f"S-{n:04d}" for n, i in enumerate(order, 1)}
    step_rows = [_row(steps[i], sid[i], depth[i]) for i in order]
    link_rows = [{"From": sid[i], "To": sid[j], "Link": k, "Detail": d} for i, j, k, d in links if i in sid and j in sid]
    return assemble(A, request, step_rows, link_rows, [], list(extra_sheets))


def assemble(A, request, step_rows, link_rows, route_rows, extra):
    """Every sheet of a result from its steps: the atlas rows those steps use, unchanged."""
    used = {"states": {r["State"] for r in step_rows}, "formats": {r["Format"] for r in step_rows},
            "channels": {r["Channel"] for r in step_rows}, "surfaces": {r["Surface"] for r in step_rows if r["Surface"]},
            "ownership": {r["Ownership"] for r in step_rows if r["Ownership"]},
            "audiences": {a for r in step_rows for a in split(r["Audiences"])}}
    rids = {r["Source"].split(" ")[0] for r in step_rows if r["Kind"] == "Recipe option"}
    uids = {r["Source"] for r in step_rows if r["Kind"] == "Content unit"}
    recipes = [p for p in A.recipes if p["id"] in rids]
    metrics = {m["name"] for p in recipes for m in p["metrics"]["direct"] + p["metrics"]["downstream"]}
    units = [u for u in A.units if u["ID"] in uids]
    metrics |= {u.get(c) for u in units for c in ("Primary metric", "Secondary metric") if u.get(c)}
    used["metrics"] = metrics
    out = [_sheet("Steps", step_rows, STEP_COLS, "Every construction reachable from the anchors: recipe options, content units "
                  "and existing pieces, with the depth (links from the nearest anchor) and its state grade: the weakest of the format's, channel's and surface's grade at the state."),
           _sheet("Links", link_rows, LINK_COLS, "How one step leads to another: Progression (the state's Intended progression), "
                  "Transformation (Format transformations) or Candidate (Candidates), sharing at least one audience."),
           _sheet("Routes", route_rows, ROUTE_COLS, "Routes composed over the steps, each checked step by step and link by link.")]
    out += list(extra)
    for name, field in [("Customer States", "states"), ("Audiences", "audiences"), ("Formats", "formats"), ("Channels", "channels"),
                        ("Ownership", "ownership"), ("Surfaces", "surfaces"), ("Metrics", "metrics")]:
        s = A.space[name]
        out.append(_sheet(name, [r for r in s["rows"] if r.get(KEY[name]) in used[field]], s["columns"], s.get("description"),
                          header_row=s["header_row"]))
    for name, (ra, ca) in MAP_AXES.items():
        m = A.fm[name]
        keep_r, keep_c = used[AXIS[ra]], used[AXIS[ca]]
        regc = set(A.keys[ca])
        cols = [c for c in m["columns"] if c and c not in regc] + [c for c in m["columns"] if c in keep_c]
        out.append(_sheet(name, [{c: r.get(c) for c in cols} for r in m["rows"] if r["Key"] in keep_r], cols, m.get("description")))
    out.append(_sheet("Recipes", [models.recipe_row(p) for p in recipes], A.rdoc["stage_columns"], "The recipes the steps come from."))
    poss = models.sheet(A.rdoc, "Possibilities")
    out.append(_sheet("Possibilities", [r for r in poss["rows"] if r["State"] in used["states"] and r["Audience"] in used["audiences"]],
                      poss["columns"], poss["description"]))
    full = models.sheet(A.place, "Full matrix")
    out.append(_sheet("Content units", units, full["columns"], None, header_row=full["header_row"], column_groups=full["column_groups"]))
    for name in ("Content unit ↔ Transformation", "Content unit ↔ Repurposing"):
        s = models.sheet(A.tdoc, name)
        out.append(_sheet(name, [r for r in s["rows"] if r["Content unit ID"] in uids], s["columns"], s["description"]))
    s = models.sheet(A.tdoc, "Candidates")
    out.append(_sheet("Candidates", [r for r in s["rows"] if r["Source format"] in used["formats"]], s["columns"], s["description"]))
    return {"name": request.get("name") or "atlas", "request": request, "sheets": out}


def sheet(doc, name):
    return next(s for s in doc["sheets"] if s["name"] == name)


# ---------- skills' program operations ----------
def anchors_for(A, steps, anchor):
    S = set(anchor.get("states") or A.states)
    Au = set(anchor.get("audiences") or A.keys["Audiences"])
    return [i for i, s in enumerate(steps) if s["State"] in S and (not s["Audiences"] or set(s["Audiences"]) & Au)]


def request_check(A, request, fields):
    rows = []
    for field, reg in fields.items():
        for v in request.get(field) or []:
            if v not in A.keys[reg]:
                rows.append({"Field": field, "Value": v, "Registry": f"{reg} → {KEY[reg]}"})
    return rows


def resolve(request):
    A = Atlas()
    anchor = request.get("anchors") or {}
    bad = request_check(A, anchor, {"states": "Customer States", "audiences": "Audiences"})
    anchor = {k: [v for v in anchor.get(k) or [] if v not in {b["Value"] for b in bad}] for k in ("states", "audiences")}
    steps = atlas_steps(A)
    depth, links = graph(A, anchors_for(A, steps, anchor), steps)
    return build(A, request, steps, depth, links, [_sheet("Request check", bad, ["Field", "Value", "Registry"],
                                                          "Anchor values not found in their registry; each is left out."),
                                                   anchor_check(A, steps, anchor)])


def anchor_check(A, steps, anchor):
    """Each anchor audience at each anchor state: its Audience State Fit grade and the steps addressed to it there."""
    rows = []
    for au in anchor.get("audiences") or []:
        for st in anchor.get("states") or A.states:
            n = sum(1 for s in steps if s["State"] == st and au in s["Audiences"])
            g = A.grade("Audience State Fit", au, st)
            rows.append({"Audience": au, "State": st, "Audience grade": g, "Steps": n,
                         "Finding": None if g and n else "not present (Audience State Fit)" if not g else "present, no step"})
    return _sheet("Anchor check", rows, ["Audience", "State", "Audience grade", "Steps", "Finding"],
                  "Each anchor audience at each anchor state: its Audience State Fit grade and the steps addressed to it there. "
                  "Not present: the atlas holds no content for that audience as reader at that state. Present, no step: model gap.")


def place_pieces(A, pieces):
    """Existing pieces as steps, each checked: every value an atlas value, every pair marked in the fit maps."""
    steps, rows = [], []
    for p in pieces:
        st, f, c, s, aud = p.get("state"), p.get("format"), p.get("channel"), p.get("surface"), p.get("audiences") or []
        findings = [f"{lab}: {v} is not an atlas value" for lab, v, reg in
                    [("state", st, "Customer States"), ("format", f, "Formats"), ("channel", c, "Channels"),
                     ("surface", s, "Surfaces")] + [("audience", a, "Audiences") for a in aud] if v not in A.keys[reg]]
        if not findings:
            findings = [f"{pair} not marked" for pair, g in A.pairs(st, f, c, s, aud) if not g]
        rows.append({"Piece ID": p["id"], "Piece": p.get("name"), "Where": p.get("where"), "State": st, "Format": f, "Channel": c,
                     "Surface": s, "Audiences": ", ".join(aud) or None, "Placement basis": p.get("basis"),
                     "Check": "; ".join(findings) or "OK"})
        steps.append({"Kind": "Existing piece", "Source": p["id"], "Name": p.get("name"), "State": st, "Format": f, "Channel": c,
                      "Ownership": A.channel.get(c, {}).get("Ownership"), "Surface": s, "Audiences": aud, "Track": p.get("track"),
                      "State grade": A.weakest(st, f, c, s) if st in A.states else None, "Time to first result": None})
    return steps, rows


def map_existing(request):
    A = Atlas()
    pieces = request.get("pieces") or []
    psteps, placement = place_pieces(A, pieces)
    ok = [i for i, r in enumerate(placement) if not r["Check"].startswith(("state:", "format:", "channel:", "surface:", "audience:"))]
    steps = psteps + atlas_steps(A)
    depth, links = graph(A, ok, steps)
    cover = []
    have = {(r["State"], a) for r in placement for a in split(r["Audiences"])}
    for au in A.keys["Audiences"]:
        for st in A.states:
            g = A.grade("Audience State Fit", au, st)
            if g:
                cover.append({"State": st, "Audience": au, "Audience grade": g,
                              "Existing pieces": ", ".join(r["Piece ID"] for r in placement if r["State"] == st and au in split(r["Audiences"])) or None})
    extra = [_sheet("Placement", placement, ["Piece ID", "Piece", "Where", "State", "Format", "Channel", "Surface", "Audiences",
                                             "Placement basis", "Check"],
                    "Each existing piece placed on the atlas: values and the check of every pair against the fit maps."),
             _sheet("Coverage", cover, ["State", "Audience", "Audience grade", "Existing pieces"],
                    "Every audience at every state where it is present (Audience State Fit), with the existing pieces there; blank = nothing yet.")]
    return build(A, request, steps, depth, links, extra)


def check_routes(doc, routes):
    """Composed routes: each step a Step ID of the result or a construction; each step's pairs against the fit maps;
    each link a Progression or a marked transformation (or candidate)."""
    A = Atlas()
    by_id = {r["Step ID"]: r for r in sheet(doc, "Steps")["rows"]}
    rows, ok_all = [], True
    for n, route in enumerate(routes, 1):
        rid = route.get("id") or f"R-{n:03d}"
        resolved = []
        for s in route["steps"]:
            r = by_id.get(s) if isinstance(s, str) else {"Step ID": None, "State": s.get("state"), "Format": s.get("format"),
                                                         "Channel": s.get("channel"), "Surface": s.get("surface"),
                                                         "Audiences": ", ".join(s.get("audiences") or [])}
            resolved.append(r)
        for k, r in enumerate(resolved):
            if r is None:
                rows.append({"Route ID": rid, "Route": route.get("name"), "Step": k + 1, "Check": "unknown Step ID"})
                ok_all = False
                continue
            findings = [f"{p} not marked" for p, g in A.pairs(r["State"], r["Format"], r["Channel"], r["Surface"], split(r["Audiences"])) if not g]
            nxt = resolved[k + 1] if k + 1 < len(resolved) else None
            link = None
            if nxt:
                if nxt["State"] in A.next.get(r["State"], []):
                    link = f"Progression: {r['State']} → {nxt['State']}"
                elif A.link(r["Format"], nxt["Format"]):
                    link = f"{A.link(r['Format'], nxt['Format'])}: {r['Format']} → {nxt['Format']}"
                else:
                    findings.append(f"no link to step {k + 2}: not the next state, no transformation {r['Format']} → {nxt['Format']}")
            ok_all &= not findings
            rows.append({"Route ID": rid, "Route": route.get("name"), "Step": k + 1, "Step ID": r["Step ID"], "State": r["State"],
                         "Format": r["Format"], "Channel": r["Channel"], "Surface": r["Surface"], "Link to next": link,
                         "Check": "; ".join(findings) or "OK", "Why": route.get("why") if k == 0 else None})
    return rows, ok_all


def filter_doc(doc, params, composed=None):
    """Narrow a result by params; nothing is recomputed. A route stays only when every step stays;
    a construction step is judged by its own values and state grade. Returns the narrowed result and the kept routes."""
    A = Atlas()
    p = {k: set(v) for k, v in params.items() if isinstance(v, list) and v}
    min_grade = RANK.get(params.get("min_grade"), 0)
    track = params.get("track")

    def keep(r):
        return ((not p.get("states") or r["State"] in p["states"]) and (not p.get("channels") or r["Channel"] in p["channels"])
                and (not p.get("ownership") or r["Ownership"] in p["ownership"]) and (not p.get("formats") or r["Format"] in p["formats"])
                and (not p.get("audiences") or set(split(r["Audiences"])) & p["audiences"])
                and (not track or r["Track"] in ("Any", track, None))
                and (not min_grade or RANK.get(r["State grade"], 0) >= min_grade)
                and (not p.get("time_to_first_result") or r["Time to first result"] in p["time_to_first_result"] or r["Kind"] != "Recipe option"))
    steps = [r for r in sheet(doc, "Steps")["rows"] if keep(r)]
    ids = {r["Step ID"] for r in steps}
    links = [r for r in sheet(doc, "Links")["rows"] if r["From"] in ids and r["To"] in ids]
    def kept(s):
        if isinstance(s, str):
            return s in ids
        c = s.get("channel") or ""
        return keep({"State": s.get("state"), "Format": s.get("format"), "Channel": c, "Ownership": c.split(":")[0],
                     "Surface": s.get("surface"), "Audiences": ", ".join(s.get("audiences") or []), "Track": None,
                     "State grade": A.weakest(s.get("state"), s.get("format"), c, s.get("surface")),
                     "Kind": "Construction", "Time to first result": None})
    composed = [r for r in composed or [] if all(kept(s) for s in r["steps"])]
    extra = [s for s in doc["sheets"] if s["name"] in ("Placement", "Coverage", "Request check")]
    bad = request_check(A, params, {"states": "Customer States", "audiences": "Audiences", "channels": "Channels",
                                    "ownership": "Ownership", "formats": "Formats"})
    extra = [s for s in extra if s["name"] != "Request check"] + [_sheet("Request check", bad, ["Field", "Value", "Registry"],
                                                                      "Filter values not found in their registry; each is ignored.")]
    out = assemble(A, {**doc["request"], "filter": params}, steps, links, [], extra)
    sheet(out, "Routes")["rows"] = check_routes(out, composed)[0]
    used = {k: {r[k] for r in steps} for k in ("Format", "Channel", "Surface")}
    rids = {r["Source"].split(" ")[0] for r in steps if r["Kind"] == "Recipe option"}
    poss = sheet(out, "Possibilities")
    poss["rows"] = [r for r in poss["rows"] if (r["Value"].split(" ")[0] in rids if r["Kind"] == "Recipe" else r["Value"] in used[r["Kind"]])
                    and (r["Kind"] == "Recipe" or RANK.get(r["Grade"], 0) >= min_grade)]
    out["name"] = params.get("name") or f"{doc['name']}-filtered"
    return out, composed


# ---------- files ----------
def styles():
    import render

    S = render.STYLES
    return {**S["space"], **S["fit_maps"], **S["transformations"], "Recipes": S["recipes"]["Unaware"],
            "Possibilities": S["recipes"]["Possibilities"], "Content units": S["place"]["Full matrix"],
            "Steps": {"tab": "FF0F766E", "by": "State", "colors_from": "stage_funnel", "columns": ["State"], "bold": ["Name"],
                      "freeze": "C4", "grade_column": "State grade"},
            "Links": {"tab": "FF0F766E", "freeze": "C4"}, "Routes": {"tab": "FF0F766E", "by": "Route ID", "bold": ["Route"], "freeze": "D4"},
            "Placement": {"tab": "FFB45309", "bold": ["Piece"], "freeze": "C4"},
            "Coverage": {"tab": "FFB45309", "by": "State", "colors_from": "stage_funnel", "columns": ["State"], "freeze": "C4",
                         "grade_column": "Audience grade"},
            "Request check": {"tab": "FFB91C1C", "freeze": "A4"}}


def summary(doc, *, xlsx=True):
    req = {k: v for k, v in doc["request"].items() if v and k not in ("pieces",)}
    n = {s["name"]: len(s["rows"]) for s in doc["sheets"]}
    data = ("possibilities.xlsx (one tab per sheet, for reading) and "
            "possibilities.json (the same sheets under `sheets`, for further processing)." if xlsx else
            "possibilities.json (every sheet under `sheets`, for further processing). "
            "Render a workbook when needed with `python tools/possibilities.py export-xlsx <result-folder>`.")
    out = [f"# {doc['name']}", "", "Possibilities for this request. Data: " + data, "", "## Request", ""]
    out += [f"- {k}: {json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v}" for k, v in req.items()]
    if doc["request"].get("pieces"):
        out.append(f"- pieces: {len(doc['request']['pieces'])} existing pieces")
    out += ["", "## Sheets", "", "| Sheet | Rows |", "|---|---|"] + [f"| {s['name']} | {n[s['name']]} |" for s in doc["sheets"]]
    routes = sheet(doc, "Routes")["rows"]
    if routes:
        bad = {r["Route ID"] for r in routes if r["Check"] != "OK"}
        out += ["", f"Routes: {len({r['Route ID'] for r in routes})} composed, {len(bad)} with findings."]
    for name in ("Placement", "Request check"):
        if name in n:
            rows = sheet(doc, name)["rows"]
            out += ["", f"## {name}", ""]
            if name == "Placement":
                out += [f"- {r['Piece ID']} {r['Piece']}: {r['Check']}" for r in rows]
            else:
                out += [f"- {r['Field']}: {r['Value']} is not in {r['Registry']}" for r in rows] or ["- every value is an atlas value"]
    return "\n".join(out) + "\n"


def write_xlsx(doc, out_dir):
    """Render the saved sheets; enumeration, route checks and model data are untouched."""
    import openpyxl
    import render

    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    for s in doc["sheets"]:
        ws = wb.create_sheet(s["name"][:31])
        for (r, j), v in models.sheet_grid(s).items():
            ws.cell(r, j, v)
    render.STYLES["result"] = styles()
    render.style(wb, doc, "result")
    wb.save(out_dir / "possibilities.xlsx")


def write(doc, out_dir, request_file=None, *, xlsx=True):
    out_dir.mkdir(parents=True, exist_ok=True)
    if request_file and Path(request_file).resolve() != (out_dir / "request.json").resolve():
        shutil.copy(request_file, out_dir / "request.json")
    (out_dir / "possibilities.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    if xlsx:
        write_xlsx(doc, out_dir)
    else:
        (out_dir / "possibilities.xlsx").unlink(missing_ok=True)
    (out_dir / "summary.md").write_text(summary(doc, xlsx=xlsx))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("op", choices=["resolve", "map", "check", "filter", "export-xlsx"])
    ap.add_argument("target")
    ap.add_argument("params", nargs="?")
    ap.add_argument("--out")
    ap.add_argument("--no-xlsx", action="store_true", help="write JSON and summary only; remove any previous workbook")
    a = ap.parse_args(argv)
    if a.op == "export-xlsx" and (a.no_xlsx or a.out):
        ap.error("export-xlsx writes into its result folder; --no-xlsx and --out do not apply")
    if a.op in ("resolve", "map"):
        request = json.loads(Path(a.target).read_text())
        doc = resolve(request) if a.op == "resolve" else map_existing(request)
        out = Path(a.out) if a.out else ROOT / "artifacts" / doc["name"]
        write(doc, out, a.target, xlsx=not a.no_xlsx)
    elif a.op == "check":
        out = Path(a.target)
        doc = json.loads((out / "possibilities.json").read_text())
        rows, ok = check_routes(doc, json.loads((out / "routes.json").read_text()))
        sheet(doc, "Routes")["rows"] = rows
        write(doc, out, xlsx=not a.no_xlsx)
        print(f"routes: {len({r['Route ID'] for r in rows})}, {'all OK' if ok else 'with findings'}")
        return 0 if ok else 1
    elif a.op == "export-xlsx":
        out = Path(a.target)
        doc = json.loads((out / "possibilities.json").read_text())
        write_xlsx(doc, out)
        (out / "summary.md").write_text(summary(doc))
    else:
        src = Path(a.target)
        params = json.loads(Path(a.params).read_text())
        composed = json.loads((src / "routes.json").read_text()) if (src / "routes.json").exists() else []
        doc, composed = filter_doc(json.loads((src / "possibilities.json").read_text()), params, composed)
        out = Path(a.out) if a.out else src.parent / doc["name"]
        write(doc, out, xlsx=not a.no_xlsx)
        shutil.copy(a.params, out / "filter.json")
        (out / "routes.json").write_text(json.dumps(composed, indent=2, ensure_ascii=False) + "\n")
    n = {s["name"]: len(s["rows"]) for s in doc["sheets"]}
    print(f"{doc['name']}: steps {n['Steps']}, links {n['Links']}, routes {len({r['Route ID'] for r in sheet(doc, 'Routes')['rows']})} → {out}")


if __name__ == "__main__":
    sys.exit(main())
