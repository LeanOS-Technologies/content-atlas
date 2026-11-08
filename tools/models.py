"""The models as JSON, and their spreadsheet layout.

space, content units, fit maps and transformations hold sheets; compose/recipes.json holds recipes grouped by stage.
`grid_*` turns a model into {sheet: {(row, column): value}}: the exact cells its xlsx shows.
render.py writes those cells; check.py compares them with the xlsx. Both use the same layout, so a passing
check means the xlsx and the JSON hold the same values.
"""
import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODELS = {"space": "knowledge/model/enumerate/space.json", "place": "knowledge/model/place/content-units.json",
          "fit_maps": "knowledge/model/combine/fit-maps.json", "recipes": "knowledge/model/compose/recipes.json",
          "transformations": "knowledge/model/amplify/transformations.json"}
OUTPUTS = {key: path.replace(".json", ".xlsx") for key, path in MODELS.items()}


def read(key):
    return json.loads((ROOT / MODELS[key]).read_text())


def write(key, doc):
    (ROOT / MODELS[key]).write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")


def sheet(doc, name):
    return next(s for s in doc["sheets"] if s["name"] == name)


# ---------- sheet models ----------
def sheet_grid(s):
    """Cells of one sheet: preface rows, header, rows, sections below the table."""
    g = {}
    if "column_groups" in s:  # Full matrix: group labels on row 1 above the first column of each group
        pos = {c: j for j, c in enumerate(s["columns"], 1) if c is not None}
        for group, cols in s["column_groups"].items():
            g[(1, pos[cols[0]])] = group
    else:
        for i, key in enumerate(("title", "description"), 1):
            if s.get(key) is not None:
                g[(i, 1)] = s[key]
        for i, note in enumerate(s.get("notes", []), 3):
            g[(i, 1)] = note
    hr = s["header_row"]
    for j, c in enumerate(s["columns"], 1):
        if c is not None:
            g[(hr, j)] = c
    for i, row in enumerate(s["rows"], hr + 1):
        for j, c in enumerate(s["columns"], 1):
            if c is not None and row.get(c) is not None:
                g[(i, j)] = row[c]
    for sec in s.get("sections", []):
        g[(sec["row"], 1)] = sec["title"]
        for j, h in enumerate(sec["header"], 1):
            if h is not None:
                g[(sec["row"] + 1, j)] = h
        for i, r in enumerate(sec["rows"], sec["row"] + 2):
            for j, v in enumerate(r, 1):
                if v is not None:
                    g[(i, j)] = v
    return g


def grid_sheets(doc):
    return {s["name"]: sheet_grid(s) for s in doc["sheets"]}


# ---------- recipes model ----------
KIT = ["Format", "Channel", "Surface"]
KIT_FIELD = {"Format": "format", "Channel": "channel", "Surface": "surface"}
PLAIN = {"Recipe ID": "id", "Recipe": "name", "Track": "track", "Desired response": "desired_response", "CTA": "cta",
         "When": "when", "Why it works": "why_it_works", "Risk": "risk", "How to apply": "how_to_apply", "Source": "source",
         "Time to first result": "time_to_first_result"}


@lru_cache(maxsize=None)
def recipe_context():
    """What the derived recipe columns read: Customer States Journey stage, Channels Ownership."""
    sp = {s["name"]: s for s in read("space")["sheets"]}
    journey = {r["State"]: r["Journey stage"] for r in sp["Customer States"]["rows"]}
    owner = {r["Key"]: r["Ownership"] for r in sp["Channels"]["rows"]}
    return journey, owner


def _lettered(p, vals):
    if not vals:
        return None
    if p.get("kit_lettered", True):
        return "\n".join(f"{letter}. {v}" for letter, v in vals)
    return vals[0][1]


def recipe_row(p):
    """One recipe as a stage-sheet row {column: value}; Journey stage, Ownership and Content units are derived."""
    journey, owner = recipe_context()
    row = {col: p.get(field) for col, field in PLAIN.items()}
    row["State"] = ", ".join(p["states"]) or None
    row["Journey stage"] = ", ".join(dict.fromkeys(journey[s] for s in p["states"])) or None
    for col in KIT:
        row[col] = _lettered(p, [(o["option"], o[KIT_FIELD[col]]["key"]) for o in p["kit"] if o.get(KIT_FIELD[col])])
    row["Ownership"] = _lettered(p, [(o["option"], owner[o["channel"]["key"]]) for o in p["kit"] if o.get("channel")])
    row["Audiences"] = ", ".join(a["name"] for a in p["audiences"]) or None
    m = p["metrics"]
    row["Direct metrics"] = ", ".join(x["name"] for x in m["direct"]) or None
    row["Downstream metrics"] = ", ".join(x["name"] for x in m["downstream"]) or None
    row["Metric note"] = m.get("note")
    return row


def recipes(doc=None):
    """Every recipe once, in stage-sheet order."""
    doc = doc or read("recipes")
    return list({rid: doc["recipes"][rid] for st in doc["stages"] for rid in st["recipes"]}.values())


def grid_recipes(doc):
    out = {}
    for st in doc["stages"]:
        g = {}
        if st.get("title") is not None:
            g[(1, 1)] = st["title"]
        if st.get("description") is not None:
            g[(2, 1)] = st["description"]
        cols = doc["stage_columns"]
        for j, c in enumerate(cols, 1):
            g[(3, j)] = c
        for i, rid in enumerate(st["recipes"], 4):
            row = recipe_row(doc["recipes"][rid])
            for j, c in enumerate(cols, 1):
                if row.get(c) is not None:
                    g[(i, j)] = row[c]
        out[st["stage"]] = g
    for s in doc.get("sheets", []):  # views after the stage sheets: Possibilities
        out[s["name"]] = sheet_grid(s)
    return out


def grids(key, doc=None):
    doc = doc or read(key)
    return grid_recipes(doc) if key == "recipes" else grid_sheets(doc)
