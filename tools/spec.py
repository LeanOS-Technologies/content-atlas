"""Write the spec of each vertical from its current JSON: knowledge/model/<vertical>/spec.md.

    python tools/spec.py          write every spec
Counts, values and readers are read from the models, so a spec is current whenever `make build` has run;
`make check` fails when a spec differs from what its JSON gives.
"""
import collections
import json
import re
import sys
from collections import Counter
from pathlib import Path

import models

ROOT = models.ROOT
C = Counter


def enumerate_spec():
    OUT = {}
    sp = json.load(open(ROOT / "knowledge/model/enumerate/space.json")); sh = {s["name"]: s for s in sp["sheets"]}
    st = json.load(open(ROOT / "tools/styles.json"))["space"]
    ref = {p["sheet"]: p for p in json.load(open(ROOT / "tools/reference.json"))["prefixes"] if p.get("sheet")}
    KEY = {"Customer States": "State", "Formats": "Key", "Channels": "Key", "Ownership": "Type", "Surfaces": "Surface", "Audiences": "Audience", "Metrics": "Metric name"}
    PURPOSE = {
     "Customer States": "Where the person is in the journey: 11 customer states from Unaware to Advocacy, with how they think, what they need and how to talk to them.",
     "Formats": "The shape content takes: 148 formats in 10 families, with modality, length, cost, reuse and the job each does.",
     "Channels": "The routes that carry content to a person: 174 channels in 18 families, with ownership, cost, control, reach and measurement.",
     "Ownership": "Who controls the route and the audience: Owned, Earned, Paid, Shared.",
     "Surfaces": "Where the person meets content: 140 surfaces in 11 families, each a place or a slot inside one, with what the person does there.",
     "Audiences": "Who the content is for: 16 audiences, each an audience group in a buying role.",
     "Metrics": "How a result is measured: 117 metrics, each with definition, counting rule, unit and direction.",
    }
    READ_BY = {
     "Customer States": ["combine: every × State fit map (state columns)", "place: Full matrix Customer States group (by State, Secondary state)", "compose: recipe states; recipe Journey stage (derived from Journey stage)", "tools/coherence: unit and recipe-option stages"],
     "Formats": ["combine: Format State, Format Ownership, Format Channel, Format Surface, Audience Format fit", "place: Full matrix Formats group (by Format)", "compose: recipe option format", "amplify: rows and columns of Format transformations"],
     "Channels": ["combine: Channel State, Channel Surface, Format Channel, Audience Channel fit (Audience groups); tools/coherence: Ownership and Secondary ownership as channel × ownership", "place: Full matrix Channels group (by Primary channel)", "compose: recipe option channel; recipe Ownership (derived from Ownership)", "contract: a request's channels and ownership; tools/query: the cut"],
     "Ownership": ["combine: Format Ownership, Ownership State fit; space: Channels Ownership, Secondary ownership", "place: Full matrix Ownership group (by Primary ownership, Secondary ownership)", "compose: recipe Ownership (the channel's, derived)"],
     "Surfaces": ["combine: Format Surface, Channel Surface, State Surface fit", "place: Full matrix Surfaces group (by Primary surface)", "compose: recipe option surface", "space: Formats Best surface, Surfaces Contained in"],
     "Audiences": ["combine: Audience State, Audience Format, Audience Channel fit", "place: Full matrix Audiences group (by Audience, a list)", "compose: recipe Audiences"],
     "Metrics": ["place: Full matrix Metrics group (by Primary metric, Secondary metric)", "space: Formats and Channels Success metric", "compose: recipe Direct metrics, Downstream metrics"],
    }
    EDIT = {
     "Formats": "Key is `Format family: Name`.",
     "Channels": "Key is `Ownership: Name`, with Shared written `Shared / hybrid`. One row per platform: two platforms are two channels. Audience describes who the channel reaches in its own terms; Audience groups lists the groups of the Audiences sheet it reaches.",
     "Surfaces": "A surface is a place or a slot, never a format or a platform. Contained in names a surface in this sheet.",
     "Audiences": "Audience is `<group, singular> <role, lower case>`; every group × role pair has a row.",
     "Metrics": "Metric name is the value Content Units use in Primary metric and Secondary metric.",
    }
    keys = {n: {r[KEY[n]] for r in sh[n]["rows"]} for n in KEY}
    def coltype(n, c):
        rows = sh[n]["rows"]; ne = [r.get(c) for r in rows if r.get(c) not in (None, "")]
        if c == KEY[n]: return "key, unique", ""
        if c in ("ID", "Metric ID"): return "ID, unique", ""
        if not ne: return "text", "empty in every row"
        items = [x.strip() for v in ne for x in str(v).split(",")]
        for m, ks in keys.items():
            if sum(1 for x in items if x in ks) / len(items) > 0.8:
                multi = any("," in str(v) for v in ne)
                return ("list of " if multi else "") + f"{m} {KEY[m]}", ""
        dist = Counter(str(v) for v in ne)
        if any("," in str(v) for v in ne) and len({x.lower() for x in items}) <= 12:
            vals = list(dict.fromkeys(x[0].upper() + x[1:] for x in items))
            if c == "Decision maker":
                return "list of Audiences Buying role", ", ".join(vals)
            return "list", ", ".join(vals)
        if len(dist) <= 14 and all(len(v) <= 30 for v in dist): return "value", ", ".join(dist)
        return "text", ""
    L = ["# Space spec", "",
         "The axes of the Content Atlas. Source: `space.json`. Output: `space.xlsx`, rendered from the JSON; edits made in the xlsx are overwritten. Styling: `tools/styles.json`.", "",
         "| Sheet | Rows | Key | ID | Grouped by | Purpose |", "|---|---|---|---|---|---|"]
    for n in sh:
        p = ref.get(n)
        L.append(f"| {n} | {len(sh[n]['rows'])} | {KEY[n]} | {p['prefix'] + ' (from ' + p['first_id'] + ')'} | {st[n].get('by') or '—'} | {PURPOSE[n]} |")
    L += ["", "## Rules", "",
          "- Every row has an ID. IDs are given once, in creation order, and never reused or renumbered; names may change, IDs do not. `make reference` prints the next free ID per prefix.",
          "- The key is unique and is the value every other model uses to point at the row.",
          "- A row sits inside its group; a new row goes into its group, not at the end.",
          "- A list cell separates its values with `, `.",
          "- Every value in a reference column is a key of the referenced sheet.",
          "- Edit `space.json`, then `make build`: derived fit maps, the Full matrix and every view are recomputed, and `make check` fails if any output differs from the JSON.",
          "- `make verify` checks IDs (reference), content-unit values against these sheets (schema) and every pair of values against the fit maps (coherence).", ""]
    for n, s in sh.items():
        L += [f"## {n}", "", PURPOSE[n], "", f"- Key: {KEY[n]}"]
        if st[n].get("by"):
            L.append(f"- Grouped by {st[n]['by']}: {', '.join(dict.fromkeys(r[st[n]['by']] for r in s['rows']))}")
        if EDIT.get(n): L.append(f"- {EDIT[n]}")
        L.append("- Read by: " + "; ".join(READ_BY[n]))
        L += ["", "| Column | Type | Values |", "|---|---|---|"]
        for c in [c for c in s["columns"] if c]:
            t, v = coltype(n, c)
            L.append(f"| {c} | {t} | {v} |")
        L.append("")
    OUT["knowledge/model/enumerate/spec.md"] = "\n".join(L)
    return OUT


