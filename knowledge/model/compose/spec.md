# Compose spec

Recipes: defined combinations of format, channel and surface for the customer states they serve. Source: `recipes.json`. Output: `recipes.xlsx`, one sheet per customer state, rendered from the JSON. Documents: `template.json` (one row per state) and `examples.json`, each rendered to its `.md`.

110 recipes, 254 options. A recipe is held once and listed on the stage sheet of each of its states (139 sheet rows; 28 recipes sit on more than one sheet).

| Stage sheet | Recipes |
|---|---|
| Unaware | 21 |
| Problem-aware | 26 |
| Solution-aware | 18 |
| Product-aware | 13 |
| Decision | 14 |
| Purchase | 6 |
| Onboarding | 7 |
| Retention | 13 |
| Expansion | 2 |
| Resurrection | 3 |
| Advocacy | 16 |

## Possibilities

For each audience at each customer state where it is present (Audience State Fit): the recipes serving that state for that audience, and every format, channel and surface that fits it. Grade = the weaker of the audience's grade at the state and the value's grade there (Primary, Secondary, Fit), strongest first. Filter State and Audience to read one situation.

Columns: State, Audience, Audience grade, Kind, Value, Grade. 5981 rows, the last sheet of `recipes.xlsx`, built by `make derive`; never edited.

## Recipe

One row per recipe on each stage sheet. Stored = held in `recipes.json`; derived = computed when rendered, never stored.

| Column | JSON field | Kind | Values |
|---|---|---|---|
| Recipe ID | id | stored | pattern `AW-nn` or `AN|B|C-<state code>[-n]`; prefixes C (46), AN (30), B (18), AW (16) |
| Track | track | stored | Any (46), B2C (46), B2B (18) |
| Journey stage | — | derived | Customer States Journey stage of each state, in state order, no repeats |
| State | states | stored | Customer States states, separated by ", " |
| Recipe | name | stored | text |
| Format | kit[].format | stored | Formats key with ID, one per option; options lettered A, B, C … when a recipe has more than one |
| Channel | kit[].channel | stored | Channels key with ID, one per option |
| Ownership | — | derived | Channels Ownership of each option's channel |
| Surface | kit[].surface | stored | Surfaces surface with ID, one per option |
| Audiences | audiences | stored | Audiences (the 16), separated by ", "; Prospect user (67), Prospect champion (46), Prospect buyer (41), Customer user (34), Prospect blocker (26), Customer champion (24), Customer buyer (15), Partner user (2), Partner champion (2), Employee user (1), Employee champion (1) |
| Desired response | desired_response | stored | text |
| CTA | cta | stored | text |
| Direct metrics | metrics.direct | stored | Metrics names with ID, separated by ", " |
| Downstream metrics | metrics.downstream | stored | Metrics names with ID, separated by ", "; empty when no downstream measure is claimed |
| Metric note | metrics.note | stored | text: how to read the metrics (94 recipes) |
| When | when | stored | text: the conditions under which the recipe fits |
| Why it works | why_it_works | stored | text |
| Risk | risk | stored | text |
| How to apply | how_to_apply | stored | text |
| Time to first result | time_to_first_result | stored | Weeks (65), Months (35), Days (10) |
| Source | source | stored | Situation coverage (52), B2C playbook (43), Combining the axes (10), B2B secondary lane (5) |

## Rules

- A recipe option is one format, one channel and one surface. Options are alternatives: running any one of them runs the recipe.
- Ownership is not chosen: it is the option's channel's Ownership in the Channels sheet.
- Journey stage is not chosen: it is the Journey stage of the recipe's states.
- The content units an option produces are listed in place, Content unit ↔ Recipe; compose does not read place.
- Audiences: the audiences present (Audience State Fit) at every one of the recipe's states and reached (Audience Channel Fit) by at least one option's channel.
- Metrics name Metrics registry entries only; anything else about measuring goes in Metric note.
- Source names where the recipe comes from: B2C playbook, Combining the axes, B2B secondary lane, Situation coverage (recipes written to cover customer states and audiences the other sources left empty).
- A recipe's options name channels; whoever plans for a product matches the channels that product can use against them. The atlas holds no product data.
- `make coherence` checks every pair in every option at each of the recipe's states against the fit maps (Format × State, Channel × State, State × Surface, Format × Channel, Format × Surface, Channel × Surface, Audience × State, Audience × Channel, Audience × Format). Current result: 254 options, 0 pairs not marked.
- `make coherence` fails when a marked Audience State Fit cell has no recipe for that audience at that state.
- Recipes never feed the fit maps: no map cell is computed from a recipe.

## Template

`template.json`: one row per customer state, the constraints a state puts on what can be asked and shown. Columns: State, User state, Intent, Trust, Friction tolerance, Proof needed, Attention span, Decision maker, CTA, Format, Channel, Ownership, Surface, Metric, Why this and not that, B2C state, B2B secondary recipe, Recipes defined, Content units, Source.

- Recipes defined and Content units are derived (`make derive`): the recipes on the state's stage sheet, and the content units whose State is the state.
- Format, Channel, Ownership and Surface are descriptions of what fits the state, not registry keys.

## Examples

