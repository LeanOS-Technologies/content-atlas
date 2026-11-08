"""Coherence check: every pair of values in a content unit and in a recipe option, against the fit map that pairs them.

    python tools/coherence.py            summary and every pair the fit maps do not mark
    python tools/coherence.py --json

A content unit has one value per axis. A recipe option has a format, channel, ownership and surface, at each of the
recipe's states. A pair is coherent when its cell in the fit map is marked (Primary, Secondary, Fit or an example).

Coverage reads the other direction: every marked Audience State Fit cell is served by at least one recipe whose states
and audiences include it. Exit 1 on any pair not marked or any cell not covered.
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path


import models

# (pair, fit map, field giving the row key, field giving the column key); fields name a unit column or a recipe-option field
# Ownership is not chosen: it is the channel's (Channels: Ownership, Secondary ownership). It is checked only against the
# channel; format × ownership already acts inside Format Channel Fit, and Ownership State Fit holds tactics, not a test.
PAIRS = [("Format × State", "Format State Fit", "format", "stage"),
         ("Format × Channel", "Format Channel Fit", "format", "channel"),
         ("Format × Surface", "Format Surface Fit", "format", "surface"),
         ("Channel × State", "Channel State Fit", "channel", "stage"),
         ("Channel × Ownership", "Channels registry", "channel", "ownership"),
         ("Channel × Surface", "Channel Surface Fit", "channel", "surface"),
         ("State × Surface", "State Surface Fit", "surface", "stage"),
         ("Audience × State", "Audience State Fit", "audience", "stage"),
         ("Audience × Format", "Audience Format Fit", "audience", "format"),
         ("Audience × Channel", "Audience Channel Fit", "audience", "channel")]
UNIT = {"format": "Format", "channel": "Primary channel", "surface": "Primary surface", "ownership": "Primary ownership", "stage": "State"}


def fit_maps():
    """The fit maps, plus the Channels registry read as channel × ownership (Ownership = Primary, Secondary ownership = Secondary)."""
    out = {s["name"]: {r["Key"]: r for r in s["rows"]} for s in models.read("fit_maps")["sheets"]}
    ch = models.sheet(models.read("space"), "Channels")["rows"]
    out["Channels registry"] = {r["Key"]: {r["Ownership"]: "Primary", **({r["Secondary ownership"]: "Secondary"} if r.get("Secondary ownership") else {})} for r in ch}
    return out


def subjects():
    """Every content unit and every recipe option at each of its states, as {field: [values]}."""
    out = []
    for u in models.sheet(models.read("place"), "Full matrix")["rows"]:
        v = {k: [u.get(c)] if u.get(c) else [] for k, c in UNIT.items()}
        v["audience"] = [x.strip() for x in str(u.get("Audience") or "").split(",") if x.strip()]
        out.append(("Content unit", u["ID"], u.get("Content unit name"), v))
    owner = models.recipe_context()[1]
    for p in models.recipes():
        for o in p["kit"]:
            v = {"format": [o["format"]["key"]] if o.get("format") else [], "channel": [o["channel"]["key"]] if o.get("channel") else [],
                 "surface": [o["surface"]["key"]] if o.get("surface") else [],
                 "ownership": [owner[o["channel"]["key"]]] if o.get("channel") else [],
                 "stage": list(p["states"]), "audience": [a["name"] for a in p["audiences"]]}
            out.append(("Recipe option", f"{p['id']} {o['option']}", p["name"], v))
    return out


def run():
    fm, rows = fit_maps(), []
    for kind, sid, name, v in subjects():
        for pair, mp, a, b in PAIRS:
            for x in v[a]:
                for y in v[b]:
                    rows.append({"subject": kind, "id": sid, "name": name, "pair": pair, "row": x, "column": y,
                                 "fit_map": mp, "cell": fm[mp].get(x, {}).get(y)})
    return rows


def coverage():
    """Every marked Audience State Fit cell, with the recipes serving that audience at that state."""
    s = models.sheet(models.read("fit_maps"), "Audience State Fit")
    R = models.recipes()
    return [{"audience": r["Key"], "state": st, "grade": r[st],
             "recipes": [p["id"] for p in R if st in p["states"] and r["Key"] in {a["name"] for a in p["audiences"]}]}
            for r in s["rows"] for st in s["columns"][3:] if r.get(st)]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    rows, cover = run(), coverage()
    uncovered = [c for c in cover if not c["recipes"]]
    if a.json:
        json.dump({"pairs": rows, "coverage": cover}, sys.stdout, indent=2, ensure_ascii=False)
        print()
        return 1 if uncovered or any(not r["cell"] for r in rows) else 0
    for kind in ("Content unit", "Recipe option"):
        mine = [r for r in rows if r["subject"] == kind]
        bad = [r for r in mine if not r["cell"]]
        print(f"{kind}s: {len({r['id'] for r in mine})}  pairs {len(mine)}  not marked {len(bad)}  "
              f"({', '.join(f'{p} {n}' for p, n in Counter(r['pair'] for r in bad).most_common())})")
        for r in bad:
            print(f"  {r['id']}  {r['pair']}: {r['row']} × {r['column']}")
    print(f"Audience State Fit cells: {len(cover)}  covered by a recipe {len(cover) - len(uncovered)}  not covered {len(uncovered)}")
    for c in uncovered:
        print(f"  {c['audience']} × {c['state']} ({c['grade']}): no recipe")
    return 1 if uncovered or any(not r["cell"] for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