def combine_spec():
    OUT = {}
    fm = json.load(open(ROOT / "knowledge/model/combine/fit-maps.json"))["sheets"]
    SOURCE = ["Format State Fit", "Format Ownership Fit", "Channel State Fit", "Ownership State Fit", "Format Surface Fit", "Channel Surface Fit", "Audience State Fit"]
    AXES = {"Format State Fit": ("Formats", "Customer States"), "Format Ownership Fit": ("Formats", "Ownership"), "Channel State Fit": ("Channels", "Customer States"),
            "Ownership State Fit": ("Ownership", "Customer States"), "Format Channel Fit": ("Formats", "Channels"),         "Format Surface Fit": ("Formats", "Surfaces"), "Channel Surface Fit": ("Channels", "Surfaces"), "State Surface Fit": ("Surfaces", "Customer States"),
            "Audience State Fit": ("Audiences", "Customer States"), "Audience Format Fit": ("Audiences", "Formats"), "Audience Channel Fit": ("Audiences", "Channels")}
    FEEDS = {"Format State Fit": ["Format Channel Fit", "Audience Format Fit"], "Channel State Fit": ["Format Channel Fit", "State Surface Fit", "Audience Channel Fit"],
             "Format Ownership Fit": ["Format Channel Fit"], "Ownership State Fit": [], "Format Surface Fit": ["Format Channel Fit"],
             "Channel Surface Fit": ["Format Channel Fit", "State Surface Fit"], "Audience State Fit": ["Audience Format Fit", "Audience Channel Fit"],
             "Format Channel Fit": [], "State Surface Fit": [], "Audience Format Fit": [], "Audience Channel Fit": []}
    LINKS = {"Format State Fit", "Channel State Fit", "State Surface Fit", "Audience State Fit", "Audience Channel Fit"}
    COH = {"Format State Fit": "Format × State", "Format Ownership Fit": "Format × Ownership", "Format Channel Fit": "Format × Channel", "Format Surface Fit": "Format × Surface",
           "Channel State Fit": "Channel × State", "Channel Surface Fit": "Channel × Surface",
           "Ownership State Fit": "Ownership × State", "State Surface Fit": "State × Surface", "Audience State Fit": "Audience × State",
           "Audience Format Fit": "Audience × Format", "Audience Channel Fit": "Audience × Channel"}
    FED = set()
    L = ["# Combine spec", "",
         "Fit maps: which pairs of space values work together. Source: `fit-maps.json`. Output: `fit-maps.xlsx`, rendered from the JSON. The derived maps read only the source maps and columns of the space; there is no other rule file.", "",
         "A fit map pairs two space sheets: one runs down the rows (the Key column), the other across the columns. A cell says how the pair fits; a blank cell means the pair is not a default recommendation.", "",
         "| Map | Rows | Columns | Cell values | Kind | Rows × columns | Marked cells |", "|---|---|---|---|---|---|---|"]
    info = {}
    for s in fm:
        lead = [c for c in s["columns"] if c in ("Key", "Format", "Format family", "Channel", "Channel family", "Surface family", "Typical funnel fit", "Audience group", "Buying role", "Classification")]
        cols = [c for c in s["columns"] if c and c not in lead]
        cells = [r.get(c) for r in s["rows"] for c in cols if r.get(c) not in (None, "")]
        dist = Counter(cells)
        vals = ", ".join(dist) if len(dist) <= 4 else f"free text ({len(dist)} distinct)"
        kind = "source" if s["name"] in SOURCE else "derived"
        info[s["name"]] = (lead, cols, vals, kind, len(cells))
        a, b = AXES[s["name"]]
        L.append(f"| {s['name']} | {a} | {b} | {vals} | {kind} | {len(s['rows'])} × {len(cols)} | {len(cells)} |")
    L += ["", "## Rules", "",
          "- Source maps are authored; `make derive` never writes them.",
          "- Derived maps are recomputed by `make derive` from the source maps and space columns (Customer States Funnel and Surface, Surfaces Typical funnel fit, Channels Ownership, Secondary ownership and Audience groups); edits to a derived map are overwritten.",
          "- Rows and columns follow the order of their space sheet; a key in a map is a key of that sheet.",
          "- `make coherence` looks up each pair of values in a content unit or a recipe option in the map that pairs them. Ownership is not chosen (it is the channel's), so Format Ownership Fit acts only inside Format Channel Fit, and Ownership State Fit holds tactics to read, not a test.",
          "- `make coherence` also reads Audience State Fit the other way: every marked cell is served by at least one recipe whose states and audiences include it; a cell no recipe serves fails the check.",
          "- No map is fed by content units or recipes: every derived cell traces to cells of the source maps and to columns of the space.",
          "- Grades: Primary (central), Secondary (supports), Fit (possible). A derived cell is as strong as the weakest cell it is composed from, along its strongest path.",
          "- Channel × ownership is not a map: each channel's Ownership and Secondary ownership in the Channels sheet are its Primary and Secondary ownership, and coherence reads them there.", ""]
    for s in fm:
        lead, cols, vals, kind, marked = info[s["name"]]
        a, b = AXES[s["name"]]
        L += [f"## {s['name']}{' *' if s['name'] in FED else ''}", "", s["description"], "",
              f"- Rows: {a} ({len(s['rows'])}), Key column; also shown: {', '.join(c for c in lead if c != 'Key') or '—'}",
              f"- Columns: {b} ({len(cols)})",
              f"- Cell: {vals}; {marked} marked",
              f"- Kind: {kind}"]
        if FEEDS[s["name"]]: L.append(f"- Feeds: {', '.join(FEEDS[s['name']])}")
        reads = ([f"coherence ({COH[s['name']]})"] if s["name"] not in ("Format Ownership Fit", "Ownership State Fit") else []) + (["compose Possibilities"] if s["name"] in LINKS else [])
        none = {"Format Ownership Fit": "derive, inside Format Channel Fit; no check of its own", "Ownership State Fit": "people: the tactics per ownership type and state; no check"}
        L.append(f"- Read by: {'; '.join(reads) or none[s['name']]}")
        for sec in s.get("sections", []):
            L.append(f"- Section \"{sec['title']}\": {len(sec['rows'])} rows")
        L.append("")
    OUT["knowledge/model/combine/spec.md"] = "\n".join(L)
    return OUT


