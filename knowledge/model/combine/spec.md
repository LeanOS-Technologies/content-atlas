# Combine spec

Fit maps: which pairs of space values work together. Source: `fit-maps.json`. Output: `fit-maps.xlsx`, rendered from the JSON. The derived maps read only the source maps and columns of the space; there is no other rule file.

A fit map pairs two space sheets: one runs down the rows (the Key column), the other across the columns. A cell says how the pair fits; a blank cell means the pair is not a default recommendation.

| Map | Rows | Columns | Cell values | Kind | Rows × columns | Marked cells |
|---|---|---|---|---|---|---|
| Format State Fit | Formats | Customer States | Primary, Fit | source | 146 × 11 | 563 |
| Format Ownership Fit | Formats | Ownership | free text (347 distinct) | source | 146 × 4 | 397 |
| Channel State Fit | Channels | Customer States | Secondary, Primary | source | 174 × 11 | 637 |
| Ownership State Fit | Ownership | Customer States | free text (30 distinct) | source | 4 × 11 | 36 |
| Format Channel Fit | Formats | Channels | Fit, Primary, Secondary | derived | 146 × 174 | 3442 |
| Format Surface Fit | Formats | Surfaces | Fit, Primary | source | 146 × 140 | 824 |
| Channel Surface Fit | Channels | Surfaces | Fit | source | 174 × 140 | 1076 |
| State Surface Fit | Surfaces | Customer States | Secondary, Fit, Primary | derived | 140 × 11 | 842 |
| Audience State Fit | Audiences | Customer States | Primary, Fit | source | 16 × 11 | 31 |
| Audience Format Fit | Audiences | Formats | Primary, Fit | derived | 16 × 146 | 801 |
| Audience Channel Fit | Audiences | Channels | Secondary, Primary, Fit | derived | 16 × 174 | 748 |

## Rules

