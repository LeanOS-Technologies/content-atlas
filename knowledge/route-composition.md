# Route composition

A route is a path a person can take through content: a sequence of steps, one per state, where each step hands the person to the next. The worker composes routes over the Steps and Links of a result; the program checks every composed route.

## Link kinds

| Link | Meaning | When it carries a person forward |
|---|---|---|
| Progression | the next step sits at the state's Intended progression (space → Customer States), e.g. Product-aware → Decision | the step's desired response is the entry of the next state, e.g. "read story, compare" → "start trial, contact sales" |
| Transformation: Down / Up / Across | the next step's format is what this step's format becomes (amplify → Format transformations), e.g. Case study → Social post (Down) | the same message is reused in a form the next state consumes |
| Candidate | a format pair not yet marked in Format transformations | allowed in a route, shown as Candidate: the atlas does not yet hold this transformation |

A route may move backwards by transformation (a Decision-stage case study cut down into Unaware posts): that is amplification, the message travelling to people earlier in the journey.

## What makes a route coherent

1. Every step is valid: its pairs are marked in the fit maps (checked by the program).
2. Every link is a Progression or a marked transformation (checked by the program).
3. Each step serves the audience the route is for: the audiences overlap along the route.
4. Each step's proof matches the state: Proof needed (Customer States) rises from None at Unaware to Financial, technical at Decision; a step whose content cannot carry that proof breaks the route there.
5. Friction rises only where the state tolerates it: Friction tolerance Low at Unaware and Purchase, High at Decision.
6. Recipe steps carry their conditions: When, Risk and Time to first result of the recipe (Recipes sheet) apply to the route; a route whose recipe When does not hold for the requester is still returned, with that condition named in Why.

Points 1 and 2 are program checks; points 3 to 6 are the worker's judgment, written in the route's Why.

## Which routes to compose

Compose routes that answer the requirement, starting at the anchors or the existing pieces:
- the shortest forward route from each anchor to the next two states;
- for existing pieces, a route that connects pieces already held, and a route from each piece to the next state using what it can become;
- one amplification route per anchor where a transformation reaches an earlier state.

Every composed route is kept, including those with findings; a finding is reported, not deleted. The worker does not rank routes.
