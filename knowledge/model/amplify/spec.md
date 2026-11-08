# Amplify spec

Transformations: how the same message moves from one format to another. Source: `transformations.json`. Output: `transformations.xlsx`, rendered from the JSON.

| Sheet | Kind | Rows | Columns |
|---|---|---|---|
| Format transformations | source: authored | 146 source formats | 146 target formats |
| Candidates | view: recomputed by `make derive` | 232 pairs | 5 |
| Content unit ↔ Transformation | view: recomputed by `make derive` | 814 | 6 |
| Content unit ↔ Repurposing | view: recomputed by `make derive` | 232 | 5 |

Content unit ↔ Transformation: Every format a content unit's format transforms into (Down, Up, Across), and the units derived from it in that format.

Content unit ↔ Repurposing: Each format a content unit repurposes into, and the transformation that takes its format there (Down, Up, Across; Same format: a new version in the unit's own format; blank: Format transformations has no such pair, listed in its Candidates sheet).

## Format transformations

Key is the source format, the format columns are the target. Read a row for what a format can become, a column for what it can be built from. Rows and columns follow the Formats sheet; Storyboard and Voiceover are left out (production inputs, listed in combine Format State Fit, Not in the table).

| Marker | Meaning | Example |
|---|---|---|
| Down | into a smaller format: break apart | article → social post, carousel, newsletter |
| Up | into a larger format: build up | social posts → article; articles → ebook |
| Across | into a format of the same size | social post → infographic |

296 pairs marked across 74 formats: 86 Down, 86 Up, 124 Across. Down and Up are one pair seen from its two ends. The marker is the direction the formats' Typical length gives (Short, Medium, Long). A blank means it is not a default transformation.

## Candidates

Format pairs that are not marked in Format transformations but that the other verticals point at. It is a review list: a pair enters Format transformations only when it is marked there by hand, and then leaves Candidates on the next `make derive`.

| Column | Values |
|---|---|
| Source format, Target format | Formats keys |
| Marker | the direction Typical length gives: Down, Up, Across |
| Content units | units whose format repurposes into the target (2 pairs): the matrix contradicts a unit, read these first |
| Recipes | recipes with both formats as options (230 pairs): options are alternatives, so this suggests the pair, it does not prove it |

Markers: Across 132, Down 50, Up 50.

## Rules

- Format transformations is authored; `make derive` never writes it. Candidates is recomputed and never edited.
- A content unit's Repurposes into should be a marked pair. Content unit ↔ Repurposing shows the result per unit: Down 108, Across 84, Up 26, Same format 12, blank 2 (Same format: a new version in the unit's own format).
- Candidates never feed Format transformations.

## What reads transformations

| Reader | What it takes |
|---|---|
| Content unit ↔ Transformation (this workbook) | every format each unit's format transforms into, and the units derived in it (814 links) |
| Content unit ↔ Repurposing (this workbook) | the transformation behind each Repurposes into (232 links) |
