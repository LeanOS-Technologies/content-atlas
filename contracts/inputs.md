# Inputs

Three request shapes, one per skill. Each is a JSON file; the worker writes it from the conversation and keeps it in the artifact as `request.json` (or `filter.json`). Every value that names an atlas object must be an atlas value (Customer States → State, Audiences → Audience, Formats → Key, Channels → Key, Ownership → Type, Surfaces → Surface); a value that is not is reported in Request check or Placement and left out.

## Resolve request (.claude/skills/resolve-possibilities)

| Field | Meaning | Required | Default |
|---|---|---|---|
| name | artifact folder name, `artifacts/<name>/` | no | `atlas` |
| requirement | the requirement in the requester's words | yes | — |
| anchors.states | customer states the requirement is about; routes start there | no | all 11 |
| anchors.audiences | audiences the requirement is about; a step must share at least one | no | all 16 |

Anchors only say where routes start. Nothing else is cut: every channel, ownership type, format and track stays in the result.

```json
{
  "name": "b2b-decision",
  "requirement": "B2B tool. Buyers are comparing us with two competitors and deciding this quarter. What can we do for them?",
  "anchors": {"states": ["Decision"], "audiences": ["Prospect buyer"]}
}
```

## Map request (.claude/skills/map-existing-content)

| Field | Meaning | Required |
|---|---|---|
| name | artifact folder name | no |
| requirement | what the requester wants to know about their content | yes |
| pieces[] | existing pieces, each placed on the atlas by the worker | yes |
| pieces[].id | the requester's identifier or `EX-n` | yes |
| pieces[].name, where | what the piece is and where it lives | yes |
| pieces[].basis | the evidence the placement rests on (what the piece says, who receives it, how they arrive) | yes |
| pieces[].state, format, channel, surface | atlas values | yes |
| pieces[].audiences | atlas values | no |
| pieces[].track | B2C or B2B | no |

Example: `contracts/examples/existing-b2b.map.json`.

## Routes (composed by the worker, checked by the program)

`artifacts/<name>/routes.json`: a list of routes; each has `id`, `name`, `why` and `steps`. A step is a Step ID of the result (`S-0001`) or a construction `{state, format, channel, surface, audiences}`.

## Filter params (.claude/skills/filter-possibilities)

| Field | Keeps | Empty means |
|---|---|---|
| name | artifact folder name | `<source name>-filtered` |
| states, audiences, channels, ownership, formats | steps with a listed value (audiences: at least one) | no restriction |
| track | steps with track Any or the one given | both |
| min_grade | steps whose state grade is at least Fit, Secondary or Primary; graded Possibilities rows likewise | any grade |
| time_to_first_result | recipe-option steps with a listed value (Days, Weeks, Months) | any |

A route stays only when every one of its steps stays. Example: `contracts/examples/owned-secondary.filter.json`.
