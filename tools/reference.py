"""Reference layer: ID prefixes, their counts and next IDs, ID integrity, channel attribute vocabularies.

    python tools/reference.py              ID table and findings
    python tools/reference.py --json
    python tools/reference.py --next FM    next free ID for a prefix

An ID is given once, in row order, when a row is created. It is never reused
or renumbered; names can change, IDs do not.
"""
import argparse
import json
import re
import sys

from pathlib import Path


from atlas import MANIFEST, load, load_json, split

REFERENCE = load_json("tools/reference.json")


def _tables(sheet_names):
    by_book = {}
    for s in sheet_names:
        by_book.setdefault(MANIFEST["sheets"][s], []).append(s)
    out = {}
    for book, names in by_book.items():
        out.update(load(book, sheets=names))
    return out


def ids(spec, t):
    sheets = spec.get("sheets") or [spec["sheet"]]
    out = []
    for s in sheets:
        out += [r.get(spec["column"]) for r in t[s].rows if r.get(spec["column"])]
    if spec.get("select"):
        out = [i for i in out if str(i).startswith(spec["select"])]
    return out


def next_id(spec, t):
    if spec.get("numbered") is False:
        return None
    found = ids(spec, t)
    m = re.match(r"^(.*?)(\d+)$", spec["first_id"])
    head, width = m.group(1), len(m.group(2))
    nums = [int(i[len(head):]) for i in found if str(i).startswith(head) and str(i)[len(head):].isdigit()]
    return f"{head}{(max(nums) + 1 if nums else 1):0{width}d}"


def check(t):
    findings, table = [], []
    for spec in REFERENCE["prefixes"]:
        found = ids(spec, t)
        uniq = list(dict.fromkeys(found))
        multi_sheet = bool(spec.get("sheets"))
        dup = sorted({i for i in found if found.count(i) > 1}) if not multi_sheet else []
        bad = [i for i in uniq if not re.match(spec["pattern"], str(i))]
        table.append({"prefix": spec["prefix"], "identifies": spec["identifies"],
                      "sheet": spec.get("sheet") or "stage sheets", "count": len(uniq),
                      "first": uniq[0] if uniq else None, "next": next_id(spec, t)})
        if dup:
            findings.append({"code": "R01", "level": "defect", "prefix": spec["prefix"], "ids": dup, "message": "Duplicate ID"})
        if bad:
            findings.append({"code": "R02", "level": "defect", "prefix": spec["prefix"], "ids": bad, "message": "ID does not match its pattern"})
        if spec.get("numbered") is not False:
            nums = [int(re.search(r"(\d+)$", i).group(1)) for i in uniq if re.search(r"\d+$", str(i))]
            out_of_order = [uniq[k] for k in range(1, len(nums)) if nums[k] <= nums[k - 1]]
            if out_of_order:
                findings.append({"code": "R03", "level": "signal", "prefix": spec["prefix"], "ids": out_of_order,
                                 "message": "ID not in row order"})
    ch = t["Channels"]
    for a in REFERENCE["channel_allowed_values"]:
        if a["column"] not in ch.header:
            findings.append({"code": "R04", "level": "signal", "attribute": a["attribute"],
                             "message": f"No Channels column for attribute '{a['attribute']}'"})
            continue
        allowed = {v.lower() for v in a["values"]}
        bad = sorted({str(v) for v in ch.column(a["column"]) if v is not None
                      and not all(x.lower() in allowed for x in split(v))})
        if bad:
            findings.append({"code": "R05", "level": "signal", "attribute": a["attribute"], "values": bad,
                             "message": f"Channels '{a['column']}' values outside the allowed list {a['values']}"})
    return table, findings


def all_tables():
    names = set()
    for spec in REFERENCE["prefixes"]:
        names.update(spec.get("sheets") or [spec["sheet"]])
    names.add("Channels")
    return _tables(sorted(names))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--next", metavar="PREFIX")
    a = ap.parse_args(argv)
    t = all_tables()
    if a.next:
        spec = next(s for s in REFERENCE["prefixes"] if s["prefix"] == a.next)
        print(next_id(spec, t))
        return
    table, findings = check(t)
    if a.json:
        json.dump({"data_version": REFERENCE["data_version"], "ids": table, "findings": findings},
                  sys.stdout, indent=2, ensure_ascii=False)
        print()
        return
    print(f"Data version {REFERENCE['data_version']}")
    for r in table:
        print(f"{r['prefix']:<12} {r['identifies'][:40]:<40} {r['sheet']:<18} {r['count']:>4}  next {r['next'] or '-'}")
    for x in findings:
        print(f"{x['code']} {x['level']}: {x['message']}", ", ".join(map(str, (x.get("ids") or x.get("values") or [])[:12])))


if __name__ == "__main__":
    main()