`examples.json`: worked examples of one topic carried through the states (10 sections). The Recipe column there names a kind of recipe (SEO, Authority, Referral), not a Recipe ID.

## What reads recipes

| Reader | What it takes |
|---|---|
| place Content unit ↔ Recipe | units each option produces (94 links) |
| compose Possibilities (this workbook) | the recipes for each audience at each state where it is present |
| tools/coherence.py | every option pair against the fit maps |
| place Content Units Recipe and Track, tools/assignments.py, tools/audit.py | which recipe each content unit follows; the unit's state must be among the recipe's states and the tracks must match |
| amplify Candidates (transformations.json) | format pairs that are options of the same recipe but not marked in Format transformations |
| tools/derive.py template | Recipes defined per state |

## Using recipes

Combination chain: state → user state → intent → trust → friction tolerance → proof needed → CTA → format → channel → surface. Ownership follows from the channel.

| Step | Action | Detail | Dictates |
|---|---|---|---|
| 1 | Start with the state | Which customer state is the person in? | |
| 2 | Derive the user state | What do they know, feel and want there? (Template: User state) | |
| 3 | Derive the constraints | Intent, trust, friction tolerance, proof needed (Template) | |
| 4 | Pick the CTA that fits the constraints | Ask only for what the state allows | Constraints → CTA |
| 5 | Pick the format that carries the CTA | | CTA → format |
| 6 | Pick the channel where that format lives | Format Channel Fit | Format → channel |
| 7 | Pick the surface where it renders | Format Surface Fit, Channel Surface Fit, State Surface Fit | Format + channel → surface |
| Then | Read the derived values | Ownership from the channel; metrics from the Metrics registry | |

### Picking a recipe (ask in order)

| # | Question | Guide |
|---|---|---|
| 1 | Where is the audience already spending attention? | That eliminates most channels. |
| 2 | What can be afforded? | $0: earned and owned social. Low: owned, earned and small paid tests. High: paid, shared and the rest. |
| 3 | What assets exist already? | A founder who writes: authority, LinkedIn. Video skills: reach. A community: community. A podcast: borrowed trust. None: search content and one social channel. |
| 4 | What is the time horizon? | Days: paid. Weeks: social and PR. Months: search and community. Years: brand and owned audience. Compare with Time to first result. |
| 5 | What is the category? | B2C impulse: reach, interrupt, meme. B2C considered: search, social proof, community. B2B SMB: search, social, community. B2B enterprise: authority, borrowed trust, events, PR. |
| 6 | What is the competition doing? | Crowded: go where they are not. Empty: dominate it. |
| 7 | What can be measured? | Start where the Direct metrics can be measured. |

Before a recipe enters a plan: at least one of its options uses a channel the product can use; at least one of its Audiences is in the plan; its Time to first result fits the product's time horizon. Priority, status and timing belong to the product's plan, not to the recipe.

### Evaluating (after Time to first result, then at 30–60 days)

| # | Question | Check |
|---|---|---|
| 1 | Did it reach the right people? | Audience quality, not only volume |
| 2 | Did they engage? | The Direct metrics |
| 3 | Did it move them to the next state? | The Downstream metrics; a recipe that performs directly but moves no one is not working |
| 4 | What did each outcome cost? | Cost per outcome |
| 5 | What compounded? | Search, owned audience, community |
| 6 | What stopped when spending stopped? | Paid, most social |
| 7 | What to double down on? | Highest signal, lowest cost, most compounding |

### B2C and B2B

| Dimension | B2C | B2B |
|---|---|---|
| Decision maker | One person, fast | Committee, slow |
| Buying trigger | Emotion, impulse, need | Budget, pain, mandate |
| Price sensitivity | High | Lower |
| Trust source | Social proof, reviews, influencers | Case studies, ROI, references |
| Sales cycle | Minutes to days | Weeks to months |
| Sales motion | Self-serve | Sales-assisted |
| Volume | High | Low |
| CAC tolerance | Low | Higher |
| Retention driver | Habit, delight, identity | Contract, integration, ROI |
| Channels | Social | LinkedIn, email, events |

### First steps by budget (B2C)

| Budget | Steps |
|---|---|
| $0 budget, no audience | 1. One short-form video platform. 2. Post 1–3 times a day for 30 days. 3. Search content for problem-aware. 4. Ten reviews from the first customers. 5. An email list from day one. |
| Small ($1–5k a month) | 1. Short-form organic plus a paid boost on the best posts. 2. Search content twice a month. 3. Micro-influencer seeding. 4. Retargeting site visitors. 5. Email flows: welcome, abandoned cart, post-purchase. |
| Larger ($10k+ a month) | 1. Paid social at scale. 2. Influencer program. 3. Search and content engine. 4. PR. 5. Community. 6. Retention and referral programs. |

### B2C priority order

| # | Priority | Why |
|---|---|---|
| 1 | Retention before acquisition | Repeat customers cost less than new ones |
| 2 | Social proof before paid | Reviews and UGC outperform ads |
| 3 | Short-form video before blog | Where attention is |
| 4 | Email before everything | It is owned and it compounds |
| 5 | One channel deep before many shallow | Dominate one |
| 6 | Community before ads at scale | Trust beats reach |
| 7 | Referral before discount | Advocacy costs less than promotion |
