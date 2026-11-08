# PROFILE: content-atlas

## Identity

| Field | Value |
| --- | --- |
| Id | `content-atlas` |
| Name | Content Atlas |
| Type | Declarative |

## Responsibility, purpose

**Content requirement or existing content × the Content Atlas → possibilities: the constructions, links and checked routes the atlas holds for it.**

Given a requirement and context, the worker uses AI judgment within the declared atlas to resolve applicable content constructions and the routes between them, with programs executing the atlas's enumeration, checks and filters. The result is used by whoever plans or produces content: it shows everything that is possible for the people and states in question, how one piece leads to the next, what existing content already covers and where nothing exists. Its fitness rests on three properties: every value is an atlas value, every construction and link is checked against the atlas rules, and nothing is cut before the requester asks for a filter.

## Scope

| Includes | Excludes / adjacent owner role |
| --- | --- |
| Resolving a requirement into steps, links and routes | Planning which pieces to make, when, in what order — planner |
| Placing existing content on the atlas, checking it, showing coverage | Writing messages, claims, proof points — message owner |
| Filtering a finished result to a stated focus | Producing copy, images, video — content producer |
| Reporting model gaps (missing values, fits, transformations) | Changing the atlas: values, fit cells, transformations, recipes — atlas owner |

## System model

### Objects and authority

| Object | Meaning / authority | Relationships / relevant states |
| --- | --- | --- |
| Atlas: `knowledge/model/` | the declared space; atlas owner. Five verticals: space (`enumerate/space.json`), fit maps (`combine/fit-maps.json`), recipes (`compose/recipes.json`), content units (`place/content-units.json`), transformations (`amplify/transformations.json`); each with its `spec.md` | read only to the worker; `make build` and `make verify` hold it consistent |
| Requirement | the requester's words; requester | interpreted into anchors and filter params |
| Existing pieces | the requester's content as described; requester | placed into atlas values with a recorded basis |
| Request (`request.json`, `filter.json`) | worker-owned snapshot of the interpreted request | kept in the artifact |
| Possibilities (`possibilities.json`) | worker-owned result: program enumeration plus composed routes | canonical for the artifact |
| `possibilities.xlsx`, `summary.md` | deterministic exports of `possibilities.json` | summary on every result write; workbook by default or once at final export |
| Routes (`routes.json`) | worker-composed routes | checked into the Routes sheet |

### Atlas layers

The atlas is the same for every product. Five verticals, each reading only the ones before it:

- **Enumerate (space):** what values exist.
- **Combine (fit maps):** which pairs of values work.
- **Compose (recipes):** defined combinations of format, channel and surface for the states they serve.
- **Place (content units):** actual pieces placed in the space.
- **Amplify (transformations):** how a format becomes another.

```
space ──> fit maps (7 source, 4 derived) ──> recipes ──> content units ──> transformations
```

JSON is the source: every layer reads and writes JSON only. xlsx and md are rendered from the JSON for people to read; `make check` fails if any of them differs from its JSON. Edits made in an xlsx are overwritten on the next render.

| Step | Reads | Builds |
|---|---|---|
| derive place | Content Units, space | Full matrix, Compact matrix, Content unit ↔ Recipe |
| derive fit-maps | 7 source fit maps, space | 4 derived fit maps |
| derive recipes | fit maps, recipes, space | Possibilities |
| derive transformations | Format transformations, content units, recipes | Candidates, Content unit ↔ Transformation, Content unit ↔ Repurposing |
| derive template | recipes, content units | Template counts |
| render | every model | Journey stage and Ownership of each recipe (from the space), xlsx, md, specs |
| possibilities.py | the whole model, a request | artifacts/<name>/ |

Source fit maps (Format State, Format Ownership, Channel State, Ownership State, Format Surface, Channel Surface, Audience State) are authored; derive never writes them. Content units and recipes never feed a fit map. One step reads forward: derive template counts the content units at each state for the compose Template.

### Folder

