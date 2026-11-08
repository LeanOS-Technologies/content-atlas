---
name: map-existing-content
description: Given a requester's existing content (a list, sitemap or inventory), place every piece on the Content Atlas, check each placement, show coverage by audience and state, and resolve the possibilities and routes that start from what already exists. Use when the requester has content and asks what it is, what is missing or where it can go.
---

# Map existing content

Existing pieces × atlas → placement, coverage and possibilities anchored on the pieces, in `artifacts/<name>/`.

## Inputs

The pieces as the requester gives them: names, links, descriptions, who receives them. Shape: contracts/inputs.md › Map request.

## Method

| Step | Owner | What happens |
|---|---|---|
| 1. Place | AI | For each piece decide state, format, channel, surface and audiences (knowledge/placement.md). Record the basis: what in the piece or its delivery decides each value. Place as found, including mismatches. |
| 2. Write the request | AI | `artifacts/<name>/request.json` with name, requirement and pieces. |
| 3. Check and enumerate | program | `python tools/possibilities.py map artifacts/<name>/request.json --out artifacts/<name> --no-xlsx`: each value against its registry and each pair against the fit maps (Placement); every audience × state with its pieces (Coverage); then steps reachable from the valid pieces, as in resolve. |
| 4. Read the findings | AI | An unknown value is corrected when the placement was wrong, or reported as a model gap when the atlas lacks it. An unmarked pair is kept: it is a finding about the piece (for example a case study on the blog at Unaware). |
| 5. Compose routes | AI | Routes that connect pieces already held, and from each piece to the next state using what it can become (knowledge/route-composition.md), into routes.json. |
| 6. Check | program | `python tools/possibilities.py check artifacts/<name> --no-xlsx`. |
| 7. Export | program | When this is the final result, run `python tools/possibilities.py export-xlsx artifacts/<name>` once, after the final route check. If a requested focus will be filtered next, defer workbook rendering to the final filtered result. The JSON, checked routes and findings are unchanged. |
| 8. Report | AI | work-result.md: placement with findings, coverage gaps (audience × state with nothing), routes from what exists, model gaps. |

## Acceptance

- Every piece has a placement with its basis and a program check (I7).
- Coverage lists every audience × state where the audience is present (I2).
- Routes checked; findings corrected or reported (I3, I5).
- Nothing cut by channel, ownership, format, track or grade (I6).

## Failure

| Condition | Action |
|---|---|
| Piece too vague to place | place what is decidable, mark the rest in basis, ask the requester only if the state cannot be decided |
| Value the atlas lacks | model gap, handoff to the atlas owner; the piece stays with the finding |
