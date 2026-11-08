# Space spec

The axes of the Content Atlas. Source: `space.json`. Output: `space.xlsx`, rendered from the JSON; edits made in the xlsx are overwritten. Styling: `tools/styles.json`.

| Sheet | Rows | Key | ID | Grouped by | Purpose |
|---|---|---|---|---|---|
| Customer States | 11 | State | CS (from CS-01) | Funnel | Where the person is in the journey: 11 customer states from Unaware to Advocacy, with how they think, what they need and how to talk to them. |
| Formats | 148 | Key | FM (from FM-001) | Format family | The shape content takes: 148 formats in 10 families, with modality, length, cost, reuse and the job each does. |
| Channels | 175 | Key | CH (from CH-001) | Channel family | The routes that carry content to a person: 174 channels in 18 families, with ownership, cost, control, reach and measurement. |
| Ownership | 4 | Type | OW (from OW-01) | — | Who controls the route and the audience: Owned, Earned, Paid, Shared. |
| Surfaces | 140 | Surface | SF (from SF-001) | Typical funnel fit | Where the person meets content: 140 surfaces in 11 families, each a place or a slot inside one, with what the person does there. |
| Audiences | 16 | Audience | AU (from AU-01) | Audience group | Who the content is for: 16 audiences, each an audience group in a buying role. |
| Metrics | 117 | Metric name | MET (from MET-001) | — | How a result is measured: 117 metrics, each with definition, counting rule, unit and direction. |

## Rules

- Every row has an ID. IDs are given once, in creation order, and never reused or renumbered; names may change, IDs do not. `make reference` prints the next free ID per prefix.
- The key is unique and is the value every other model uses to point at the row.
- A row sits inside its group; a new row goes into its group, not at the end.
- A list cell separates its values with `, `.
- Every value in a reference column is a key of the referenced sheet.
- Edit `space.json`, then `make build`: derived fit maps, the Full matrix and every view are recomputed, and `make check` fails if any output differs from the JSON.
- `make verify` checks IDs (reference), content-unit values against these sheets (schema) and every pair of values against the fit maps (coherence).

## Customer States

Where the person is in the journey: 11 customer states from Unaware to Advocacy, with how they think, what they need and how to talk to them.

- Key: State
- Grouped by Funnel: TOFU, MOFU, BOFU, Post-purchase
- Read by: combine: every × State fit map (state columns); place: Full matrix Customer States group (by State, Secondary state); compose: recipe states; recipe Journey stage (derived from Journey stage); tools/coherence: unit and recipe-option stages

| Column | Type | Values |
|---|---|---|
| ID | ID, unique |  |
| Journey stage | value | Awareness, Consideration, Decision, Retention, Advocacy |
| Funnel | value | TOFU, MOFU, BOFU, Post-purchase |
| State | key, unique |  |
| Definition | list | Doesn't know they have a problem, Knows the pain, Not the solution, Knows solutions exist, Knows you exist, Ready to choose, Buying, Just bought, Using, Getting value, Churned or dormant, Loves it |
| Mind state | text |  |
| Question in their head | list | "Everything's fine?", "Why does this hurt?", "What are my options?", "Is this right for me?", "Why you, Why now?", "How do I complete this?", "How do I start?", "Is this still worth it?", "What else can I do?", "Why did I leave?", "How do I share this?" |
| Communication objective | value | Reveal the problem, Name and frame the problem, Educate on approaches, Differentiate and prove, Reduce risk, close, Remove friction, Get to first value, Deepen habit and value, Upsell, cross-sell, seats, Win back, Enable referral and voice |
| Communication approach | text |  |
| Suitable formats | text |  |
| Surface | text |  |
| Format families | list | Video, Visual / Static, Paid Creative — cross-format, Written / Text, Audio, Interactive, Experiential / Event, Social Proof / UGC, Conversational / Transactional |
| Channel families | text |  |
| Desired response | text |  |
| Secondary desired response | text | empty in every row |
| Success metrics | text |  |
| Intended progression | list of Customer States State |  |
| Disengagement signals | list | Bounce on first page, No return visit, Gated-form abandonment, Unsubscribes, Abandoned checkout, Stalled deals, Inactivity, Churn, Downgrades, No action after prompt |
| Friction sources | text |  |
| Proof needed | list | None, Social, Technical, Financial |
| Friction tolerance | value | Low, Medium, High |
| Intent | value | Passive, Active, Transactional |
| Awareness level | value | None, Problem, Solution, Product, Vendor |
| Commitment | value | Low, Medium, High |
| Time to act | value | Someday, Soon, Now |
| Decision maker | list of Audiences Buying role | User, Champion, Buyer, Blocker |
| Emotional state | value | Curious, Skeptical, Anxious, Ready |
| Risk level | value | Low, Medium, High |
| Reversibility | value | Easy, Hard, Locked-in |
| Friction | value | Low, Medium, High |
| Stage decay | value | Days, Weeks, Hours, Months |
| Owning team | list | Content / brand marketing, Content marketing, Product marketing, Sales, Revenue operations, Product, Customer success, Lifecycle marketing, Community, Marketing |
| Best ownership mix | text |  |