def compose_spec():
    OUT = {}



    doc = models.read("recipes")
    R = models.recipes(doc)
    t = json.loads((ROOT / "knowledge/model/compose/template.json").read_text())
    ex = json.loads((ROOT / "knowledge/model/compose/examples.json").read_text())
    links = {s["name"]: s for k in ("place", "transformations", "recipes") for s in models.read(k).get("sheets", [])}
    rows = [models.recipe_row(p) for p in R]
    C = collections.Counter
    opts = sum(len(p["kit"]) for p in R)


    def vals(c):
        v = C(p for p in c if p is not None)
        return ", ".join(f"{k} ({n})" for k, n in v.most_common())


    prefix = C(p["id"].split("-")[0] for p in R)
    out = ["# Compose spec", "",
           "Recipes: defined combinations of format, channel and surface for the customer states they serve. "
           "Source: `recipes.json`. Output: `recipes.xlsx`, one sheet per customer state, rendered from the JSON. "
           "Documents: `template.json` (one row per state) and `examples.json`, each rendered to its `.md`.", "",
           f"{len(R)} recipes, {opts} options. A recipe is held once and listed on the stage sheet of each of its states "
           f"({sum(len(st['recipes']) for st in doc['stages'])} sheet rows; "
           f"{sum(1 for p in R if len(p['states']) > 1)} recipes sit on more than one sheet).", "",
           "| Stage sheet | Recipes |", "|---|---|"]
    out += [f"| {st['stage']} | {len(st['recipes'])} |" for st in doc["stages"]]
    V = links
    out += ["", "## Possibilities", "", V["Possibilities"]["description"], "",
            "Columns: " + ", ".join(V["Possibilities"]["columns"]) + f". {len(V['Possibilities']['rows'])} rows, the last sheet of "
            "`recipes.xlsx`, built by `make derive`; never edited."]
    out += ["", "## Recipe", "",
            "One row per recipe on each stage sheet. Stored = held in `recipes.json`; derived = computed when rendered, never stored.", "",
            "| Column | JSON field | Kind | Values |", "|---|---|---|---|"]
    FIELD = {
        "Recipe ID": ("id", "stored", f"pattern `AW-nn` or `AN|B|C-<state code>[-n]`; prefixes " + ", ".join(f"{k} ({n})" for k, n in prefix.most_common())),
        "Track": ("track", "stored", vals(p["track"] for p in R)),
        "Journey stage": ("—", "derived", "Customer States Journey stage of each state, in state order, no repeats"),
        "State": ("states", "stored", "Customer States states, separated by \", \""),
        "Recipe": ("name", "stored", "text"),
        "Format": ("kit[].format", "stored", "Formats key with ID, one per option; options lettered A, B, C … when a recipe has more than one"),
        "Channel": ("kit[].channel", "stored", "Channels key with ID, one per option"),
        "Ownership": ("—", "derived", "Channels Ownership of each option's channel"),
        "Surface": ("kit[].surface", "stored", "Surfaces surface with ID, one per option"),
        "Audiences": ("audiences", "stored", "Audiences (the 16), separated by \", \"; " + vals(a["name"] for p in R for a in p["audiences"])),
        "Desired response": ("desired_response", "stored", "text"),
        "CTA": ("cta", "stored", "text"),
        "Direct metrics": ("metrics.direct", "stored", "Metrics names with ID, separated by \", \""),
        "Downstream metrics": ("metrics.downstream", "stored", "Metrics names with ID, separated by \", \"; empty when no downstream measure is claimed"),
        "Metric note": ("metrics.note", "stored", f"text: how to read the metrics ({sum(1 for p in R if p['metrics']['note'])} recipes)"),
        "When": ("when", "stored", "text: the conditions under which the recipe fits"),
        "Why it works": ("why_it_works", "stored", "text"),
        "Risk": ("risk", "stored", "text"),
        "How to apply": ("how_to_apply", "stored", "text"),
        "Time to first result": ("time_to_first_result", "stored", vals(p["time_to_first_result"] for p in R)),
        "Source": ("source", "stored", vals(p["source"] for p in R)),
    }
    assert list(FIELD) == doc["stage_columns"], set(FIELD) ^ set(doc["stage_columns"])
    out += [f"| {c} | {f} | {k} | {v} |" for c, (f, k, v) in FIELD.items()]
    out += ["", "## Rules", "",
            "- A recipe option is one format, one channel and one surface. Options are alternatives: running any one of them runs the recipe.",
            "- Ownership is not chosen: it is the option's channel's Ownership in the Channels sheet.",
            "- Journey stage is not chosen: it is the Journey stage of the recipe's states.",
            "- The content units an option produces are listed in place, Content unit ↔ Recipe; compose does not read place.",
            "- Audiences: the audiences present (Audience State Fit) at every one of the recipe's states and reached (Audience Channel Fit) "
            "by at least one option's channel.",
            "- Metrics name Metrics registry entries only; anything else about measuring goes in Metric note.",
            "- Source names where the recipe comes from: B2C playbook, Combining the axes, B2B secondary lane, Situation coverage "
            "(recipes written to cover customer states and audiences the other sources left empty).",
            "- A recipe's options name channels; whoever plans for a product matches the channels that product can use against them. The atlas holds no product data.",
            f"- `make coherence` checks every pair in every option at each of the recipe's states against the fit maps "
            f"(Format × State, Channel × State, State × Surface, Format × Channel, Format × Surface, Channel × Surface, Audience × State, "
            f"Audience × Channel, Audience × Format). Current result: {opts} options, 0 pairs not marked.",
            "- `make coherence` fails when a marked Audience State Fit cell has no recipe for that audience at that state.",
            "- Recipes never feed the fit maps: no map cell is computed from a recipe.", "",
            "## Template", "",
            f"`template.json`: one row per customer state, the constraints a state puts on what can be asked and shown. "
            f"Columns: {', '.join(t['columns'])}.", "",
            "- Recipes defined and Content units are derived (`make derive`): the recipes on the state's stage sheet, and the content "
            "units whose State is the state.",
            "- Format, Channel, Ownership and Surface are descriptions of what fits the state, not registry keys.", "",
            "## Examples", "",
            f"`examples.json`: worked examples of one topic carried through the states ({len(ex.get('sections', ex.get('tables', [])) or [])} "
            "sections). The Recipe column there names a kind of recipe (SEO, Authority, Referral), not a Recipe ID.", "",
            "## What reads recipes", "",
            "| Reader | What it takes |", "|---|---|",
            f"| place Content unit ↔ Recipe | units each option produces ({len(links['Content unit ↔ Recipe']['rows'])} links) |",
            "| compose Possibilities (this workbook) | the recipes for each audience at each state where it is present |",
            "| tools/coherence.py | every option pair against the fit maps |",
            "| place Content Units Recipe and Track, tools/assignments.py, tools/audit.py | which recipe each content unit follows; the unit's state must be among the recipe's states and the tracks must match |",
            "| amplify Candidates (transformations.json) | format pairs that are options of the same recipe but not marked in Format transformations |",
            "| tools/derive.py template | Recipes defined per state |", "",
            "## Using recipes", "",
            "Combination chain: state → user state → intent → trust → friction tolerance → proof needed → CTA → format → channel → surface. "
            "Ownership follows from the channel.", "",
            "| Step | Action | Detail | Dictates |", "|---|---|---|---|",
            "| 1 | Start with the state | Which customer state is the person in? | |",
            "| 2 | Derive the user state | What do they know, feel and want there? (Template: User state) | |",
            "| 3 | Derive the constraints | Intent, trust, friction tolerance, proof needed (Template) | |",
            "| 4 | Pick the CTA that fits the constraints | Ask only for what the state allows | Constraints → CTA |",
            "| 5 | Pick the format that carries the CTA | | CTA → format |",
            "| 6 | Pick the channel where that format lives | Format Channel Fit | Format → channel |",
            "| 7 | Pick the surface where it renders | Format Surface Fit, Channel Surface Fit, State Surface Fit | Format + channel → surface |",
            "| Then | Read the derived values | Ownership from the channel; metrics from the Metrics registry | |", "",
            "### Picking a recipe (ask in order)", "",
            "| # | Question | Guide |", "|---|---|---|",
            "| 1 | Where is the audience already spending attention? | That eliminates most channels. |",
            "| 2 | What can be afforded? | $0: earned and owned social. Low: owned, earned and small paid tests. High: paid, shared and the rest. |",
            "| 3 | What assets exist already? | A founder who writes: authority, LinkedIn. Video skills: reach. A community: community. A podcast: borrowed trust. None: search content and one social channel. |",
            "| 4 | What is the time horizon? | Days: paid. Weeks: social and PR. Months: search and community. Years: brand and owned audience. Compare with Time to first result. |",
            "| 5 | What is the category? | B2C impulse: reach, interrupt, meme. B2C considered: search, social proof, community. B2B SMB: search, social, community. B2B enterprise: authority, borrowed trust, events, PR. |",
            "| 6 | What is the competition doing? | Crowded: go where they are not. Empty: dominate it. |",
            "| 7 | What can be measured? | Start where the Direct metrics can be measured. |", "",
            "Before a recipe enters a plan: at least one of its options uses a channel the product can use; at least one of its Audiences is in the "
            "plan; its Time to first result fits the product's time horizon. Priority, status and timing belong to the product's plan, "
            "not to the recipe.", "",
            "### Evaluating (after Time to first result, then at 30–60 days)", "",
            "| # | Question | Check |", "|---|---|---|",
            "| 1 | Did it reach the right people? | Audience quality, not only volume |",
            "| 2 | Did they engage? | The Direct metrics |",
            "| 3 | Did it move them to the next state? | The Downstream metrics; a recipe that performs directly but moves no one is not working |",
            "| 4 | What did each outcome cost? | Cost per outcome |",
            "| 5 | What compounded? | Search, owned audience, community |",
            "| 6 | What stopped when spending stopped? | Paid, most social |",
            "| 7 | What to double down on? | Highest signal, lowest cost, most compounding |", "",
            "### B2C and B2B", "",
            "| Dimension | B2C | B2B |", "|---|---|---|",
            "| Decision maker | One person, fast | Committee, slow |",
            "| Buying trigger | Emotion, impulse, need | Budget, pain, mandate |",
            "| Price sensitivity | High | Lower |",
            "| Trust source | Social proof, reviews, influencers | Case studies, ROI, references |",
            "| Sales cycle | Minutes to days | Weeks to months |",
            "| Sales motion | Self-serve | Sales-assisted |",
            "| Volume | High | Low |",
            "| CAC tolerance | Low | Higher |",
            "| Retention driver | Habit, delight, identity | Contract, integration, ROI |",
            "| Channels | Social | LinkedIn, email, events |", "",
            "### First steps by budget (B2C)", "",
            "| Budget | Steps |", "|---|---|",
            "| $0 budget, no audience | 1. One short-form video platform. 2. Post 1–3 times a day for 30 days. 3. Search content for problem-aware. 4. Ten reviews from the first customers. 5. An email list from day one. |",
            "| Small ($1–5k a month) | 1. Short-form organic plus a paid boost on the best posts. 2. Search content twice a month. 3. Micro-influencer seeding. 4. Retargeting site visitors. 5. Email flows: welcome, abandoned cart, post-purchase. |",
            "| Larger ($10k+ a month) | 1. Paid social at scale. 2. Influencer program. 3. Search and content engine. 4. PR. 5. Community. 6. Retention and referral programs. |", "",
            "### B2C priority order", "",
            "| # | Priority | Why |", "|---|---|---|",
            "| 1 | Retention before acquisition | Repeat customers cost less than new ones |",
            "| 2 | Social proof before paid | Reviews and UGC outperform ads |",
            "| 3 | Short-form video before blog | Where attention is |",
            "| 4 | Email before everything | It is owned and it compounds |",
            "| 5 | One channel deep before many shallow | Dominate one |",
            "| 6 | Community before ads at scale | Trust beats reach |",
            "| 7 | Referral before discount | Advocacy costs less than promotion |", ""]
    OUT["knowledge/model/compose/spec.md"] = "\n".join(out)
    return OUT


