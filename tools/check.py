"""Strict check that the outputs equal the JSON, and that derived values are current.

    python tools/check.py           all checks; exit status 1 on any difference
    python tools/check.py xlsx      every cell of the three xlsx against the JSON models
    python tools/check.py md        every md against the JSON it is rendered from
    python tools/check.py derived   derived matrix columns, Compact matrix and derived fit maps up to date

xlsx: same sheets in the same order, every cell value equal, no extra cells, no formulas. An empty string
counts as an empty cell.
"""
import argparse
import sys

import models
from atlas import ROOT


def check_xlsx():
    import openpyxl

    problems = []
    for key in models.MODELS:
        path = ROOT / models.OUTPUTS[key]
        if not path.exists():
            problems.append(f"{path.relative_to(ROOT)}: missing (run make render)")
            continue
        grid = models.grids(key)
        wb = openpyxl.load_workbook(path)
        if wb.sheetnames != list(grid):
            problems.append(f"{path.relative_to(ROOT)}: sheets {wb.sheetnames} differ from JSON {list(grid)}")
        for name in grid:
            if name not in wb.sheetnames:
                continue
            ws, want = wb[name], grid[name]
            have = {}
            for row in ws.iter_rows():
                for c in row:
                    v = c.value
                    if v is None or v == "":
                        continue
                    if c.data_type == "f" or hasattr(v, "text"):
                        problems.append(f"{path.name} {name} {c.coordinate}: formula")
                    have[(c.row, c.column)] = v
            diff = [k for k in set(want) | set(have) if want.get(k) != have.get(k)]
            for r, j in sorted(diff)[:5]:
                problems.append(f"{path.name} {name} {openpyxl.utils.get_column_letter(j)}{r}: "
                                f"xlsx {have.get((r, j))!r} != json {want.get((r, j))!r}")
            if len(diff) > 5:
                problems.append(f"{path.name} {name}: {len(diff) - 5} more differences")
    return problems


def check_md():
    from render import md_documents
    problems = []
    for _, md_path, text in md_documents():
        rel = md_path.relative_to(ROOT)
        if not md_path.exists():
            problems.append(f"{rel}: missing (run make render)")
        elif md_path.read_text() != text:
            problems.append(f"{rel}: differs from its JSON (run make render)")
    return problems


def check_derived():
    import derive
    problems = []
    for key, fn in (("place", derive.derive_matrix), ("fit_maps", derive.derive_fit_maps), ("recipes", derive.derive_possibilities), ("transformations", derive.derive_candidates), ("template", derive.derive_template)):
        _, changes = fn()
        if changes:
            problems.append(f"{models.MODELS.get(key) or {'template': derive.TEMPLATE}[key]}: {changes} derived values out of date (run make derive)")
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("what", nargs="?", default="all", choices=["all", "xlsx", "md", "derived"])
    a = ap.parse_args(argv)
    checks = {"derived": check_derived, "xlsx": check_xlsx, "md": check_md}
    failed = False
    for name, fn in checks.items():
        if a.what not in ("all", name):
            continue
        problems = fn()
        print(f"{name}: {'ok' if not problems else f'{len(problems)} problem(s)'}")
        for p in problems:
            print("  ", p)
        failed |= bool(problems)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
