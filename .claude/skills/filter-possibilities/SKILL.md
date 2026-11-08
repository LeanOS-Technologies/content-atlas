---
name: filter-possibilities
description: Narrow a finished possibilities artifact to the requester's focus (states, audiences, channels, ownership, formats, track, minimum grade, time to first result) into a new artifact, without recomputing anything. Use after resolve-possibilities or map-existing-content, when the requester wants to see one part of it.
---

# Filter possibilities

Possibilities artifact × params → a narrower possibilities artifact.

## Inputs

An artifact folder with possibilities.json; the focus in the requester's words. Shape: contracts/inputs.md › Filter params.

## Method

| Step | Owner | What happens |
|---|---|---|
| 1. Translate | AI | Words to params (knowledge/requirement-mapping.md › Filter params). State each translation in work-result.md ("owned, earned and shared channels" → ownership Owned, Earned, Shared). |
| 2. Filter | program | `python tools/possibilities.py filter artifacts/<name> filter.json --no-xlsx`: steps kept by every param, links between kept steps, routes whose every step is kept, the atlas rows the kept steps use, Possibilities rows of kept values at or above min_grade. Writes `artifacts/<filter name>/`; the source artifact is unchanged. |
| 3. Export | program | `python tools/possibilities.py export-xlsx artifacts/<filter name>`: render the final workbook from the saved JSON and refresh its summary. |
| 4. Report | AI | work-result.md: params, rows before and after per sheet, routes dropped and why. |

## Acceptance

- The source artifact is unchanged (C1).
- Every kept step satisfies every param; every dropped route has a dropped step (I8).
- Params with values not in their registry are reported in Request check.
