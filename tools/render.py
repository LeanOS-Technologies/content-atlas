"""Write the human-readable outputs from the JSON.

    python tools/render.py xlsx     every model's xlsx from its JSON
    python tools/render.py md       the .md beside every JSON table and document
    python tools/render.py all

An existing xlsx is used as the style template: its cell styles, column widths, frozen panes and dropdowns stay;
every value is rewritten from the JSON. New table rows take the style of the row above; title and header rows never do.
"""
import argparse
import json
from copy import copy
from pathlib import Path

import models
from atlas import LAYOUT, ROOT, load_json

STYLES = load_json("tools/styles.json")


# ---------- xlsx ----------
def _meta(doc, key, name):
    """(columns, header row, rows as {column: value}) of one sheet, for any model."""
    if key == "recipes" and any(x["stage"] == name for x in doc["stages"]):
        st = next(x for x in doc["stages"] if x["stage"] == name)
        return doc["stage_columns"], 3, [models.recipe_row(doc["recipes"][rid]) for rid in st["recipes"]]
    s = models.sheet(doc, name)
    return s["columns"], s["header_row"], s["rows"]


def _colors(spec):
    if "colors" in spec:
        return spec["colors"]
    src = spec.get("colors_from")
    if src == "stage_funnel":  # a state takes the colour of its funnel position
        funnel = STYLES["space"]["Customer States"]["colors"]
        stages = models.sheet(models.read("space"), "Customer States")["rows"]
        return {r["State"]: funnel[r["Funnel"]] for r in stages}
    return STYLES["space"][src]["colors"] if src else {}


def _autowidth(ws, j, col, values):
    """Width for a text column whose width is unset, the default, or narrower than its header word."""
    from openpyxl.utils import get_column_letter
    dim = ws.column_dimensions[get_column_letter(j)]
    longest_word = max((len(w) for w in str(col).split()), default=4)
    if dim.width not in (None, 13.0) and dim.width >= longest_word + 1:
        return
    lens = sorted(len(str(v).split("\n")[0]) for v in values if v not in (None, ""))
    p90 = lens[int(len(lens) * 0.9)] if lens else 0
    dim.width = max(10, min(48, max(p90, longest_word) + 2))


def _style_grouped(ws, doc, name, spec, base):
    """A sheet whose columns sit in groups (Full matrix): group labels on row 1, header on the header row, a strong line
    and a tint per group, text columns sized to content."""
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

    s = models.sheet(doc, name)
    hr, cols = s["header_row"], s["columns"]
    grid = Side(style="thin", color=base["grid"])
    strong = Side(style="medium", color=base["group_line"])
    tints = spec["column_groups"]
    pos = {c: j for j, c in enumerate(cols, 1) if c}
    group_of, starts = {}, set()
    for i, (g, gc) in enumerate(s["column_groups"].items()):
        starts.add(pos[gc[0]])
        for c in gc:
            group_of[pos[c]] = tints[i % len(tints)]
    ws.freeze_panes = spec.get("freeze")
    for j, col in enumerate(cols, 1):
        left = strong if j in starts else grid
        g = ws.cell(1, j)
        g.fill = PatternFill("solid", fgColor=group_of.get(j, tints[0]))
        g.font = Font(bold=True, size=base["body_size"] + 1)
        g.alignment = Alignment(wrap_text=False, vertical="center")
        g.border = Border(left=left, top=grid, bottom=grid)
        h = ws.cell(hr, j)
        h.fill = PatternFill("solid", fgColor=base["header_fill"])
        h.font = Font(bold=True, color=base["header_font"], size=base["body_size"])
        h.alignment = Alignment(wrap_text=True, vertical="center")
        h.border = Border(left=left, right=grid, top=grid, bottom=strong)
        for i, row in enumerate(s["rows"]):
            c = ws.cell(hr + 1 + i, j)
            c.fill = PatternFill(fill_type=None)
            c.font = Font(bold=col in spec.get("bold", []), size=base["body_size"])
            c.alignment = Alignment(wrap_text=True, vertical="top")
            c.border = Border(left=left, right=grid, top=grid, bottom=grid)
        _autowidth(ws, j, col, [row.get(col) for row in s["rows"]])
    ws.row_dimensions[1].height = 20
    ws.row_dimensions[hr].height = 45
    for i in range(len(s["rows"])):
        ws.row_dimensions[hr + 1 + i].height = None


