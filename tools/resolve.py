"""Resolve the Full matrix: compute every derived column from the rules held beside the columns.

Rules: content-units.json Full matrix "derived" (one rule per derived column). Allowed values: Content Units "allowed",
checked on the Full matrix.

resolve(tables) fills every derived column (lookups into the parent sheets,
chained lookups, publishing rules, attainment) so other layers read values,
not formulas.
"""
import models
from atlas import load, split_known


def rules():
    """{sheet: {column: rule}} for every sheet with derived columns."""
    return {"Full matrix": models.sheet(models.read("place"), "Full matrix")["derived"]}


def allowed():
    """{sheet: {column: rule}}: Content Units columns, checked on the Full matrix."""
    return {"Full matrix": models.sheet(models.read("place"), "Content Units")["allowed"]}


def required():
    return models.sheet(models.read("place"), "Content Units")["required"]


def _sheets(r):
    """The sheets the rules read and the sheets they fill."""
    names = set(r)
    for specs in r.values():
        for spec in specs.values():
            names.update(x["sheet"] for x in [spec] + spec.get("steps", []) if "sheet" in x)
    for spec in (s for specs in allowed().values() for s in specs.values()):
        if "registry" in spec:
            names.add(spec["registry"]["sheet"])
    return sorted(names)


def tables(root=None):
    kw = {"root": root} if root else {}
    r = rules()
    return resolve(load("place", sheets=_sheets(r), **kw), r)


def _apply(spec, row, t):
    kind = spec["kind"]
    if kind == "ratio":
        n, d = row.get(spec["numerator"]), row.get(spec["denominator"])
        return n / d if isinstance(n, (int, float)) and isinstance(d, (int, float)) and d else None
    key = row.get(spec["key"])
    if key in (None, ""):
        return None
    if kind == "lookup":
        hit = t[spec["sheet"]].index(spec["match_column"]).get(key)
        return hit.get(spec["value_column"]) if hit else None
    if kind == "lookup_list":  # key holds a comma-separated list; one value per item, in order
        idx = t[spec["sheet"]].index(spec["match_column"])
        vals = [idx[k].get(spec["value_column"]) for k in (x.strip() for x in str(key).split(",")) if k in idx]
        return ", ".join(dict.fromkeys(str(v) for v in vals if v is not None)) or None
    if kind == "chain":
        v = key
        for step in spec["steps"]:
            hit = t[step["sheet"]].index(step["match_column"]).get(v)
            if not hit:
                return None
            v = hit.get(step["value_column"])
        return v
    if kind == "rules":
        hits = [r.get(spec["value_column"]) for r in t[spec["sheet"]].rows
                if {key, spec["also_match"]} & {x.strip() for x in str(r.get(spec["match_column"]) or "").split(";")} and r.get(spec["value_column"])]
        return spec["join"].join(str(h) for h in hits) or None
    raise ValueError(kind)


def resolve(t, r=None):
    """Fill derived columns until nothing changes (derived columns can read other derived columns)."""
    r = r or rules()
    for _ in range(8):
        changed = False
        for sheet, specs in r.items():
            for row in t[sheet].rows:
                for col, spec in specs.items():
                    v = _apply(spec, row, t)
                    if row.get(col) != v:
                        row[col] = v
                        changed = True
        if not changed:
            return t
    raise RuntimeError("derived columns did not settle")


def allowed_values(rule, t):
    if "values" in rule:
        return set(rule["values"])
    reg = rule["registry"]
    rows = t[reg["sheet"]].rows
    for k, v in reg.get("where", {}).items():
        rows = [r for r in rows if r.get(k) == v]
    return {r.get(reg["column"]) for r in rows if r.get(reg["column"]) is not None}