- Source maps are authored; `make derive` never writes them.
- Derived maps are recomputed by `make derive` from the source maps and space columns (Customer States Funnel and Surface, Surfaces Typical funnel fit, Channels Ownership, Secondary ownership and Audience groups); edits to a derived map are overwritten.
- Rows and columns follow the order of their space sheet; a key in a map is a key of that sheet.
- `make coherence` looks up each pair of values in a content unit or a recipe option in the map that pairs them. Ownership is not chosen (it is the channel's), so Format Ownership Fit acts only inside Format Channel Fit, and Ownership State Fit holds tactics to read, not a test.
- `make coherence` also reads Audience State Fit the other way: every marked cell is served by at least one recipe whose states and audiences include it; a cell no recipe serves fails the check.
- No map is fed by content units or recipes: every derived cell traces to cells of the source maps and to columns of the space.
- Grades: Primary (central), Secondary (supports), Fit (possible). A derived cell is as strong as the weakest cell it is composed from, along its strongest path.
- Channel × ownership is not a map: each channel's Ownership and Secondary ownership in the Channels sheet are its Primary and Secondary ownership, and coherence reads them there.

## Format State Fit

Which formats suit each customer state. Key is the Formats key and the state columns are the Customer States states. Primary = a state within the format's own Funnel stage (Formats sheet: TOFU = Unaware, Problem-aware; MOFU = Solution-aware, Product-aware; BOFU = Decision, Purchase; Retention = Onboarding through Resurrection; Advocacy = Advocacy). Fit = a further common, practical use of the format at the state. A blank means it is not a default recommendation.

- Rows: Formats (146), Key column; also shown: Format, Format family
- Columns: Customer States (11)
- Cell: Primary, Fit; 563 marked
- Kind: source
- Feeds: Format Channel Fit, Audience Format Fit
- Read by: coherence (Format × State); compose Possibilities
- Section "Not in the table": 4 rows

## Format Ownership Fit

How each format is published or delivered under each ownership type. A cell gives a short delivery example; a blank means the format is not generally used that way. Ownership follows the Ownership registry: Owned is a channel you control, Earned is placement won through merit, relationships or newsworthiness (including an accepted guest post), Paid is rented placement, and Shared is co-controlled with a partner, platform, employee or customer. Paid promotion of an owned asset does not change that asset’s ownership: the advertisement is the Paid content unit. Fit depends on what the content communicates; choosing the format alone does not establish fit.

- Rows: Formats (146), Key column; also shown: Format, Format family
- Columns: Ownership (4)
- Cell: free text (347 distinct); 397 marked
- Kind: source
- Feeds: Format Channel Fit
- Read by: derive, inside Format Channel Fit; no check of its own
- Section "Not in the table": 2 rows

## Channel State Fit

Which channels support each customer state. Primary = a commonly central channel for completing the stage’s task, not a claim that it is the best channel for every business. Secondary = it supports the stage; its presence alone does not make it central. A blank means it is not generally recommended for that stage. Every channel has been assessed individually against what the audience needs to do at each stage. Fit depends on what the content communicates; choosing the channel alone does not establish fit.

- Rows: Channels (174), Key column; also shown: Channel, Channel family
- Columns: Customer States (11)
- Cell: Secondary, Primary; 637 marked
- Kind: source
- Feeds: Format Channel Fit, State Surface Fit, Audience Channel Fit
- Read by: coherence (Channel × State); compose Possibilities
- Section "Not in the table": 1 rows

## Ownership State Fit

Typical tactics for each ownership type at each customer state. A blank means no tactic is generally recommended for that ownership type at that stage. Tactics depend on what the content communicates; choosing an ownership type alone does not establish fit.

- Rows: Ownership (4), Key column; also shown: —
- Columns: Customer States (11)
- Cell: free text (30 distinct); 36 marked
- Kind: source
- Read by: people: the tactics per ownership type and state; no check

## Format Channel Fit

Which formats travel on which channels. Key is the Formats key; the channel columns are the Channels keys. A cell is marked when some surface is marked for both in Format Surface Fit and Channel Surface Fit, both fit a common state (Format State Fit, Channel State Fit), and the format has a delivery (Format Ownership Fit) under the channel's Ownership or Secondary ownership. Grade = the weaker of the format's grade on the strongest shared surface and the strongest shared state (the weaker of the format's and the channel's grade there). A blank means it is not a default recommendation.

- Rows: Formats (146), Key column; also shown: Format, Format family
- Columns: Channels (174)
- Cell: Fit, Primary, Secondary; 3442 marked
- Kind: derived
- Read by: coherence (Format × Channel)

## Format Surface Fit

Which surfaces a format can render on. Key is the Formats key; the surface columns are the Surfaces registry. Primary = the format's Best surface (Formats sheet). Fit = a further surface the format commonly renders on. A blank means it is not a default recommendation. Source map.

- Rows: Formats (146), Key column; also shown: Format, Format family
- Columns: Surfaces (140)
- Cell: Fit, Primary; 824 marked
- Kind: source
- Feeds: Format Channel Fit
- Read by: coherence (Format × Surface)

## Channel Surface Fit

Which surfaces each channel puts content on. Key is the Channels key; the surface columns are the Surfaces registry. Fit marks a surface the channel commonly delivers to. A blank means it is not a default recommendation. Source map.

- Rows: Channels (174), Key column; also shown: Channel, Channel family
- Columns: Surfaces (140)
- Cell: Fit; 1076 marked
- Kind: source
- Feeds: Format Channel Fit, State Surface Fit
- Read by: coherence (Channel × Surface)

## State Surface Fit

Which surfaces are appropriate at each customer state. Key is the Surfaces registry name and the state columns are the Customer States states. Primary = Customer States names the surface for the state. Secondary = the state is in the surface's Typical funnel fit (TOFU = Unaware, Problem-aware; MOFU = Solution-aware, Product-aware; BOFU = Decision, Purchase; Post-purchase = Onboarding through Advocacy; Any = every state). Fit = a channel that is Primary at the state (Channel State Fit) reaches the surface (Channel Surface Fit). A blank means it is not a default recommendation.

- Rows: Surfaces (140), Key column; also shown: Surface family, Typical funnel fit
- Columns: Customer States (11)
- Cell: Secondary, Fit, Primary; 842 marked
- Kind: derived
- Read by: coherence (State × Surface); compose Possibilities

## Audience State Fit

Fit by audience: an audience group in a buying role. Key is the Audiences registry name and the state columns are the Customer States states. The audience is the reader of content at the state, and the state is that reader's own. Primary = the audience is present and its buying role decides at the state (Customer States Decision maker). Fit = present and involved. A group that carries content to another group's reader (a partner co-hosting or distributing, an employee sharing) is not marked here: Channels Audience groups and Ownership Shared hold it. A blank means it is not a default recommendation. Source map.

- Rows: Audiences (16), Key column; also shown: Audience group, Buying role
- Columns: Customer States (11)
- Cell: Primary, Fit; 31 marked
- Kind: source
- Feeds: Audience Format Fit, Audience Channel Fit
- Read by: coherence (Audience × State); compose Possibilities

## Audience Format Fit

Fit by audience: an audience group in a buying role. Key is the Audiences registry name; the format columns are the Formats keys. A cell is marked when the format fits a state where the audience is present (Format State Fit, Audience State Fit). Grade = the weaker of the two cells at the strongest shared state. A blank means it is not a default recommendation.

- Rows: Audiences (16), Key column; also shown: Audience group, Buying role
- Columns: Formats (146)
- Cell: Primary, Fit; 801 marked
- Kind: derived
- Read by: coherence (Audience × Format)

## Audience Channel Fit

Fit by audience: an audience group in a buying role. Key is the Audiences registry name; the channel columns are the Channels keys. A cell is marked when the channel fits a state where the audience is present (Channel State Fit, Audience State Fit) and the channel reaches the audience group (Channels: Audience groups). Grade = the weaker of the two cells at the strongest shared state. A blank means it is not a default recommendation.

- Rows: Audiences (16), Key column; also shown: Audience group, Buying role
- Columns: Channels (174)
- Cell: Secondary, Primary, Fit; 748 marked
- Kind: derived
- Read by: coherence (Audience × Channel); compose Possibilities