def style(wb, doc, key):
    """Apply tools/styles.json: shared base look, group colours, group lines, grade colours, bold anchors, tab colour, frozen panes."""
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

    base = STYLES["base"]
    none = PatternFill(fill_type=None)
    grid = Side(style="thin", color=base["grid"])
    strong = Side(style="medium", color=base["group_line"])
    specs = STYLES.get(key, {})
    for name in wb.sheetnames:
        spec = {**specs.get("*", {}), **specs.get(name, {})}
        if not spec:
            continue
        ws = wb[name]
        ws.sheet_properties.tabColor = spec["tab"]
        if spec.get("tab_only"):
            continue
        if spec.get("column_groups"):
            _style_grouped(ws, doc, name, spec, base)
            continue
        cols, hr, rows = _meta(doc, key, name)
        cols = [c for c in cols]
        width = len(cols)
        ws.freeze_panes = spec.get("freeze")
        ws.cell(1, 1).font = Font(bold=True, size=base["title_size"])
        for r in range(2, hr):
            ws.cell(r, 1).font = Font(italic=True, size=base["body_size"], color=base["description_color"])
            ws.cell(r, 1).alignment = Alignment(wrap_text=False, vertical="top")
        ws.cell(1, 1).alignment = Alignment(wrap_text=False, vertical="top")
        lead = spec.get("lead")
        cells = spec.get("grid")
        values = base["grades"] if cells == "grades" else (cells or {})
        if spec.get("grade_column"):
            values = base["grades"]
        is_cell = (lambda c: c not in lead) if lead is not None else (lambda c: False)
        for j, col in enumerate(cols, 1):
            c = ws.cell(hr, j)
            c.fill = PatternFill("solid", fgColor=base["header_fill"])
            c.font = Font(bold=True, color=base["header_font"], size=base["body_size"])
            c.border = Border(left=grid, right=grid, top=grid, bottom=strong)
            if cells and is_cell(col):
                c.alignment = Alignment(text_rotation=90, vertical="bottom", horizontal="center")
                ws.column_dimensions[c.column_letter].width = base["grid_width"]
            else:
                c.alignment = Alignment(wrap_text=True, vertical="center")
                if spec.get("text_width") and is_cell(col):
                    ws.column_dimensions[c.column_letter].width = spec["text_width"]
        ws.row_dimensions[hr].height = 150 if cells else 30
        for j, col in enumerate(cols, 1):  # text columns without a set width are sized to their content
            if not (cells and is_cell(col)):
                _autowidth(ws, j, col, [row.get(col) for row in rows])
        by, colors = spec.get("by"), _colors(spec)
        grade_cols = {spec["grade_column"], "Audience grade"} if spec.get("grade_column") else set()
        for i, row in enumerate(rows):
            r = hr + 1 + i
            ws.row_dimensions[r].height = None
            fill = PatternFill("solid", fgColor=colors[row[by]]) if by and row.get(by) in colors else None
            closes = by and (i == len(rows) - 1 or rows[i + 1].get(by) != row.get(by))
            for j, col in enumerate(cols, 1):
                c = ws.cell(r, j)
                v = row.get(col)
                if (cells and is_cell(col) or col in grade_cols) and v in values:
                    c.fill = PatternFill("solid", fgColor=values[v][0])
                    c.font = Font(size=base["body_size"] - 1, color=values[v][1], bold=v == "Primary")
                    c.alignment = Alignment(horizontal="center", vertical="center")
                else:
                    c.fill = fill if col in spec.get("columns", []) else none
                    c.font = Font(bold=col in spec.get("bold", []), size=base["body_size"])
                    c.alignment = Alignment(wrap_text=True, vertical="top")
                c.border = Border(left=grid, right=grid, top=grid, bottom=strong if closes else grid)


