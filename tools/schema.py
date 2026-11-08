"""Schema check: the Full matrix against the rules held in the models: header, required values, allowed values.

Rules: content-units.json Full matrix "derived" and Content Units "allowed", "required";
"required".

    python tools/schema.py
    python tools/schema.py --json
"""
import argparse
import json
import sys
from pathlib import Path


from atlas import split_known
from resolve import allowed, allowed_values, required, rules, tables


def check(t):
    """Findings: header drift, missing required tags, values outside their registry or list."""
    findings = []
    m = t["Full matrix"]
    derived = rules()["Full matrix"]
    no_rule = [c for c in m.header if c != "ID" and c not in derived]
    no_column = [c for c in derived if c not in m.header]
    if no_rule or no_column:
        findings.append({"code": "S01", "level": "defect", "message": "Full matrix columns and their rules differ",
                         "missing": no_column, "extra": no_rule})
    for col in required():
        ids = [r.get("ID") for r in m.rows if r.get(col) in (None, "")]
        if ids:
            findings.append({"code": "S02", "level": "defect", "column": col, "count": len(ids), "ids": ids,
                             "message": "Required column is blank"})
    for sheet, rules_ in allowed().items():
      for col, rule in rules_.items():
        ok = allowed_values(rule, t)
        fold = rule.get("ignore_case")
        okf = {str(v).lower() for v in ok} if fold else ok
        bad = []
        for r in t[sheet].rows:
            v = r.get(col)
            if v in (None, ""):
                continue
            for x in (split_known(v, ok) if rule.get("multiple") else [v]):
                if (str(x).lower() if fold else x) not in okf:
                    bad.append((r.get("ID") or r.get("Content unit ID"), x))
        if bad:
            findings.append({"code": "S03", "level": "defect", "sheet": sheet, "column": col, "count": len(bad),
                             "values": sorted({str(x) for _, x in bad}), "ids": [i for i, _ in bad],
                             "message": "Value not in its registry or allowed list"})
    return findings


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    f = check(tables())
    if a.json:
        json.dump(f, sys.stdout, indent=2, ensure_ascii=False, default=str)
        print()
        return
    if not f:
        print("Schema: no findings")
    for x in f:
        where = x.get("column") or x.get("sheet") or ""
        print(f"{x['code']} {x['level']}: {x['message']} {where} ({x.get('count', '')})")
        for k in ("values", "missing", "extra", "out_of_order"):
            if x.get(k):
                print(f"    {k}: {', '.join(map(str, x[k][:12]))}")


if __name__ == "__main__":
    main()
