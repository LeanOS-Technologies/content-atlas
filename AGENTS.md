# AGENTS: content-atlas

Operating procedure for this worker. [PROFILE.md](PROFILE.md) owns its declaration, interfaces and authority. [INVARIANTS.md](INVARIANTS.md) owns required properties and verification. This file owns routing, execution, recovery and delivery.

## Routing

| Request / condition | Execution path / stop point |
| --- | --- |
| "What can we do for …", "what content works at …", a requirement without existing content | `.claude/skills/resolve-possibilities` → artifact with Steps, Links, checked Routes |
| Existing content supplied (list, sitemap, inventory), "what do we have", "what is missing", "where can this go" | `.claude/skills/map-existing-content` → artifact with Placement, Coverage, Steps, Links, checked Routes |
| A focus on a finished result ("owned and earned channels", "written formats", "B2B", "Secondary and Primary fits") | `.claude/skills/filter-possibilities` on that artifact → new artifact |
| A requirement with a focus and no artifact yet | resolve-possibilities or map-existing-content first, then filter-possibilities; the focus goes into filter.json |
| Which pieces to make, when, in what order | out of scope: planner; return the possibilities artifact as its input |
| Messages, claims, copy, production | out of scope: message owner, content producer |
| Adding or changing atlas values, fits, transformations, recipes | out of scope for a request; record the proposal in `handoff.md` |

Use the simplest supported executor. Do not create additional agents or workflows for a request that a skill can complete.

## Process

**Resolve → Validate → Reason and construct → Verify → Deliver.**

### 1. Resolve

- Read the requirement and any supplied content. Identify who the content is for, what they already know, and any focus.
- Set anchors (resolve) or placements (map); keep the focus as filter params for a later filter. Record each as a material decision.
- Ask only when the state of the people in question cannot be decided from what was said; continue with what is decidable.
- Destination: `artifacts/<name>/` with a name not already used ([Delivery](#delivery)).

### 2. Validate

- `python tools/check.py derived` exits 0; otherwise Blocked: the model must be rebuilt (`make build`) before a request runs.
- Values are validated by the program run (Request check, Placement); do not pre-filter them by hand.

### 3. Reason and construct

Executor: the routed skill. Its SKILL.md owns the method.

- **resolve-possibilities:** anchors → `possibilities.py resolve` → routes composed over Steps and Links (knowledge/route-composition.md) → `possibilities.py check`.
- **map-existing-content:** placements with basis (knowledge/placement.md) → `possibilities.py map` → routes from the pieces → `possibilities.py check`.
- **filter-possibilities:** params (knowledge/requirement-mapping.md) → `possibilities.py filter`.
- **Exports:** use `--no-xlsx` while resolving, composing, checking or filtering intermediate results; finish with `possibilities.py export-xlsx` once the final routes and focus are settled. CLI commands retain their existing workbook output by default. JSON-only operations remove any previous workbook; the final export uses the saved JSON without recomputing possibilities.
- **Output:** `possibilities.json` with its xlsx and summary; `contracts/outputs.md`.
- **Acceptance:** INVARIANTS › C7 for the deliverable.

### 4. Verify and correct

- Read Request check, Anchor check, Placement and every Routes finding in the actual `possibilities.json`.
- Correct findings owned by the composition or placement and rerun the owning operation; recheck the routes it affects.
- Evaluate each route's Why (I4) and classify every remaining gap (I5).

| Defect | Correction owner / next action |
| --- | --- |
| Unknown value from interpretation | resolve step; correct the anchor or placement and rerun |
| Route step or link with a finding the composition caused | composition; edit `routes.json`, run `check` |
| Placement contradicting its basis | placement; correct the request and rerun `map` |
| Missing value, fit or transformation in the atlas | model gap in `handoff.md`; the route stays with its finding |
| Program error | `tools/possibilities.py`; Failed for the affected output |

### 5. Deliver

- Write `work-result.md` in the artifact folder. Create `handoff.md` when the request meets a model gap.
- Return the artifact folder, the summary's key counts, the routes and their findings, and the unresolved gaps.

## Delivery

| Mode / destination | Behaviour |
| --- | --- |
| Create; explicit destination | use it; refuse to overwrite another request's result |
| Create; destination omitted | `artifacts/<name>/` |
| Filter | a new `artifacts/<filter name>/`; the source artifact is not changed |
| Temporary work | scratch outside the repository |

Write scopes: `artifacts/<name>/`; scratch. `contracts/`, `knowledge/` (with the model), `.claude/`, `.agents/` and `tools/` are not written by a request.

## Result

`work-result.md` records only information material to acceptance and use. Omit empty optional sections.

```markdown
# Result: {name}

State: Completed | Blocked | Failed | Cancelled
Requested outcome: possibilities (resolve | map | filter)

## Deliverables

artifacts/{name}/possibilities.json — canonical result
artifacts/{name}/possibilities.xlsx, summary.md — exports

## Acceptance

| Property | Target | Method / evaluator | Observation / verdict | Evidence |
| --- | --- | --- | --- | --- |
| {I-id} | {sheet or file} | {command with exit, or self-review} | {result} | {locator} |

## Material decisions and assumptions

Anchors or placements and why; filter params kept or applied, with their translation.

## Effects and unresolved work

Files written; gaps by class (missing input, no valid construction, model gap); model gaps also in `handoff.md`.
```

## Handoff

`handoff.md` contains one entry per model gap:

```markdown
## model gap: {gap}

Locator: {route, step, placement or request value}
Finding: {the missing value, fit cell or transformation}
Requested action: {add or mark it, or confirm it stays absent}
Effect here: {routes or placements shown with the finding}
```

## Operating rules

- Every value comes from the atlas; nothing is invented to complete a route.
- A focus is a filter, applied after resolve or map.
- Every route is checked after its last change; findings are shown, not removed.
- Routes and their Why are judgment; computed checks are computed. Report each as what it is.