def render_xlsx(key):
    import openpyxl
    from openpyxl.cell.cell import MergedCell

    grid = models.grids(key)
    path = ROOT / models.OUTPUTS[key]
    wb = openpyxl.load_workbook(path) if path.exists() else openpyxl.Workbook()
    for name in list(wb.sheetnames):
        if name not in grid:
            del wb[name]
    for name in grid:
        if name not in wb.sheetnames:
            wb.create_sheet(name)
    wb._sheets = [wb[n] for n in grid]
    doc = models.read(key)
    body = {**({st["stage"]: 4 for st in doc["stages"]} if key == "recipes" else {}),
            **{s["name"]: s["header_row"] + 1 for s in doc.get("sheets", [])}}
    for name, cells in grid.items():
        ws = wb[name]
        for rng in list(ws.merged_cells.ranges):  # cells are written one by one; no layout depends on merges
            ws.unmerge_cells(str(rng))
        for row in ws.iter_rows():
            for c in row:
                if not isinstance(c, MergedCell) and c.value is not None:
                    c.value = None
        for (r, j), v in sorted(cells.items()):
            c = ws.cell(r, j)
            if isinstance(c, MergedCell):
                raise ValueError(f"{name} {c.coordinate} is inside a merged range")
            if not c.has_style and r > body[name] and ws.cell(r - 1, j).has_style:  # new table rows only
                c._style = copy(ws.cell(r - 1, j)._style)
            c.value = v
            if isinstance(v, str) and v.startswith("="):
                c.data_type = "s"
    style(wb, doc, key)
    for name, cells in grid.items():  # nothing below the last value: no leftover rows
        ws, last = wb[name], max(r for r, _ in cells)
        if ws.max_row > last:
            ws.delete_rows(last + 1, ws.max_row - last)
        right = max(j for _, j in cells)  # nothing right of the last column
        if ws.max_column > right:
            ws.delete_cols(right + 1, ws.max_column - right)
    wb.calculation.fullCalcOnLoad = False
    wb.save(path)
    return path


# ---------- md ----------
def _cell(v):
    if v is None:
        return ""
    if isinstance(v, float):
        v = f"{v:g}"
    if isinstance(v, list):
        v = "; ".join(map(str, v))
    return str(v).replace("|", "\\|").replace("\n", "<br>")


def md_table(columns, rows):
    out = ["| " + " | ".join(_cell(c) for c in columns) + " |", "|" + "---|" * len(columns)]
    for r in rows:
        vals = r if isinstance(r, list) else [r.get(c) for c in columns]
        out.append("| " + " | ".join(_cell(v) for v in vals) + " |")
    return out


def md_for(doc, title=None):
    """Markdown for one JSON table or document; the layout follows the document's shape."""
    out = [f"# {title or doc.get('title') or doc['name']}", ""]
    intro = doc.get("subtitle") or doc.get("description")
    if intro:
        out += [intro, ""]
    if "tables" in doc:  # Examples
        for t in doc["tables"]:
            out += [f"## {t['title']}", ""] + md_table(t["columns"], t["rows"]) + [""]
    else:  # a table, optionally with sections below it
        out += md_table(doc["columns"], doc["rows"]) + [""]
        for t, sec in doc.get("sections", {}).items():
            out += [f"## {t}", ""] + md_table(sec["columns"], sec["rows"]) + [""]
    return "\n".join(out)


TITLES = {}


def md_documents():
    """(json path, md path, md text) for every JSON table and document that has a md beside it."""
    out = []
    for name, rel in list(LAYOUT["tables"].items()) + list(LAYOUT["documents"].items()):
        p = ROOT / rel
        doc = json.loads(p.read_text())
        out.append((p, p.with_suffix(".md"), md_for(doc, TITLES.get(name))))
    from spec import specs  # the spec of each vertical, written from its JSON
    out += [(None, ROOT / rel, text) for rel, text in specs().items()]
    return out


def render_md():
    docs = md_documents()
    for _, md_path, text in docs:
        md_path.write_text(text)
    return len(docs)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("what", choices=["xlsx", "md", "all"])
    a = ap.parse_args(argv)
    if a.what in ("xlsx", "all"):
        for key in models.MODELS:
            print("wrote", render_xlsx(key).relative_to(ROOT))
    if a.what in ("md", "all"):
        print("wrote", render_md(), "md files")


if __name__ == "__main__":
    main()
