# Run anatomy

The three example requests, traced step by step. Their results are in `artifacts/b2b-decision/`, `artifacts/existing-b2b/` and `artifacts/existing-b2b-owned/`.

## 1. Resolve: b2b-decision

Requirement: "B2B tool. Buyers are comparing us with two competitors and deciding this quarter. What can we do for them?"

| Step | Owner | What happens | Numbers |
|---|---|---|---|
| Model check | program | `python tools/check.py derived` | exit 0 |
| Anchors | AI | "deciding" → Decision (its Question in their head: "Why you, why now?"); "buyers" → Prospect buyer. "This quarter" is kept for a filter (time_to_first_result) | request.json: name, requirement, anchors |
| Anchor steps | program | every recipe option at Decision (one per option) and every content unit at Decision that shares Prospect buyer | 53 steps at depth 0 |
| Breadth-first | program | from each step: Progression to Purchase (the Intended progression of Decision), a transformation or candidate to a step in another state; both ends share an audience; at most 3 links | depth 1: 203, depth 2: 43, depth 3: 4; 303 steps, 18,813 links (Progression 13,956; Transformation 3,167; Candidate 1,690) |
| Atlas rows | program | the space rows, the 11 fit maps, the recipes, Possibilities and content units the steps use | 66 recipes, 3,889 Possibilities rows, 91 content units, 75 formats, 65 channels |
| Compose | AI | 4 routes over Steps and Links, written to routes.json | R-001 S-0177 → S-0228 → S-0014 → S-0244; R-002 S-0197 → S-0016 → S-0245; R-003 S-0213 → S-0020 → S-0244; R-004 S-0199 → S-0038 → S-0244 |
| Check | program | `make check-routes RESULT=artifacts/b2b-decision`: each step's pairs against the fit maps, each link a Progression or a marked transformation | 13 rows, all OK, exit 0 |
| Report | AI | work-result.md | 2 missing inputs (security reviewer in the committee; named contact with an active opportunity), 0 model gaps |

Time: resolve about 23 seconds, check about 25 seconds (most of it writing the 18,813 links to the xlsx).

R-001 read on the Routes sheet:

| Step | Step ID | State | Format | Channel | Link to next |
|---|---|---|---|---|---|
| 1 | S-0177 | Solution-aware | Social Proof / UGC: Reviews | Earned: G2 | Progression: Solution-aware → Product-aware |
| 2 | S-0228 | Product-aware | Written / Text: Case study | Owned: Resource / content hub | Progression: Product-aware → Decision |
| 3 | S-0014 | Decision | Written / Text: Comparison page | Owned: Product pages | Progression: Decision → Purchase |
| 4 | S-0244 | Purchase | Written / Text: Order form | Owned: Sales (1:1) | |

## 2. Map: existing-b2b

Requirement: "B2B tool. We already publish a blog, a newsletter, LinkedIn posts and two case studies. What do we have, and where can it go?"

| Step | Owner | What happens | Numbers |
|---|---|---|---|
| Placement | AI | each piece placed with its basis (knowledge/placement.md) | EX-1 to EX-5 in request.json |
| Placement check | program | each piece's pairs against the fit maps | EX-1 to EX-4 OK; EX-5 (case study on the blog at Unaware): Format × State, Format × Surface, Audience × State (Prospect buyer) not marked |
| Coverage | program | every audience × state where the audience is present, with the pieces there | 46 cells, 7 with a piece; none at Decision or Purchase |
| Breadth-first | program | from the 5 pieces, same rules as resolve | depth 0: 5, depth 1: 252, depth 2: 51; 308 steps, 19,844 links (Progression 14,680; Transformation 3,391; Candidate 1,773) |
| Compose | AI | 4 routes from the pieces | R-001 EX-3 → EX-1 → EX-2 → EX-4; R-002 EX-4 → comparison page → order form; R-003 EX-4 → battle cards; R-004 EX-5 → reference calls |
| Check | program | `make check-routes RESULT=artifacts/existing-b2b` | 11 rows; R-004 step 1 carries EX-5's 3 findings; exit 1 |
| Report | AI | work-result.md | EX-5 classified as no valid construction, owner the requester; 0 model gaps |

Time: map about 24 seconds, check about 25 seconds.

R-004 stays in the result with its findings: a route is shown, not removed.

## 3. Filter: existing-b2b-owned

Params (contracts/examples/owned-secondary.filter.json): ownership Owned, Earned, Shared; track B2B; min_grade Secondary.

| Step | Owner | What happens | Numbers |
|---|---|---|---|
| Translate | AI | focus words to params | the three params above |
| Filter | program | `make filter RESULT=artifacts/existing-b2b PARAMS=contracts/examples/owned-secondary.filter.json`: steps kept by every param, links between kept steps, routes whose every step is kept, then the kept routes checked again | Steps 308 → 105; Links 19,844 → 2,407; Recipes 66 → 25; Possibilities 3,889 → 526; Content units 91 → 23; routes 4 → 2 |
| Verify | program | source possibilities.json hash before and after; kept set recomputed from the source | hashes equal; 105 = 105 |
| Report | AI | work-result.md | R-002 dropped (S-0217 comparison page graded Fit); R-004 dropped (EX-5 has no state grade) |

Time: about 5 seconds.
