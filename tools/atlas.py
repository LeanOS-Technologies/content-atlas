"""Read the Content Atlas models into tables.

Everything is read from JSON: the models (space, content units, fit maps, recipes, transformations) through models.py, and the
compose documents (Template, Examples) from their JSON files. A table is a header plus rows of
{column: value}. xlsx and md files are outputs; no layer reads them.
"""
import json
from pathlib import Path

import models

ROOT = models.ROOT


def load_json(rel):
    return json.loads((ROOT / rel).read_text())


# Which model or JSON table holds each sheet, and the stage sheets of the recipes model.
LAYOUT = {'tables': {},
 'sheets': {'Content Units': 'place',
            'Customer States': 'space',
            'Formats': 'space',
            'Channels': 'space',
            'Ownership': 'space',
            'Surfaces': 'space',
            'Audiences': 'space',
            'Metrics': 'space',
            'Full matrix': 'place',
            'Compact matrix': 'place',
            'Format State Fit': 'fit_maps',
            'Format Ownership Fit': 'fit_maps',
            'Channel State Fit': 'fit_maps',
            'Ownership State Fit': 'fit_maps',
            'Format Channel Fit': 'fit_maps',
            'Format Surface Fit': 'fit_maps',
            'Channel Surface Fit': 'fit_maps',
            'State Surface Fit': 'fit_maps',
            'Audience State Fit': 'fit_maps',
            'Audience Format Fit': 'fit_maps',
            'Audience Channel Fit': 'fit_maps',
            'Unaware': 'recipes',
            'Problem-aware': 'recipes',
            'Solution-aware': 'recipes',
            'Product-aware': 'recipes',
            'Decision': 'recipes',
            'Purchase': 'recipes',
            'Onboarding': 'recipes',
            'Retention': 'recipes',
            'Expansion': 'recipes',
            'Resurrection': 'recipes',
            'Advocacy': 'recipes',
            'Format transformations': 'transformations',
            'Content unit ↔ Transformation': 'transformations',
            'Content unit ↔ Repurposing': 'transformations',
            'Content unit ↔ Recipe': 'place',
            'Possibilities': 'recipes',
            'Candidates': 'transformations'},
 'stage_sheets': ['Unaware',
                  'Problem-aware',
                  'Solution-aware',
                  'Product-aware',
                  'Decision',
                  'Purchase',
                  'Onboarding',
                  'Retention',
                  'Expansion',
                  'Resurrection',
                  'Advocacy'],
 'documents': {'Template': 'knowledge/model/compose/template.json',
               'Examples': 'knowledge/model/compose/examples.json'}}
MANIFEST = LAYOUT


class Table:
    def __init__(self, name, header, rows):
        self.name = name
        self.header = header
        self.rows = rows

    def column(self, name):
        return [r.get(name) for r in self.rows]

    def index(self, key):
        """First row per non-empty key value."""
        out = {}
        for r in self.rows:
            k = r.get(key)
            if k not in (None, "") and k not in out:
                out[k] = r
        return out


def _sheet_tables(s):
    out = {s["name"]: Table(s["name"], [c for c in s["columns"] if c is not None], [dict(r) for r in s["rows"]])}
    for sec in s.get("sections", []):
        hdr = sec["header"]
        rows = [{h: v for h, v in zip(hdr, r) if h is not None} for r in sec["rows"]]
        name = f"{s['name']} / {sec['title']}"
        out[name] = Table(name, [h for h in hdr if h is not None], rows)
    return out


def read_table(name, root=ROOT):
    """A table kept as JSON, with its sections as 'Sheet / Section' tables."""
    doc = json.loads((Path(root) / LAYOUT["tables"][name]).read_text())
    out = {name: Table(name, doc["columns"], doc["rows"])}
    for title, sec in doc.get("sections", {}).items():
        out[f"{name} / {title}"] = Table(f"{name} / {title}", sec["columns"], sec["rows"])
    return out


SHEET_MODELS = ("space", "place", "fit_maps", "transformations")


def load(key, sheets=None, root=ROOT):
    """Tables of one model ('space', 'place', 'fit_maps', 'recipes', 'transformations') or of a JSON table group
    (). Each named sheet is read from the model or JSON table that holds it, whichever key is given."""
    out = {}
    if key in SHEET_MODELS:
        docs = {}
        def by_name(k):
            if k not in docs:
                docs[k] = {s["name"]: s for s in models.read(k)["sheets"]}
            return docs[k]
        for n in sheets or list(by_name(key)):
            if n in LAYOUT["tables"]:
                out.update(read_table(n, root))
            else:
                owner = LAYOUT["sheets"].get(n, key)
                out.update(_sheet_tables(by_name(owner if owner in SHEET_MODELS else key)[n]))
        return out
    if key == "recipes":
        doc = models.read("recipes")
        names = sheets or [st["stage"] for st in doc["stages"]]
        for st in doc["stages"]:
            if st["stage"] in names:
                out[st["stage"]] = Table(st["stage"], doc["stage_columns"],
                                         [models.recipe_row(doc["recipes"][rid]) for rid in st["recipes"]])
        return out
    for n in sheets or [n for n, g in LAYOUT["sheets"].items() if g == key and n in LAYOUT["tables"]]:
        out.update(read_table(n, root))
    return out


def load_recipes():
    """Recipes as stage-sheet rows, one entry per Recipe ID (a recipe on two stage sheets appears once)."""
    t = load("recipes")
    out = {}
    for name in LAYOUT["stage_sheets"]:
        for r in t[name].rows:
            if r.get("Recipe ID") and r["Recipe ID"] not in out:
                out[r["Recipe ID"]] = r
    return out


def split_known(value, known):
    """Split a comma-separated list whose items may themselves contain commas, matching against known values."""
    if value in (None, ""):
        return []
    if value in known:
        return [value]
    parts, out, buf = [x.strip() for x in str(value).split(",")], [], ""
    for p in parts:
        buf = f"{buf}, {p}" if buf else p
        if buf in known:
            out.append(buf)
            buf = ""
    if buf:
        out += [x.strip() for x in buf.split(",")]
    return out


def split(value, sep=","):
    return [x.strip() for x in str(value).split(sep) if x.strip()] if value not in (None, "") else []


def selected(rows, product):
    """Rows of one product; '*' or 'All' selects every row."""
    if product in ("*", "All", None):
        return list(rows)
    return [r for r in rows if r.get("Product") == product]
