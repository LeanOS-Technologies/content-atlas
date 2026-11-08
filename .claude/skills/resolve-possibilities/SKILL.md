---
name: resolve-possibilities
description: Given a content requirement in ordinary words, resolve everything the Content Atlas holds for it — the steps reachable from the people and states it is about, the links between them, and checked routes — as a possibilities artifact. Use when a requester asks what content they can do, for whom, where.
---

# Resolve possibilities

Requirement × atlas → possibilities: Steps, Links, checked Routes and the atlas rows they use, in `artifacts/<name>/`.

## Inputs

The requirement as stated. Optional: states and audiences the requester names. Shape: contracts/inputs.md › Resolve request.

## Method

| Step | Owner | What happens |
|---|---|---|
| 1. Interpret | AI | Read who the content is for and what they already know (knowledge/requirement-mapping.md). Set anchors: the states and audiences the requirement is about. When the words fit two states, anchor both. Keep any focus the requester states (channels, formats, timing) as filter params for filter-possibilities; anchors hold only states and audiences. |
| 2. Write the request | AI | `artifacts/<name>/request.json` with name, requirement, anchors. |
| 3. Enumerate | program | `python tools/possibilities.py resolve artifacts/<name>/request.json --out artifacts/<name> --no-xlsx`: every recipe option and content unit at the anchors, then every step reachable within 3 links (Progression, Transformation, Candidate) sharing an audience; with the atlas rows those steps use. |
| 4. Compose routes | AI | Over Steps and Links, compose the routes knowledge/route-composition.md names for this requirement. Write each with id, name, why and steps to `routes.json`. Why names the requirement it answers and the conditions read: the recipe's When and Risk, the state's Proof needed and Friction tolerance. A construction the atlas does not list may be a step when it serves the requirement. |
| 5. Check | program | `python tools/possibilities.py check artifacts/<name> --no-xlsx`: every step's fit-map pairs, every link a Progression or a marked transformation. Findings are written on the route's rows. |
| 6. Correct | AI | A finding owned by the composition (a step or link chosen badly) is corrected in routes.json and rechecked. A route that cannot be made valid without changing the atlas stays, with its finding, and the missing fit or transformation is reported as a model gap. |
| 7. Export | program | When this is the final result, run `python tools/possibilities.py export-xlsx artifacts/<name>` once, after the final route check. If a requested focus will be filtered next, defer workbook rendering to the final filtered result. The JSON, checked routes and findings are unchanged. |
| 8. Report | AI | work-result.md: anchors and why, routes and their findings, filter params kept for a later filter, gaps. |

## Acceptance

- Request check empty, or each unknown value reported (I1).
- Anchor check read: every "not present" row is answered in work-result by the reading the requirement meant (knowledge/requirement-mapping.md › reader or carrier); every "present, no step" row is a model gap (I5).
- Steps and Links are exactly the program's enumeration from the anchors (I2).
- Every route checked; every finding either corrected or reported with its owner (I3, I5).
- Every route's Why cites the conditions it read (I4).
- Nothing cut by channel, ownership, format, track or grade (I6).

## Failure

| Condition | Action |
|---|---|
| Anchor value not an atlas value | reported in Request check; resolve with the rest |
| Anchor check: audience not present at a state | the audience is not the reader there; re-anchor on the reader (requirement-mapping › reader or carrier) and keep the carrier as a filter param |
| Requirement names nobody and no state | anchors empty: whole atlas; say so in work-result |
| No route can be composed for the requirement | report which link or fit is missing; model gap to the atlas owner |
