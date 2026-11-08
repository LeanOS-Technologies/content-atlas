# INVARIANTS: content-atlas

Each invariant states a required property, its observable violation and verification appropriate to that property. A check establishes only what it directly examines.

Notation: `D` = `artifacts/<name>/`; `T` = scratch outside the repository; `U` = none. `P` = `D/possibilities.json`; `R` = `D/routes.json`.

## Domain invariants

### I1 Atlas values only

**Property.** Every state, audience, format, channel, ownership type, surface, recipe, content unit and metric in `P` is an atlas value with its ID; a requested value that is not appears in Request check or Placement and nowhere else.

**Violation signature.** A value in Steps, Routes or Placement that no registry holds; an invented channel or format.

**Verification.**
- Class: computational.
- Target and method: `possibilities.py` builds every sheet from `knowledge/model/`; request values are looked up before use (Request check, Placement › Check).
- Acceptance: Request check lists exactly the unknown values; every Placement row with an unknown value says so.
- Evidence: Request check and Placement sheets of `P`.
- Correction owner: interpretation (skill step 1) or the atlas owner for a genuine gap.

### I2 Enumeration follows the declared rules

**Property.** Steps are every recipe option (per state) and content unit at the anchors, plus every step reachable within 3 links; a link is a Progression to the state's Intended progression, or a marked transformation or candidate to another state's step, sharing at least one audience.

**Violation signature.** A step without a link path from an anchor; a link between steps whose formats no transformation joins and whose states are not in progression.

**Verification.**
- Class: computational.
- Target and method: rerun the same request with `possibilities.py` and compare Steps and Links; spot-check links against Customer States › Intended progression and Format transformations.
- Acceptance: identical Steps and Links on rerun; every spot-checked link matches its rule.
- Evidence: the two `P` files; the checked rows.
- Correction owner: `tools/possibilities.py` (graph).

### I3 Every composed route is checked

**Property.** Every route in `R` appears in Routes, each step with its fit-map check and each link with its kind or the reason none exists.

**Violation signature.** A route in `R` missing from Routes; a step with an unmarked pair shown as OK; a link that is neither a Progression nor a marked transformation shown without a finding.

**Verification.**
- Class: computational.
- Target and method: `possibilities.py check D` after the last change to `R`.
- Acceptance: the route count in Routes equals the count in `R`; exit status 0, or 1 with every finding written on its row.
- Evidence: Routes sheet; command exit.
- Correction owner: the composition (skill step 4) for a chosen step or link; the atlas owner for a missing rule.

### I4 Routes state their reasoning

**Property.** Every route's Why names what it answers in the requirement and the conditions read: the recipe's When or Risk where the route uses a recipe, and the state's Proof needed or Friction tolerance where they decide a step.

**Violation signature.** An empty Why; a Why that repeats the route's name; a route through a recipe whose When contradicts the requirement without saying so.

**Verification.**
- Class: specialist evaluation (self-review, labelled).
- Target and method: read each route's Why against the requirement and the cited Recipes and Customer States rows.
- Acceptance: each route cites at least one condition it read, and any contradiction with the requirement is named.
- Evidence: Routes › Why; work-result.md › Acceptance.
- Correction owner: the composition.

### I5 Gaps are classified

**Property.** Each unmet part of a requirement is reported as one of: missing input (the requester did not say), no valid construction (the rules allow none), model gap (the atlas lacks a value, fit or transformation).

**Violation signature.** "Nothing found" without a class; a model gap silently worked around; a missing input treated as no construction.

**Verification.**
- Class: specialist evaluation.
- Target and method: read work-result.md › Effects and unresolved work and `handoff.md` against Request check, Placement and Routes findings.
- Acceptance: every finding that is not corrected has a class and, for model gaps, a handoff entry.
- Evidence: work-result.md, handoff.md.
- Correction owner: the reporting step.

### I6 No cut before the filter

**Property.** Resolve and map results contain every step their anchors reach, regardless of channel, ownership, format, track or grade.

**Violation signature.** A resolve or map result whose Steps exclude an ownership type, format family or track that the anchors reach; a focus written into anchors.