def place_amplify_spec():
    OUT = {}



    C = collections.Counter
    place = models.read("place")
    cu = models.sheet(place, "Content Units")
    fmx = models.sheet(place, "Full matrix")
    cmx = models.sheet(place, "Compact matrix")
    links = {s["name"]: s for k in ("place", "transformations", "recipes") for s in models.read(k).get("sheets", [])}
    U = cu["rows"]
    ALLOWED = cu["allowed"]


    def allowed(c):
        a = ALLOWED.get(c)
        if not a:
            return "text"
        if "registry" in a:
            v = f'{a["registry"]["sheet"]} {a["registry"]["column"]}'
        else:
            v = ", ".join(a["values"])
        return v + (" (a list, separated by \", \")" if a.get("multiple") else "")


    def filled(c):
        return sum(1 for r in U if r.get(c) not in (None, ""))


    chosen = set(cu["chosen"])
    out = ["# Place spec", "",
           "Content units: actual pieces of content placed in the space. Source: `content-units.json`. Output: `content-units.xlsx`, "
           "rendered from the JSON. The rules sit beside the columns they govern: Content Units `chosen`, `allowed` and "
           "`required`; Full matrix `derived`, one rule per derived column.", "",
           "| Sheet | Kind | Rows | Columns |", "|---|---|---|---|",
           f"| Content Units | source: edit here only | {len(U)} | {len(cu['columns'])} |",
           f"| Full matrix | view: recomputed by `make derive` | {len(fmx['rows'])} | {len([c for c in fmx['columns'] if c])} in {len(fmx['column_groups'])} groups |",
           f"| Compact matrix | view: columns of the Full matrix | {len(cmx['rows'])} | {len(cmx['columns'])} |",
           f"| Content unit ↔ Recipe | view: recomputed by `make derive` | {len(links['Content unit ↔ Recipe']['rows'])} | {len(links['Content unit ↔ Recipe']['columns'])} |", "",
           "Content unit ↔ Recipe: " + links["Content unit ↔ Recipe"]["description"], "",
           "## Content Units", "",
           "One row per content unit. Identity columns say what the unit is; chosen columns place it on each axis of the space.", "",
           "| Column | Kind | Values | Filled |", "|---|---|---|---|"]
    for c in cu["columns"]:
        kind = "chosen" if c in chosen else "identity"
        out.append(f"| {c} | {kind} | {allowed(c)} | {filled(c)} of {len(U)} |")
    out += ["", f"Products: {', '.join(f'{k} ({n})' for k, n in C(r.get('Product') for r in U).most_common())}. "
            f"States: {', '.join(f'{k} ({n})' for k, n in C(r.get('State') for r in U).most_common())}.", "",
            "## Full matrix", "",
            "Every Content Units row with every attribute its chosen values point at, one column group per parent sheet. Row 1 names "
            "the group, row 2 is the header. Each derived column is a lookup into its parent (a list lookup for list values, rules "
            "for the two computed columns). Each rule in Full matrix `derived` names the parent sheet, the key column of the unit, "
            "the column matched in the parent and the column read, with a description.", "",
            "| Group | Columns | Read from |", "|---|---|---|"]
    src = {}
    for g, cols in fmx["column_groups"].items():
        out.append(f"| {g} | {len(cols)} | {src.get(g, 'Content Units' if g == 'Content Units' else 'space: ' + g)} |")
    kinds = C(v["kind"] for v in fmx["derived"].values())
    out += ["", f"Derived columns: {sum(kinds.values())} ({', '.join(f'{k} {n}' for k, n in kinds.most_common())}).", "",
            "## Compact matrix", "",
            f"Columns: {', '.join(cmx['columns'])}. Each is the Full matrix column of the same name.", "",
            "## Rules", "",
            "- Edit Content Units only; `make derive` rebuilds both views, `make check` fails when one is out of date.",
            "- Ownership is not chosen: Primary ownership is the Primary channel's Ownership; Secondary ownership is chosen.",
            "- `make schema` checks that every Full matrix column but ID has a rule and every rule a column, that required "
            f"columns are filled ({', '.join(cu['required'])}), that every value is allowed.",
            "- `make coherence` checks every pair of a unit's values against the fit maps: "
            f"{len(U)} units, 0 pairs not marked.",
            "- Repurposes into names format keys; each pair must be marked in amplify Format transformations, or it shows in its Candidates sheet.", "",
            "## What reads content units", "",
            "| Reader | What it takes |", "|---|---|",
            f"| Content unit ↔ Recipe (this workbook) | the recipe options that produce each unit ({len(links['Content unit ↔ Recipe']['rows'])} links) |",
            f"| amplify Content unit ↔ Transformation | every format the unit's format transforms into ({len(links['Content unit ↔ Transformation']['rows'])} links) |",
            f"| amplify Content unit ↔ Repurposing | each Repurposes into and its transformation ({len(links['Content unit ↔ Repurposing']['rows'])} links) |",
            "| amplify Candidates | Repurposes into pairs not marked in Format transformations |",
            "| compose Template | Content units per state |",
            "",
            "## Using the matrix", "",
            "The matrix is a database, not a document: axes are columns, content units are rows, values are tags, views are filters, "
            "an audit is a query, strategy is the balance of the portfolio across axes. Format says what to make, channel where, "
            "state why, ownership who controls it, surface exactly where it renders.", "",
            "| Step | What to do |", "|---|---|",
            "| 1. Lock the axes | Use only registry values; nobody invents new ones in a row. |",
            "| 2. One row per unit | Columns are the axes plus strategy and measurement. |",
            "| 3. Tag every unit | One format, one primary channel (secondary optional), one primary state, one surface, one CTA, one metric. |",
            "| 4. Audit for gaps | Formats in only one state; states with one format; channels missing from BOFU or Advocacy; states with the fewest units or the most units and worst metrics; the share of reach that is paid, owned, earned, shared; surfaces with no content or too much. |",
            "| 5. Audit for mismatches | BOFU content on a TOFU surface, TOFU content on a BOFU surface, paid creative on an owned surface, owned content on an earned channel. |",
            "| 6. Map the real path | Instrument the journey: where people enter, loop, skip states, drop off, re-enter. Fix the biggest drop. |",
            "| 7. Build views | Same data, different filters. |",
            "| 8. Review | Weekly: production, status, blockers. Monthly: performance by state, channel, format. Quarterly: portfolio balance, ownership mix, gaps, mismatches. Yearly: retire dead values, add new ones. |", "",
            "| Mistake | Why it hurts |", "|---|---|",
            "| Conflating axes | \"Paid social video\" is paid + social + video, not a format. |",
            "| Too many values | Nobody tags consistently. |",
            "| No primary | A unit tagged with five states says nothing. |",
            "| No owner, no audit | The tags drift and stop being true. |",
            "| Tool before schema | The tool gets rebuilt once the axes are defined. |",
            "| Waiting for the perfect taxonomy | Ship a first version, iterate. |",
            "| Ignoring surface, ownership or state | Without surface it is vague, without ownership blind to risk, without state misaligned. |", ""]
    OUT["knowledge/model/place/spec.md"] = "\n".join(out)

    # ---------- amplify ----------
    tdoc = models.read("transformations")
    ft = models.sheet(tdoc, "Format transformations")
    cand = models.sheet(tdoc, "Candidates")["rows"]
    cells = [v for r in ft["rows"] for c, v in r.items() if v in ("Down", "Up", "Across")]
    fmts = {r["Key"] for r in ft["rows"] if any(v in ("Down", "Up", "Across") for v in r.values())} | \
           {c for r in ft["rows"] for c, v in r.items() if v in ("Down", "Up", "Across")}
    cm = C(cells)
    rep = links["Content unit ↔ Repurposing"]["rows"]
    rc = C(r["Transformation"] or "blank" for r in rep)
    out = ["# Amplify spec", "",
           "Transformations: how the same message moves from one format to another. Source: `transformations.json`. Output: "
           "`transformations.xlsx`, rendered from the JSON.", "",
           "| Sheet | Kind | Rows | Columns |", "|---|---|---|---|",
           f"| Format transformations | source: authored | {len(ft['rows'])} source formats | {len(ft['columns']) - 3} target formats |",
           f"| Candidates | view: recomputed by `make derive` | {len(cand)} pairs | {len(models.sheet(tdoc, 'Candidates')['columns'])} |",
           f"| Content unit ↔ Transformation | view: recomputed by `make derive` | {len(links['Content unit ↔ Transformation']['rows'])} | {len(links['Content unit ↔ Transformation']['columns'])} |",
           f"| Content unit ↔ Repurposing | view: recomputed by `make derive` | {len(links['Content unit ↔ Repurposing']['rows'])} | {len(links['Content unit ↔ Repurposing']['columns'])} |", "",
           "Content unit ↔ Transformation: " + links["Content unit ↔ Transformation"]["description"], "",
           "Content unit ↔ Repurposing: " + links["Content unit ↔ Repurposing"]["description"], "",
           "## Format transformations", "",
           "Key is the source format, the format columns are the target. Read a row for what a format can become, a column for what it "
           "can be built from. Rows and columns follow the Formats sheet; Storyboard and Voiceover are left out (production inputs, "
           "listed in combine Format State Fit, Not in the table).", "",
           "| Marker | Meaning | Example |", "|---|---|---|",
           "| Down | into a smaller format: break apart | article → social post, carousel, newsletter |",
           "| Up | into a larger format: build up | social posts → article; articles → ebook |",
           "| Across | into a format of the same size | social post → infographic |", "",
           f"{len(cells)} pairs marked across {len(fmts)} formats: {cm['Down']} Down, {cm['Up']} Up, {cm['Across']} Across. "
           "Down and Up are one pair seen from its two ends. The marker is the direction the formats' Typical length gives "
           "(Short, Medium, Long). A blank means it is not a default transformation.", "",
           "## Candidates", "",
           "Format pairs that are not marked in Format transformations but that the other verticals point at. It is a review list: "
           "a pair enters Format transformations only when it is marked there by hand, and then leaves Candidates on the next "
           "`make derive`.", "",
           "| Column | Values |", "|---|---|",
           "| Source format, Target format | Formats keys |",
           "| Marker | the direction Typical length gives: Down, Up, Across |",
           f"| Content units | units whose format repurposes into the target ({sum(1 for r in cand if r['Content units'])} pairs): the matrix contradicts a unit, read these first |",
           f"| Recipes | recipes with both formats as options ({sum(1 for r in cand if r['Recipes'])} pairs): options are alternatives, so this suggests the pair, it does not prove it |", "",
           f"Markers: {', '.join(f'{k} {n}' for k, n in C(r['Marker'] for r in cand).most_common())}.", "",
           "## Rules", "",
           "- Format transformations is authored; `make derive` never writes it. Candidates is recomputed and never edited.",
           "- A content unit's Repurposes into should be a marked pair. Content unit ↔ Repurposing shows the result per unit: "
           + ", ".join(f"{k} {n}" for k, n in rc.most_common()) + " (Same format: a new version in the unit's own format).",
           "- Candidates never feed Format transformations.", "",
           "## What reads transformations", "",
           "| Reader | What it takes |", "|---|---|",
           f"| Content unit ↔ Transformation (this workbook) | every format each unit's format transforms into, and the units derived in it ({len(links['Content unit ↔ Transformation']['rows'])} links) |",
           f"| Content unit ↔ Repurposing (this workbook) | the transformation behind each Repurposes into ({len(rep)} links) |", ""]
    OUT["knowledge/model/amplify/spec.md"] = "\n".join(out)
    return OUT


def specs():
    """{path: text} of every spec."""
    out = {}
    for fn in (enumerate_spec, combine_spec, compose_spec, place_amplify_spec):
        out.update(fn())
    return out


def main():
    for rel, text in specs().items():
        (ROOT / rel).write_text(text)
    print(f"wrote {len(specs())} specs")


if __name__ == "__main__":
    sys.exit(main())