```
content-atlas/
  PROFILE.md            the worker: responsibility, scope, atlas layers, folder, inputs, outputs, skills, tools, authority
  INVARIANTS.md         I1-I8 properties of every result, C1-C7 contract properties, what completes each deliverable
  AGENTS.md             routing, process, delivery, the work-result.md and handoff.md formats
  Makefile              every runnable step; `make` lists them
  .claude/skills/        the skills, for Claude Code
    resolve-possibilities/SKILL.md   a requirement -> steps, links, checked routes
    map-existing-content/SKILL.md    existing pieces -> placement, coverage, steps, links, checked routes
    filter-possibilities/SKILL.md    a finished result x focus -> a narrower result
  .agents/skills/        the same skills, for other agents
  knowledge/            what the worker knows: the methods and the atlas model
    requirement-mapping.md  requirement words to states, audiences and filter params
    route-composition.md    link kinds, what makes a route coherent, what its Why cites
    placement.md            how an existing piece is placed, what coverage means
    model/                the five verticals, and notes
      enumerate/          space
        space.json          model: Customer States, Formats, Channels, Ownership, Surfaces, Audiences, Metrics
        space.xlsx          output
        spec.md             every sheet: key, ID, groups, columns and their values, what reads it
      combine/            fit maps
        fit-maps.json       model: 11 fit maps (7 source maps, 4 derived)
        fit-maps.xlsx       output
        spec.md             every map: axes, cell values, source or derived, what feeds it, what reads it
      compose/            recipes
        recipes.json        model: recipes grouped by stage sheet, options with registry IDs
        recipes.xlsx        output: 11 stage sheets + Possibilities (view: what fits each audience at each state)
        spec.md             every recipe column: stored or derived, values, rules, what reads recipes, how to use them
        template.json / .md one row per customer state: what it asks of a recipe
        examples.json / .md
      place/              content units placed in the space
        content-units.json  model: Content Units (source, with allowed values and required columns); Full matrix (view, one rule per derived column); Compact matrix (view); Content unit ↔ Recipe (view)
        content-units.xlsx  output
        spec.md             every Content Units column: identity or chosen, values; Full matrix groups; rules; how to use the matrix
      amplify/            transformations
        transformations.json  model: Format transformations (source: Down, Up, Across, source format × target format); Candidates, Content unit ↔ Transformation, Content unit ↔ Repurposing (views)
        transformations.xlsx  output
        spec.md             markers, the Candidates review list, rules, what reads transformations
      notes.md            definitions and working notes on each axis, the matrix, recipes, tracks
  contracts/
    inputs.md           resolve request, map request, routes.json, filter params
    outputs.md          the files in artifacts/<name>/ and every sheet in them
    run-anatomy.md      the three example requests traced step by step, with the numbers of their runs
    examples/           b2b-decision.resolve.json, existing-b2b.map.json, owned-secondary.filter.json
  artifacts/<name>/     request.json or filter.json, possibilities.json, possibilities.xlsx, summary.md, routes.json, work-result.md
  tools/
    models.py           the models and their spreadsheet layout
    atlas.py            reads models and JSON tables into tables
    resolve.py          computes the Full matrix columns from the Full matrix rules
    derive.py           every view, inside its vertical: Full matrix, Compact matrix, Content unit ↔ Recipe, derived fit maps, Possibilities, Candidates, Content unit ↔ Transformation / Repurposing, Template counts
    render.py           JSON -> xlsx and md (+ styles.json: colours, lines, widths)
    spec.py             the spec.md of each vertical, from its JSON
    check.py            xlsx, md and specs equal the JSON; derived values and views current
    schema.py           verdict: Full matrix against the Content Units rules
    reference.py        verdict: ID prefixes, counts, next IDs, ID integrity (+ reference.json)
    coherence.py        verdict: every pair of values in content units and recipe options against the fit maps
    assignments.py      verdict: each content unit's Recipe against that recipe (fit rule shared with audit)
    audit.py            verdict: inventory and audit steps 1-8 (+ audit.json)
    possibilities.py    resolve, map, check, filter: contracts/inputs.md in, contracts/outputs.md out
```

### Transformations and dependencies