**Verification.**
- Class: computational and structural.
- Target and method: request.json has only name, requirement, anchors (resolve) or pieces (map); rerun shows identical Steps.
- Acceptance: no filter field in request.json; the focus appears in a later filter.json.
- Evidence: request.json; work-result.md › Material decisions (params kept for a filter).
- Correction owner: interpretation (skill step 1).

### I7 Placements have a basis and a check

**Property.** Every existing piece has a Placement row with its values, its basis and its program check.

**Violation signature.** A piece in the request with no Placement row; an empty basis; a placement changed to make a check pass.

**Verification.**
- Class: computational (row and check present) and specialist evaluation (basis supports the values).
- Target and method: compare pieces in request.json with Placement rows; read each basis.
- Acceptance: one row per piece; every basis names what decides the state.
- Evidence: Placement sheet.
- Correction owner: placement (map skill step 1).

### I8 Filters apply exactly their params

**Property.** A filtered result holds exactly the source steps satisfying every param, the links between them, and the routes whose every step is kept; the source artifact is unchanged.

**Violation signature.** A kept step violating a param; a route kept with a dropped step; the source `possibilities.json` changed.

**Verification.**
- Class: computational.
- Target and method: recompute the kept set from the source `P` and the params; compare file hashes of the source before and after.
- Acceptance: equal sets; equal hashes.
- Evidence: both `P` files; filter.json.
- Correction owner: `tools/possibilities.py` (filter).

## Contract invariants

### C1 Ownership and write scopes

**Property.** Writes are confined to `D` and `T`. `contracts/`, `knowledge/` (with the model), `.claude/`, `.agents/` and `tools/` are unchanged by a request. Atlas defects are returned as handoffs.

**Violation signature.** A model file changed by a request; a fit cell added to make a route pass.

**Verification.** Compare hashes of `knowledge/model/` before and after the request; `python tools/check.py` passes after it. Endpoint hashes show byte equality at intake and delivery, not the absence of intermediate writes.

### C2 Request distinction and update integrity

**Property.** Each request writes its own `D`; a second request with the same name uses a new name. A filter writes a new artifact.

**Violation signature.** A result overwritten by another request; a filter written over its source.

**Verification.** Before writing, check that `D` does not hold another request's `request.json`.

### C3 Canonical sources and derived representations

**Property.** `possibilities.json` is canonical; `summary.md` is regenerated with every result write. By default `possibilities.xlsx` is regenerated too. Intermediate operations may use `--no-xlsx`, removing any previous workbook so that no stale export is presented. `export-xlsx` renders the final saved JSON without changing it.

**Violation signature.** xlsx or summary disagreeing with the json; a hand edit to the xlsx.

**Verification.** Default operations rewrite all three; rerunning `check` on an unchanged artifact reproduces them. JSON-only operations retain the same JSON and findings, write an accurate summary and leave no workbook. Exporting afterward preserves the canonical JSON and renders its sheets.

### C4 Supported claims and declared epistemic status

**Property.** Enumerations, checks and filters are reported as computed; anchors, placements, routes and Why as the worker's judgment; nothing claims observed effectiveness.

**Violation signature.** A route described as proven to convert; self-review described as independent.

**Verification.** Read work-result.md against the evidence classes in its Acceptance table.

### C5 Coherent execution and dependencies

**Property.** Every program step named in a skill actually ran; the model is current.

**Violation signature.** Routes reported checked without a `check` run after the last change to `R`; results built on a model failing `check.py`.

**Verification.** `python tools/check.py derived` exits 0 before the request; command exits recorded in work-result.md.

### C6 Authorised and confirmed effects

**Property.** No external effects; execution stays within `D` and `T`.

**Verification.** Same as C1.

### C7 Honest acceptance and completion

**Property.** Completed means the requested artifact meets the properties below and is written.

| Deliverable / maturity | Required properties | Evidence class / method |
| --- | --- | --- |
| resolve artifact | I1, I2, I3, I4, I5, I6, C1–C5 | computational (program runs, exits), specialist (Why, gaps) |
| map artifact | I1, I2, I3, I5, I6, I7, C1–C5 | computational, specialist (basis) |
| filter artifact | I1, I8, C1–C5 | computational |

A program exit establishes the computed properties only; I4, I5 and the basis in I7 need the worker's evaluation, labelled as self-review.
