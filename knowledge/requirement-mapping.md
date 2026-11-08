# Requirement mapping

How words in a requirement become atlas values. Used for resolve anchors, map placement and filter params. Every resolved value is an atlas value; a word with no atlas value is reported, never invented.

## States: what the person already knows and is doing

Read the situation of the people the content is for, not the content the requester wants to make. Each state's Question in their head (space → Customer States) is the discriminating cue.

| Cue in the requirement | State | Question in their head |
|---|---|---|
| do not know they have the problem; "reach new people", "get noticed" | Unaware | "Everything's fine?" |
| feel the pain, searching for causes or fixes | Problem-aware | "Why does this hurt?" |
| comparing kinds of solution, building a shortlist | Solution-aware | "What are my options?" |
| know the product, judging fit; "evaluators", "they are looking at us" | Product-aware | "Is this right for me?" |
| choosing now; "comparing us with competitors", "deciding this quarter" | Decision | "Why you, why now?" |
| in checkout, signing | Purchase | "How do I complete this?" |
| just bought, setting up | Onboarding | "How do I start?" |
| using, renewal ahead, churn risk | Retention | "Is this still worth it?" |
| upsell, more seats, add-ons | Expansion | "What else can I do?" |
| churned or dormant, win-back | Resurrection | "Why did I leave?" |
| referrals, reviews, case-study participants | Advocacy | "How do I share this?" |

When the words fit two states, anchor both: anchors only set where routes start.

## Audiences: group × buying role

Audience = group (Prospects, Customers, Partners, Employees) × role (User, Champion, Buyer, Blocker), 16 values. "Buyers" without a group in a sales context means Prospect buyer; after purchase, Customer buyer. "Decision makers", "economic buyer" → Buyer; "the person who uses it" → User; "internal advocate" → Champion; "security, legal, procurement objections" → Blocker. Leave audiences empty when the requirement does not name who.

## Partners and employees: reader or carrier

| Cue in the requirement | Reading | Anchors | Filter param |
|---|---|---|---|
| recruiting, enabling, rewarding partners; affiliates, co-marketing kits, directory listings for partners | partners read the content | Partner user, Partner champion at Advocacy | — |
| collaborators, co-authors, co-hosts, people who help with distribution, resellers | partners carry content to prospects | the prospect audiences at their own states | ownership: Shared; or channels: the Channels whose Audience groups include Partners |
| employees sharing company content | employees read the content | Employee user, Employee champion at Advocacy | — |
| employee advocacy reaching prospects | employees carry content to prospects | the prospect audiences at their own states | ownership: Shared |

The state is always the reader's own. Audience State Fit marks Partners and Employees only where they are the reader.

## Filter params: the focus stated by the requester

| Words | Param |
|---|---|
| owned, earned and shared channels | ownership: Owned, Earned, Shared |
| our own channels | ownership: Owned |
| written and visual formats | formats: the Written / Text and Visual / Static families |
| results within weeks | time_to_first_result: Days, Weeks |
| B2B / sells to businesses | track: B2B |
| strong fits | min_grade: Secondary or Primary |

A focus is a filter param, applied after resolve or map; anchors hold only states and audiences.

## Not mapped

Product names, messages, claims, markets, named partner organisations and budgets in money. They belong to the product; the atlas has no values for them.
