"""Assignments check: each content unit's Recipe against that recipe.

    python tools/assignments.py
    python tools/assignments.py --json

An assignment holds when the content unit's state is among the recipe's states and the tracks match.
"""
import argparse
import json
import sys
from pathlib import Path


from atlas import load, load_recipes, split


def fit(state, track, recipe):
    """'OK' when the unit's state is among the recipe's states and the tracks match; otherwise what differs."""
    if recipe is None:
        return "Recipe not on any stage sheet"
    if state is None:
        return "Content unit not in the Full matrix"
    in_state = state in split(recipe.get("State"))
    track_ok = recipe.get("Track") in ("Any", track)
    return "OK" if in_state and track_ok else " ".join(
        y for y in ("" if in_state else "State differs", "" if track_ok else "Track differs") if y)


def run():
    recipes = load_recipes()
    out = []
    for u in load("place", sheets=["Full matrix"])["Full matrix"].rows:
        if not u.get("Recipe"):
            continue
        p = recipes.get(u["Recipe"])
        st = u.get("State")
        out.append({"content_unit_id": u["ID"], "recipe": u["Recipe"], "track": u.get("Track"),
                    "content_unit_state": st, "recipe_states": p.get("State") if p else None,
                    "result": fit(st, u.get("Track"), p)})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    rows = run()
    if a.json:
        json.dump(rows, sys.stdout, indent=2, ensure_ascii=False)
        print()
        return
    bad = [r for r in rows if r["result"] != "OK"]
    print(f"Assignments: {len(rows)}  OK {len(rows) - len(bad)}  to check {len(bad)}")
    for r in bad:
        print(f"  {r['content_unit_id']} {r['recipe']}  {r['result']}")


if __name__ == "__main__":
    main()