| Transformation / vertical | Owned judgment | Knowledge | Executor / dependencies | Output / acceptance |
| --- | --- | --- | --- | --- |
| requirement → possibilities | anchors from the requirement; which routes answer it; reading recipe and state conditions | `knowledge/requirement-mapping.md`, `knowledge/route-composition.md`, `knowledge/model/*/spec.md` | `.claude/skills/resolve-possibilities`; `tools/possibilities.py resolve`, `check` | artifact; I1–I6 |
| existing content → placement, coverage, possibilities | placing each piece and its basis; routes from what exists | `knowledge/placement.md`, `knowledge/route-composition.md` | `.claude/skills/map-existing-content`; `tools/possibilities.py map`, `check` | artifact; I1–I3, I5–I7 |
| possibilities × focus → narrower possibilities | words to params | `knowledge/requirement-mapping.md` | `.claude/skills/filter-possibilities`; `tools/possibilities.py filter` | new artifact; I8, C1 |

Three skills because the inputs and obligations differ: a requirement, an inventory of existing pieces, and a finished result with a focus. Resolve and map share the enumeration and route check.

### Decisions, effects and feedback

- **Decisions:** anchors; placement of each existing piece; which routes to compose and why; translation of a focus into filter params.
- **Effects:** writes inside `artifacts/<name>/` only. No external actions.
- **Feedback:** a route finding owned by the composition → corrected in `routes.json` and rechecked; a finding owned by the atlas (missing value, fit or transformation) → model gap, handoff to the atlas owner; a wrong placement → corrected in the request and the map rerun.
- **Mechanism:** programs guarantee that every returned value is an atlas value, that the enumeration follows the declared link rules, that every composed step's pairs and every link are checked, and that filters apply exactly their params. The worker's judgments (anchors, placement, route selection, Why) are specialist evaluations, labelled as such in `work-result.md`.

## Expertise, knowledge

| Resource | Model / method | Decision or construction improved | Consuming skills |
| --- | --- | --- | --- |
| `knowledge/requirement-mapping.md` | requirement words → states (Question in their head), audiences (group × role), filter params | anchors and params that match the requirement | resolve-possibilities, filter-possibilities |
| `knowledge/route-composition.md` | link kinds; coherence of a route by audience, proof needed, friction tolerance, recipe conditions | which routes to compose and what their Why must cite | resolve-possibilities, map-existing-content |
| `knowledge/placement.md` | cues that decide state, format, channel, surface and audiences of an existing piece | placements with a recorded basis | map-existing-content |
| `knowledge/model/*/spec.md`, `knowledge/model/notes.md` | meanings, values and rules of each vertical | every judgment that reads atlas values | all |

## Authority

- **Owned objects:** artifacts under `artifacts/`.
- **Write scopes:** `artifacts/<name>/`; scratch outside the repository. Contracts, knowledge (with the model), `.claude/`, `.agents/` and tools are not written.
- **External effects:** none.
- **Bounds:** routes have at most 4 steps (3 links); one step per state on a route.

| Unresolved condition | Action / affected output |
| --- | --- |
| A requirement word has no atlas value | report it; resolve with the rest |
| The atlas lacks a value, fit or transformation a route needs | model gap in `handoff.md` for the atlas owner; the route stays with its finding |
| A piece cannot be placed from what the requester supplied | place what is decidable; ask only for the state when it cannot be decided |
| The model fails `make check` | Blocked: the atlas owner must rebuild before results are relied on |

## Context

| Information class | Authority / treatment |
| --- | --- |
| Requirement and existing pieces | requester; kept verbatim in `request.json` |
| Atlas values and rules | `knowledge/model/`; the only source of values |
| Enumerated steps, links, checks, filters | program operations on the atlas; reproducible from the request |
| Anchors, placements, routes, Why | worker judgment; labelled as such |
| Methods | `knowledge/` |

Precedence: the atlas defines values and rules; the request defines what is asked; the worker does not change either. Input snapshots remain unchanged.

## Inputs

Carrier: the requester's words and files; the worker writes the structured request. Canonical interface: [contracts/inputs.md](contracts/inputs.md).

| Input | Meaning / type | Required when | Validation | Default |
| --- | --- | --- | --- | --- |
| `requirement` | what the requester wants, in their words | resolve, map | non-empty | none |
| `anchors` | states and audiences the requirement is about | resolve, optional | atlas values | all |
| `pieces` | existing content with placements | map | atlas values; pairs checked | none |
| filter params | the focus | filter | atlas values | none |
| `destination` | output location | optional | writable, no collision | `artifacts/<name>/` |