## Formats

The shape content takes: 148 formats in 10 families, with modality, length, cost, reuse and the job each does.

- Key: Key
- Grouped by Format family: Written / Text, Visual / Static, Audio, Video, Interactive, Conversational / Transactional, Experiential / Event, Social Proof / UGC, Physical / Print, Paid Creative — cross-format
- Key is `Format family: Name`.
- Read by: combine: Format State, Format Ownership, Format Channel, Format Surface, Audience Format fit; place: Full matrix Formats group (by Format); compose: recipe option format; amplify: rows and columns of Format transformations

| Column | Type | Values |
|---|---|---|
| ID | ID, unique |  |
| Name | text |  |
| Format family | value | Written / Text, Visual / Static, Audio, Video, Interactive, Conversational / Transactional, Experiential / Event, Social Proof / UGC, Physical / Print, Paid Creative — cross-format |
| Subformat | value | Long-form, Short-form, Live, Interactive |
| Key | key, unique |  |
| Modality | value | Text, Image, Audio, Video, Interactive |
| Interactivity | value | Passive, Active |
| Typical length | value | Medium, Long, Short |
| Production cost | value | Low, Med, High |
| Reuse | value | Atomizable, Standalone |
| Lifecycle | value | Evergreen, Campaign |
| Job to be done | text |  |
| Best surface | list of Surfaces Surface |  |
| Primary CTA | text |  |
| Funnel stage | value | TOFU, MOFU, BOFU, Retention, Production, Advocacy |
| Success metric | list of Metrics Metric name |  |

## Channels

The routes that carry content to a person: 174 channels in 18 families, with ownership, cost, control, reach and measurement.

- Key: Key
- Grouped by Channel family: Web / Site, App / Product, Email, Messaging, Social, Community, Search, Display / programmatic, Video / audio, Influencer / creator, Sponsorship, Retail media, Press / media, Listings & reviews, Partnerships, Offline / real-world, 1:1, Internal
- Key is `Ownership: Name`, with Shared written `Shared / hybrid`. One row per platform: two platforms are two channels. Audience describes who the channel reaches in its own terms; Audience groups lists the groups of the Audiences sheet it reaches.
- Read by: combine: Channel State, Channel Surface, Format Channel, Audience Channel fit (Audience groups); tools/coherence: Ownership and Secondary ownership as channel × ownership; place: Full matrix Channels group (by Primary channel); compose: recipe option channel; recipe Ownership (derived from Ownership); contract: a request's channels and ownership; tools/query: the cut

| Column | Type | Values |
|---|---|---|
| ID | ID, unique |  |
| Name | text |  |
| Channel family | text |  |
| Key | key, unique |  |
| Ownership | Ownership Type |  |
| Ownership subtype | value | Fully owned, Influenced earned, Peer shared, Leased-owned, Partially owned, Pure earned, Auction paid, Employee shared, Algorithmic earned, Platform shared, Fixed paid, Rented audience, Performance paid, Customer shared |
| Secondary ownership | Ownership Type |  |
| Data access | value | Full, None, Partial |
| Cost type | value | Fixed, Free, Variable, Rev-share |
| Compounding | value | Yes, No |
| Scalability | value | Capped, Sub-linear, Linear |
| Risk | value | Low, Medium, High |
| Trust level | value | Medium, High, Low |
| Speed to activate | value | Months, Weeks, Instant, Days |
| Gatekeeper | value | None, Editor, Partner, Algorithm, Platform |
| Reversibility | value | Easy, Hard |
| Dependency | value | Low, Medium, High |
| Portability | value | Yes, No, Partial |
| Drift risk | value | Low, Medium, High |
| Reach | value | 1:many, 1:1, Many:many |
| Direction | value | Broadcast, Conversational, Peer-to-peer |
| Control | value | Full, None, Partial |
| Persistence | value | Durable, Ephemeral, Permanent |
| Cost model | list | Free, Per message, Per conversation, CPM, CPC, CPA, Flat, Rev-share, Flat (per piece), Headcount |
| Targeting | value | Intent, 1:1, Broad, Account, Interest |
| Speed | value | Evergreen, Scheduled, Instant |
| Measurability | value | Full, Partial, Dark |
| Ownership of audience | value | Yours, Platform's, Shared, None, Creator's, Publisher's |
| Algorithmic? | value | No, Yes |
| Gatekept? | value | No, Yes |
| Bidirectional? | value | No, Yes |
| Channel decay | list | Years, Weeks, Session, Hours, Days, Hours to days, Months, Stops with spend, Days live, Months recorded, Deal cycle, Contract cycle |
| Attribution model | value | Multi-touch, Last-touch, First-touch |
| Audience | text |  |
| Audience groups | list | Prospects, Customers, Partners, Employees |
| Format fit | list | Written, Visual, Video, Interactive, Document, Audio, Live / event, Physical |
| Primary CTA | text |  |
| Funnel stage | list | TOFU, MOFU, BOFU, Retention, Advocacy, Employer brand, All |
| Success metric | list of Metrics Metric name |  |
| Constraints | text |  |
| Vertical | value | Marketing, Product, Customer success, Engineering, HR, PR, Partnerships, Sales, Founder |

