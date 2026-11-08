"""Audit layer: inventory of every registry item and the eight audit steps over the Full matrix.

    python tools/audit.py                      audit the Catalog
    python tools/audit.py --product All        every product
    python tools/audit.py --json               the full report as JSON (includes the inventory)

Reads the matrix workbook (resolved by the schema layer) and, for recipes and
the stage sheets and each content unit's Recipe and Track. Steps without data report "Not yet assessable".
"""
import argparse
import json
import sys

from assignments import fit
from atlas import load, load_json, load_recipes as load_stage_recipes, selected, split
from resolve import tables as matrix_tables

CFG = load_json("tools/audit.json")
JOURNEY = ["Awareness", "Consideration", "Decision", "Retention", "Advocacy"]
NOT_YET = "Not yet assessable"


def blank(v):
    return v in (None, "")


# ---------- inventory ----------
def inventory(t, rows):
    m = rows
    states = [r["State"] for r in t["Customer States"].rows if r.get("State")]
    axes = [
        ("Customer States", t["Customer States"], "ID", "State", "Funnel", "State", "State"),
        ("Formats", t["Formats"], "ID", "Key", "Format family", "Format", "Format"),
        ("Channels", t["Channels"], "ID", "Key", "Channel family", "Primary channel", "Primary channel"),
        ("Ownership", t["Ownership"], "ID", "Type", None, "Primary ownership", "Primary ownership"),
        ("Surfaces", t["Surfaces"], "ID", "Surface", "Surface family", "Primary surface", "Primary surface"),
    ]
    out = []
    for axis, reg, idc, keyc, groupc, col, counted in axes:
        for item in reg.rows:
            key = item.get(keyc)
            if blank(key):
                continue
            by = counted
            if axis == "Channels" and key in CFG["entry_source_channels"]:
                needle = CFG["entry_source_channels"][key].lower()
                hits = [r for r in m if needle in str(r.get("Entry source") or "").lower()]
                by = "Entry source"
            else:
                hits = [r for r in m if r.get(col) == key]
            spread = {j: sum(1 for r in hits if r.get("Journey stage") == j) for j in JOURNEY}
            covered = sum(1 for v in spread.values() if v)
            n = len(hits)
            if n == 0:
                status = "Not used"
            elif axis not in ("Customer States", "Ownership") and covered == 1:
                status = "One stage"
            elif axis == "Surfaces" and n >= CFG["heavy_surface"]:
                status = "Heavy"
            else:
                status = "In use"
            row = {"axis": axis, "id": item.get(idc), "item": key, "group": item.get(groupc) if groupc else None,
                   "counted_by": by, "content_units": n, "share": n / len(m) if m else 0, **spread,
                   "stages_covered": covered, "status": status,
                   "content_unit_names": [r.get("Content unit name") for r in hits]}
            if axis == "Customer States":
                row["distinct_formats"] = len({r.get("Format") for r in hits if r.get("Format")})
            out.append(row)
    for row in out:
        if row["axis"] == "Ownership":
            chans = [c for c in t["Channels"].rows if c.get("Ownership") == row["item"]]
            used = {r["item"] for r in out if r["axis"] == "Channels" and r["counted_by"] == "Primary channel" and r["content_units"]}
            row["channels_listed"] = len(chans)
            row["channels_used"] = sum(1 for c in chans if c.get("Key") in used)
    return out


def inv(items, axis, **cond):
    return [r for r in items if r["axis"] == axis and all(r.get(k) == v for k, v in cond.items())]


