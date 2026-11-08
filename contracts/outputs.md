# Outputs

Every result is possibilities: what the atlas holds for the request, with the routes composed over it. Nothing is ranked. Resolve and map never cut by channel, ownership, format, track or grade; filter does, as a separate step on a finished result.

## Files in `artifacts/<name>/`

| File | Reader | Holds |
|---|---|---|
| request.json (or filter.json) | anyone | the request as run |
| possibilities.json | AI, further processing | the request and every sheet below under `sheets`: name, description, columns, rows |
| possibilities.xlsx | people | one tab per sheet, styled like the atlas workbooks |
| summary.md | anyone, first | the request, rows per sheet, route findings, placement and request check; no data |
| routes.json | the worker | the composed routes, before they are checked; after a filter, the routes whose every step stays |
| work-result.md | requester | state, deliverables, acceptance with evidence, decisions, unresolved work (AGENTS.md › Result) |

All existing commands retain workbook output by default. For intermediate runs, `--no-xlsx` writes the same canonical JSON and findings plus its summary, and removes any earlier workbook. Finish with `python tools/possibilities.py export-xlsx <result-folder>` to render the final workbook and refresh the summary without rerunning enumeration or route checks. The normal skill delivery still includes the final workbook.

## Sheets

| Sheet | Rows | Built by |
|---|---|---|
| Steps | every construction reachable from the anchors: recipe options (one per state), content units and existing pieces. Columns: Step ID, Depth (links from the nearest anchor), Kind, Source, Name, State, Format, Channel, Ownership, Surface, Audiences, Track, State grade, Time to first result | program |
| Links | From, To, Link (Progression; Transformation: Down/Up/Across; Candidate: marker), Detail. Progression goes to the state's Intended progression; a transformation goes to a step in another state whose format the transformation reaches; both share at least one audience. At most 3 links from an anchor | program |
| Routes | the composed routes, one row per step: Route ID, Route, Step, Step ID, State, Format, Channel, Surface, Link to next, Check, Why | worker composes, program checks |
| Placement (map) | each existing piece: values, basis, Check (OK or each unmarked pair) | worker places, program checks |
| Coverage (map) | every audience × state where the audience is present, with the existing pieces there | program |
| Request check | anchor or filter values not in their registry | program |
| Anchor check (resolve) | each anchor audience × anchor state: Audience State Fit grade, steps addressed to it there, Finding (not present; present, no step) | program |
| Customer States, Audiences, Formats, Channels, Ownership, Surfaces, Metrics | the atlas rows the steps use | program |
| the 11 fit maps | rows and columns of the values the steps use; grades unchanged | program |
| Recipes | the recipes the steps come from, every stage-sheet column | program |
| Possibilities | the atlas Possibilities rows at the states and audiences the steps use (after a filter: of the kept values and grade) | program |
| Content units | the Full matrix rows of the content-unit steps | program |
| Content unit ↔ Transformation, Content unit ↔ Repurposing, Candidates | for those units and formats | program |

State grade: the weakest of the format's, channel's and surface's grade at the step's state (Format State Fit, Channel State Fit, State Surface Fit).

## Not returned

A plan (which pieces, when, in what order), messages and claims, product context, ranking, produced content.