## Ownership

Who controls the route and the audience: Owned, Earned, Paid, Shared.

- Key: Type
- Read by: combine: Format Ownership, Ownership State fit; space: Channels Ownership, Secondary ownership; place: Full matrix Ownership group (by Primary ownership, Secondary ownership); compose: recipe Ownership (the channel's, derived)

| Column | Type | Values |
|---|---|---|
| ID | ID, unique |  |
| Type | key, unique |  |
| Definition | list | You control the channel, The rules, The audience relationship, And the data., You don't control the channel. You earn placement through merit, Relationships, Or newsworthiness., You pay for placement, Reach, Or audience access. You rent the channel., Co-controlled. You and another party both have a stake. |
| You control | list | Channel, Rules, Data, Nothing; you influence, Placement only, Partially |
| Audience belongs to | value | You, Third party, Platform, Shared |
| Risk | value | Low, High, Medium |
| Cost model | value | Fixed / team, PR / effort, Variable / CPM, Negotiated |
| Example | list | Blog, Email list, App, Press, Reviews, Shares, Ads, Sponsorships, Co-marketing, Partners |
| Characteristics | text |  |
| Examples | text |  |
| Strengths | text |  |
| Weaknesses | text |  |
| Subtypes | text |  |
| Key risk | list | Platform dependency. You “own” your YouTube channel until YouTube changes the algorithm or bans you., You can't turn it on. You can only make it more likely., You're renting. Stop paying, Stop reaching., Partner owns the relationship more than you do. |
| Portfolio role | value | Moat and compounding, Trust and credibility, Speed and scale, Leverage and reach |
| Team | list | Content, SEO, Lifecycle, Community, PR, Comms, Growth, Performance, Media, Partnerships, BD, Advocacy |
| Key point | value | Owned compounds., Earned persuades., Paid scales., Shared leverages. |
| Trust | value | Medium, High, Low–medium, Medium–high |
| Speed | value | Slow, Instant, Medium |
| Scale | value | Capped, Unpredictable, Linear with spend, Partner-capped |
| Compounding | value | Yes, Some, No |
| Data access | value | Full, None, Partial |
| Moat | value | Strong, Weak, None, Medium |
| Risk type | value | Platform, Reputation, Cost, Partner |

## Surfaces

Where the person meets content: 140 surfaces in 11 families, each a place or a slot inside one, with what the person does there.

- Key: Surface
- Grouped by Typical funnel fit: TOFU, MOFU, BOFU, Post-purchase, Any
- A surface is a place or a slot, never a format or a platform. Contained in names a surface in this sheet.
- Read by: combine: Format Surface, Channel Surface, State Surface fit; place: Full matrix Surfaces group (by Primary surface); compose: recipe option surface; space: Formats Best surface, Surfaces Contained in

| Column | Type | Values |
|---|---|---|
| ID | ID, unique |  |
| Surface | key, unique |  |
| Surface family | value | Media, Live, Website, Email, Social feed, Search, Physical, Document, Product, Notifications, Messaging |
| Level | value | Slot, Place |
| Contained in | Surfaces Surface |  |
| What the person does | value | listen, attend, read, watch, fill in, use, scroll, search, see, pay, review, glance, study, converse |
| Typical funnel fit | value | TOFU, MOFU, BOFU, Post-purchase, Any |

## Audiences

Who the content is for: 16 audiences, each an audience group in a buying role.

- Key: Audience
- Grouped by Audience group: Prospects, Customers, Partners, Employees
- Audience is `<group, singular> <role, lower case>`; every group × role pair has a row.
- Read by: combine: Audience State, Audience Format, Audience Channel fit; place: Full matrix Audiences group (by Audience, a list); compose: recipe Audiences

| Column | Type | Values |
|---|---|---|
| ID | ID, unique |  |
| Audience | key, unique |  |
| Audience group | value | Prospects, Customers, Partners, Employees |
| Buying role | value | User, Champion, Buyer, Blocker |
| Definition | text |  |

## Metrics

How a result is measured: 117 metrics, each with definition, counting rule, unit and direction.

- Key: Metric name
- Metric name is the value Content Units use in Primary metric and Secondary metric.
- Read by: place: Full matrix Metrics group (by Primary metric, Secondary metric); space: Formats and Channels Success metric; compose: recipe Direct metrics, Downstream metrics

| Column | Type | Values |
|---|---|---|
| Metric ID | ID, unique |  |
| Metric name | key, unique |  |
| Definition | text |  |
| Calculation / counting rule | text |  |
| Unit | value | Count, %, Percentage points, Duration, Currency, Ratio, % by period, Score (−100 to 100), Score, Position |
| Direction | value | Higher is better, Context-dependent, Lower is better |