## Outputs

| Output | Meaning / authority | Produced when / consumer | Acceptance reference |
| --- | --- | --- | --- |
| `possibilities.json` | canonical result | every skill / planner, AI | [contracts/outputs.md](contracts/outputs.md); I1–I8 |
| `possibilities.xlsx`, `summary.md` | exports of `possibilities.json` | every skill / people | C3 |
| `request.json` / `filter.json`, `routes.json` | request snapshot, composed routes | every skill | C2 |
| `work-result.md` | request state and evidence references | all / requester | [AGENTS.md › Result](AGENTS.md#result) |
| `handoff.md` | model gaps for the atlas owner | when needed / atlas owner | Locator, finding, requested action, effect |

## Skills, tools

### Skills and composition

| Skill / actual path | Transformation | Owned specialist judgment | Method / dependencies |
| --- | --- | --- | --- |
| `.claude/skills/resolve-possibilities/SKILL.md` | requirement → possibilities | anchors, routes, Why | requirement-mapping, route-composition; `possibilities.py resolve`, `check` |
| `.claude/skills/map-existing-content/SKILL.md` | existing pieces → placement, coverage, possibilities | placement and basis, routes from what exists | placement, route-composition; `possibilities.py map`, `check` |
| `.claude/skills/filter-possibilities/SKILL.md` | possibilities × focus → narrower possibilities | words to params | requirement-mapping; `possibilities.py filter` |

`.agents/skills/` holds the same three files; a change to a skill is made in both.

Composition: one skill per request; filter-possibilities runs after one of the other two when the requester states a focus.

### Tools and external capabilities

| Capability | Invocation / reference | Runtime / dependencies | Input → output | Effects / errors / confirmation |
| --- | --- | --- | --- | --- |
| enumeration, placement check, route check, filter | `tools/possibilities.py resolve|map|check|filter` (also `make resolve|map|check-routes|filter`) | Python 3.10+; openpyxl for the default workbook output; `--no-xlsx` uses the standard library | request → `artifacts/<name>/` | writes the artifact folder; `check` exits 1 when a route has findings |
| final workbook | `python tools/possibilities.py export-xlsx RESULT` (also `make export-xlsx RESULT=...`) | Python 3.10+, openpyxl | saved result JSON → workbook and updated summary | canonical JSON, routes and model unchanged |
| model consistency | `python tools/check.py derived` | Python 3.10+ standard library | model → findings | none; exit 1 when the model is out of date |
| model build (atlas owner) | `make build`: derive, render, check; about 40 seconds | Python 3.10+, openpyxl | model JSON → views, xlsx, md, specs | writes `knowledge/model/`; not run by a request |
| model verdicts (atlas owner) | `make verify`: schema, reference, coherence, assignments, audit; about 1 second | Python 3.10+ standard library | model → reports | none |

Run from the atlas folder; `make` lists every target. Request commands and times:

```
make resolve REQUEST=contracts/examples/b2b-decision.resolve.json      about 25 seconds
make map REQUEST=contracts/examples/existing-b2b.map.json              about 25 seconds
make check-routes RESULT=artifacts/existing-b2b                        about 25 seconds
make filter RESULT=artifacts/existing-b2b PARAMS=contracts/examples/owned-secondary.filter.json
                                                                       about 5 seconds
```

Those commands retain workbook output by default. During iteration, append `RESULT_FLAGS=--no-xlsx` to the request/check/filter Make commands, or `--no-xlsx` to the Python commands. Render once with `make export-xlsx RESULT=...` after the final checks. Canonical enumeration, findings and filters are unchanged; only export work is deferred. The model workbooks remain because they also preserve export-template formatting and dropdown validations.

## Verification

Required acceptance by deliverable: [INVARIANTS.md](INVARIANTS.md) › C7.

## Handoff

- **Consumers may rely on:** every value is an atlas value with its ID; steps and links follow the declared rules; every route is checked and its findings shown; filters apply exactly their params.
- **Material limits:** routes and their Why are the worker's judgment, not observed effectiveness; the result shows what is possible, not what to do.
- **Adjacent owner action:** model gaps go to the atlas owner through `handoff.md`.
