# Place spec

Content units: actual pieces of content placed in the space. Source: `content-units.json`. Output: `content-units.xlsx`, rendered from the JSON. The rules sit beside the columns they govern: Content Units `chosen`, `allowed` and `required`; Full matrix `derived`, one rule per derived column.

| Sheet | Kind | Rows | Columns |
|---|---|---|---|
| Content Units | source: edit here only | 160 | 33 |
| Full matrix | view: recomputed by `make derive` | 160 | 152 in 8 groups |
| Compact matrix | view: columns of the Full matrix | 160 | 12 |
| Content unit ↔ Recipe | view: recomputed by `make derive` | 94 | 6 |

Content unit ↔ Recipe: Recipes whose options produce each content unit as it is: same state, and the option's format, channel and surface (where named) equal the unit's.

## Content Units

One row per content unit. Identity columns say what the unit is; chosen columns place it on each axis of the space.

| Column | Kind | Values | Filled |
|---|---|---|---|
| ID | identity | text | 160 of 160 |
| Product | identity | text | 160 of 160 |
| Content unit name | identity | text | 160 of 160 |
| What they need to see | identity | text | 160 of 160 |
| Entry source | identity | text | 160 of 160 |
| Slug | identity | text | 160 of 160 |
| Source content unit | identity | text | 122 of 160 |
| Derived from | identity | text | 16 of 160 |
| Amplification | identity | text | 160 of 160 |
| Repurposes into | identity | Formats Key (a list, separated by ", ") | 116 of 160 |
| Also feeds | identity | text | 7 of 160 |
| Source | identity | text | 160 of 160 |
| Content success metrics | identity | text | 160 of 160 |
| State | chosen | Customer States State | 160 of 160 |
| Secondary state | chosen | Customer States State | 21 of 160 |
| Desired response | chosen | text | 160 of 160 |
| Secondary desired response | chosen | text | 0 of 160 |
| Proof needed | chosen | None, Social, Technical, Financial (a list, separated by ", ") | 160 of 160 |
| Format | chosen | Formats Key | 160 of 160 |
| Primary channel | chosen | Channels Key | 160 of 160 |
| Secondary channel | chosen | Channels Key (a list, separated by ", ") | 53 of 160 |
| Secondary ownership | chosen | Owned, Earned, Paid, Shared | 77 of 160 |
| Primary surface | chosen | Surfaces Surface | 160 of 160 |
| Audience | chosen | Audiences Audience (a list, separated by ", ") | 160 of 160 |
| Cadence | chosen | One-shot, Recurring, Always-on | 160 of 160 |
| Primary metric | chosen | Metrics Metric name | 160 of 160 |
| Secondary metric | chosen | Metrics Metric name | 160 of 160 |
| Track | chosen | B2C, B2B | 160 of 160 |
| Recipe | chosen | text | 160 of 160 |
| Tone | chosen | Casual, Formal, Playful | 160 of 160 |
| Aspect ratio | chosen | 16:9, 9:16, 1:1 | 18 of 160 |
| Hashtags | chosen | Required | 19 of 160 |
| Disclaimers | chosen | text | 28 of 160 |

Products: Catalog (160). States: Advocacy (34), Solution-aware (23), Problem-aware (22), Decision (22), Retention (20), Product-aware (16), Unaware (12), Onboarding (6), Purchase (2), Expansion (2), Resurrection (1).

## Full matrix

Every Content Units row with every attribute its chosen values point at, one column group per parent sheet. Row 1 names the group, row 2 is the header. Each derived column is a lookup into its parent (a list lookup for list values, rules for the two computed columns). Each rule in Full matrix `derived` names the parent sheet, the key column of the unit, the column matched in the parent and the column read, with a description.

| Group | Columns | Read from |
|---|---|---|
| Content Units | 20 | Content Units |
| Customer States | 34 | space: Customer States |
| Formats | 16 | space: Formats |
| Channels | 38 | space: Channels |
| Ownership | 26 | space: Ownership |
| Surfaces | 7 | space: Surfaces |
| Audiences | 4 | space: Audiences |
| Metrics | 7 | space: Metrics |

Derived columns: 150 (lookup 147, lookup_list 3).

## Compact matrix

Columns: ID, Content unit name, Format, Primary channel, State, Primary ownership, Primary surface, Lifecycle, Modality, Typical length, Desired response, Primary metric. Each is the Full matrix column of the same name.

## Rules

- Edit Content Units only; `make derive` rebuilds both views, `make check` fails when one is out of date.
- Ownership is not chosen: Primary ownership is the Primary channel's Ownership; Secondary ownership is chosen.
- `make schema` checks that every Full matrix column but ID has a rule and every rule a column, that required columns are filled (ID, State, Desired response, Format, Primary channel, Primary surface, Primary metric, Track, Recipe), that every value is allowed.
- `make coherence` checks every pair of a unit's values against the fit maps: 160 units, 0 pairs not marked.
- Repurposes into names format keys; each pair must be marked in amplify Format transformations, or it shows in its Candidates sheet.

## What reads content units

| Reader | What it takes |
|---|---|
| Content unit ↔ Recipe (this workbook) | the recipe options that produce each unit (94 links) |
| amplify Content unit ↔ Transformation | every format the unit's format transforms into (814 links) |
| amplify Content unit ↔ Repurposing | each Repurposes into and its transformation (232 links) |
| amplify Candidates | Repurposes into pairs not marked in Format transformations |
| compose Template | Content units per state |

## Using the matrix

The matrix is a database, not a document: axes are columns, content units are rows, values are tags, views are filters, an audit is a query, strategy is the balance of the portfolio across axes. Format says what to make, channel where, state why, ownership who controls it, surface exactly where it renders.

| Step | What to do |
|---|---|
| 1. Lock the axes | Use only registry values; nobody invents new ones in a row. |
| 2. One row per unit | Columns are the axes plus strategy and measurement. |
| 3. Tag every unit | One format, one primary channel (secondary optional), one primary state, one surface, one CTA, one metric. |
| 4. Audit for gaps | Formats in only one state; states with one format; channels missing from BOFU or Advocacy; states with the fewest units or the most units and worst metrics; the share of reach that is paid, owned, earned, shared; surfaces with no content or too much. |
| 5. Audit for mismatches | BOFU content on a TOFU surface, TOFU content on a BOFU surface, paid creative on an owned surface, owned content on an earned channel. |
| 6. Map the real path | Instrument the journey: where people enter, loop, skip states, drop off, re-enter. Fix the biggest drop. |
| 7. Build views | Same data, different filters. |
| 8. Review | Weekly: production, status, blockers. Monthly: performance by state, channel, format. Quarterly: portfolio balance, ownership mix, gaps, mismatches. Yearly: retire dead values, add new ones. |

| Mistake | Why it hurts |
|---|---|
| Conflating axes | "Paid social video" is paid + social + video, not a format. |
| Too many values | Nobody tags consistently. |
| No primary | A unit tagged with five states says nothing. |
| No owner, no audit | The tags drift and stop being true. |
| Tool before schema | The tool gets rebuilt once the axes are defined. |
| Waiting for the perfect taxonomy | Ship a first version, iterate. |
| Ignoring surface, ownership or state | Without surface it is vague, without ownership blind to risk, without state misaligned. |