# ---------- recipes ----------
# ---------- steps ----------
def audit(product="Catalog"):
    t = matrix_tables()
    every = t["Full matrix"].rows
    rows = [r for r in selected(every, product) if not blank(r.get("Product"))]
    items = inventory(t, rows)
    all_ids = [r.get("ID") for r in every]
    report = {"product": product, "content_units": len(rows)}

    mv = CFG["minimum_viable"]
    defined = {"Formats": len(t["Formats"].rows), "Channels": len(t["Channels"].rows),
               "Funnel stages": len(t["Customer States"].rows), "Ownership": 4, "Surfaces": len(t["Surfaces"].rows)}
    in_use = {"Formats": len([r for r in inv(items, "Formats") if r["content_units"]]),
              "Channels": len([r for r in inv(items, "Channels", counted_by="Primary channel") if r["content_units"]]),
              "Funnel stages": len([r for r in inv(items, "Customer States") if r["content_units"]]),
              "Ownership": len([r for r in inv(items, "Ownership") if r["content_units"]]),
              "Surfaces": len([r for r in inv(items, "Surfaces") if r["content_units"]])}
    report["step1_axes"] = [{"axis": a, "defined": defined[a], "in_use": in_use[a], "minimum_viable": mv[a],
                             "status": "Pass" if in_use[a] >= mv[a] else "Below minimum"} for a in mv]

    triples = [(r.get("Content unit name"), r.get("Primary channel"), r.get("Primary surface")) for r in every]
    derived_from = {r.get("Derived from") for r in every if r.get("Derived from")}
    channels = set(t["Channels"].index("Key"))
    surfaces = set(t["Surfaces"].index("Surface"))
    report["step2_integrity"] = {
        "content_units": len(rows),
        "duplicate_ids": sum(1 for r in rows if all_ids.count(r.get("ID")) > 1),
        "duplicate_content_units": sum(1 for r in rows if triples.count((r.get("Content unit name"), r.get("Primary channel"), r.get("Primary surface"))) > 1),
        "spokes_whose_hub_is_missing": sum(1 for r in rows if r.get("Derived from") and r["Derived from"] not in all_ids),
        "repurposing_planned_no_derived_unit": sum(1 for r in rows if r.get("Repurposes into") and r.get("ID") not in derived_from),
        "primary_channel_not_in_channels": sum(1 for r in rows if r.get("Primary channel") not in channels),
        "surface_not_in_surfaces": sum(1 for r in rows if r.get("Primary surface") not in surfaces),
    }

    tagged = [r for r in rows if all(not blank(r.get(c)) for c in CFG["required_tags"])]
    report["step3_tags"] = {"content_units": len(rows), "fully_tagged": len(tagged),
                            "missing_a_required_tag": len(rows) - len(tagged),
                            "missing_ids": [r.get("ID") for r in rows if r not in tagged]}

    fs = inv(items, "Customer States")
    report["step4_format_gaps"] = {
        "formats_defined": defined["Formats"], "formats_in_use": in_use["Formats"],
        "formats_in_one_stage": [r["item"] for r in inv(items, "Formats", status="One stage")],
        "states_with_one_format": [r["item"] for r in fs if r.get("distinct_formats") == 1]}
    used_ch = [r for r in inv(items, "Channels", counted_by="Primary channel") if r["content_units"]]
    report["step4_channel_gaps"] = {
        "channels_defined": defined["Channels"], "channels_in_use": len(used_ch),
        "in_use_missing_from_bofu": [r["item"] for r in used_ch if r["Decision"] == 0],
        "in_use_missing_from_advocacy": [r["item"] for r in used_ch if r["Advocacy"] == 0]}

    stage_rows = []
    counts = {s["item"]: s["content_units"] for s in fs}
    for s in fs:
        st = s["item"]
        stage_rows.append({"state": st, "assets": s["content_units"],
                           "rank_fewest_first": 1 + sum(1 for v in counts.values() if v < s["content_units"]),
                           "distinct_formats": s["distinct_formats"]})
    report["step4_stage_gaps"] = stage_rows

    report["step4_ownership_gaps"] = [
        {"ownership": o, "reading": reading,
         "share_of_content_units": (sum(1 for r in rows if r.get("Primary ownership") == o) / len(rows)) if rows else 0}
        for o, reading in CFG["ownership_reading"].items()]
    report["step4_surface_gaps"] = {
        "surfaces_defined": defined["Surfaces"],
        "surfaces_with_no_content": len(inv(items, "Surfaces", status="Not used")),
        "surfaces_with_too_much": [r["item"] for r in inv(items, "Surfaces", status="Heavy")]}

    def ids(pred):
        return [r.get("ID") for r in rows if pred(r)]
    report["step5_mismatches"] = {
        "bofu_content_on_tofu_surface": ids(lambda r: r.get("Funnel") == "BOFU" and r.get("Typical funnel fit") == "TOFU"),
        "tofu_content_on_bofu_surface": ids(lambda r: r.get("Funnel") == "TOFU" and r.get("Typical funnel fit") == "BOFU"),
        "paid_creative_on_owned_surface": ids(lambda r: r.get("Format family") == "Paid Creative — cross-format" and r.get("Primary ownership") == "Owned"),
        "owned_content_on_earned_channel": ids(lambda r: r.get("Source") == "Brand" and r.get("Primary ownership") == "Earned" and r.get("Ownership subtype") == "Pure earned")}

    ro = CFG["awareness_rule_out"]
    def rule_out(r):
        st = r.get("State")
        a = st == "Unaware" and (r.get("What the person does") in ro["unaware"]["surface_actions"] or
                                 (r.get("Channel family") in ro["unaware"]["owned_channel_families"] and r.get("Primary ownership") == "Owned"))
        b = st in ("Unaware", "Problem-aware") and (r.get("Format name") in ro["unaware_and_problem_aware"]["format_names"] or
                                                  r.get("Primary surface") in ro["unaware_and_problem_aware"]["surfaces"])
        return a or b

    recipes = load_stage_recipes()
    units = [{**r, "Content unit ID": r.get("ID")} for r in every]  # each unit carries its Recipe and Track
    row_ids = {r.get("ID") for r in rows}
    by_id = {r.get("ID"): r for r in every}
    if recipes is None:
        report["recipes_and_tracks"] = NOT_YET
    else:
        sel_units = [u for u in units if u["Content unit ID"] in row_ids]
        used = {}
        for u in sel_units:
            if u.get("Recipe"):
                used[u["Recipe"]] = used.get(u["Recipe"], 0) + 1
        fits = [fit((by_id.get(u["Content unit ID"]) or {}).get("State"), u.get("Track"), recipes.get(u.get("Recipe"))) if u.get("Recipe") else None for u in units]
        report["recipes_and_tracks"] = {
            "recipes_defined": len(recipes),
            "recipes_with_no_content_units": [p for p in recipes if not used.get(p)],
            "content_units_with_a_recipe": sum(1 for u in sel_units if u.get("Recipe")),
            "content_units_without_a_recipe": len(rows) - sum(1 for u in sel_units if u.get("Recipe")),
            "b2c_content_units": sum(1 for u in sel_units if u.get("Track") == "B2C"),
            "b2b_content_units": sum(1 for u in sel_units if u.get("Track") == "B2B"),
            "b2c_recipes_with_no_content_units": [p for p, r in recipes.items() if r.get("Track") == "B2C" and not used.get(p)],
            "recipe_stage_differs": [u["Content unit ID"] for u, f in zip(units, fits) if f and "State differs" in f],
            "track_differs": [u["Content unit ID"] for u, f in zip(units, fits) if f and "Track differs" in f],
            "content_units_per_recipe": used,
        }
    report["recipes_and_tracks_awareness_rule_out"] = ids(rule_out)

    def count(col):
        return sum(1 for r in rows if not blank(r.get(col)))
    report["step6_added_layers"] = {
        "with_amplification_path": count("Amplification"),
        "derived_from_another_unit": count("Derived from")}

    by_metric = []
    for name in CFG["metrics"]:
        by_metric.append({"metric": name, "content_units": sum(1 for r in rows if r.get("Primary metric") == name)})
    report["step7_by_metric"] = by_metric
    report["step7_views"] = CFG["views"]
    report["step8_cadence"] = CFG["cadence"]
    report["inventory"] = items
    return report


def show(rep):
    def short(v):
        if isinstance(v, list):
            return f"{len(v)}" + (f"  ({', '.join(map(str, v[:8]))}{' ...' if len(v) > 8 else ''})" if v else "")
        if isinstance(v, float):
            return f"{v:.2f}"
        return str(v)
    print(f"Audit: {rep['product']}  content units {rep['content_units']}")
    for k, v in rep.items():
        if k in ("product", "content_units", "inventory", "step7_views", "step8_cadence"):
            continue
        print(f"\n{k}")
        if isinstance(v, dict):
            for a, b in v.items():
                print(f"  {a}: {short(b) if not isinstance(b, dict) else b}")
        elif isinstance(v, list) and v and isinstance(v[0], dict):
            for r in v:
                print("  " + "  ".join(f"{a}={short(b)}" for a, b in r.items()))
        else:
            print(f"  {short(v)}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--product", default="Catalog")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    rep = audit(a.product)
    if a.json:
        json.dump(rep, sys.stdout, indent=2, ensure_ascii=False, default=str)
        print()
    else:
        show(rep)


if __name__ == "__main__":
    main()
