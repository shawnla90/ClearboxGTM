# Offer-context onboarding — the interview pattern as portable IP

Every research agent, matching engine, and GTM workflow has an onboarding form somewhere near its start, and it is almost always rushed. This playbook elevates the interview behind [`skills/clearbox-onboard/`](../skills/clearbox-onboard/) into what it actually is: a repeatable pattern for extracting *offer context* — who you are, what you sell, why this buyer, in the buyer's own words, with every claim sourced — that any agent can run and any downstream system can consume.

## Why offer-context is the highest-leverage input

Every downstream step inherits the quality of this one. The keywords decide what gets matched. The competitor list decides what gets compared. The tracked communities decide where the system even looks — and in Clearbox, the subreddit suggestion pass runs **once**, at onboarding, and never again. A wrong keyword or an invented competitor doesn't fail loudly; it silently corrupts matching forever, and the system's output looks plausible the entire time. Almost every research or GTM system has an equivalent one-shot input; this is the discipline for getting it right the first time.

The pattern was built by a GTM engineer who ate these failure modes in real client work — the category assumed from a company name that turned out to be wrong, the competitor claim that a commenter falsified in public, the plausible-sounding subreddit that didn't exist. Each rule below is a post-mortem, not a preference.

## The interview

One question at a time, research between questions, nothing written from memory. The full mechanics live in [`skills/clearbox-onboard/SKILL.md`](../skills/clearbox-onboard/SKILL.md); this is the shape of the interview itself.

### Who you are
One sentence, the shape "X is a [category] for [who]." Hard limit 80 characters — counted with `wc -c`, not eyeballed. The bar: a stranger reads it and knows what the product is, who uses it, and why it matters. Every adjective that doesn't narrow the category or the buyer gets cut.

### What you sell
Selling points in the skill's seven fixed template shapes — each shape is falsifiable on purpose. "Unlike [competitor], X does [thing]" can be checked against the competitor's site; marketing prose can't be checked against anything. A slot you can't source gets skipped, never faked. Five sourced points beat eight with filler.

### Why this buyer
The words buyers actually type when they complain about the problem — not the words the product team uses in standup. "Cold email deliverability," not "multi-channel orchestration." This is where user briefs mislead: a brief is authoritative on positioning *intent*, never on the buyer's language. The buyer's language comes out of research.

### Why this feature
Differentiation over breadth. Lead with the claims that separate the product from named alternatives; feature lists carry the tail. Absence claims ("only X does...") are the easiest to falsify and the first thing a commenter will dunk on — when unsure, downgrade to a presence claim.

### Keywords
Lowercase, phrased the way buyers type them in posts: category terms, pain phrasings, and `<competitor> alternative` forms. Buyer language beats internal language every time, because matching runs on what buyers write, not on what the company wishes they wrote.

### Competitors
From research, never from the brief. Every competitor named must have come out of the research pass, confirmed as a real product in this category. The founder's mental list of rivals and the buyer's actual consideration set overlap less than anyone expects.

### Tracked communities
Verified or cut. Every community fetched and confirmed to exist; buyer rooms over practitioner rooms; no padding with plausible-sounding names. This is the one-shot field — it justifies the entire research pass.

## The fact-check gate

Every selling point traces to a URL, keyed to the point number in the artifact's Sources section. "Unlike X" claims need a source on X — a statement about what a rival lacks is a claim *about the rival*, and your model of the competitor is not a source. The full six rules and the before-paste checklist: [`skills/clearbox-onboard/FACTCHECK.md`](../skills/clearbox-onboard/FACTCHECK.md). Corrections found after the fact become new rules; the gate only grows.

## The context pack

The interview's output is a two-file artifact — the pack is the interface:

- **`offer-pack.md`** — the human-readable version: one-liner, selling points, keywords, competitors, communities, and a Sources section keyed to point numbers, so a reviewer can audit any claim in one hop. Skeleton: [`skills/clearbox-onboard/TEMPLATE.md`](../skills/clearbox-onboard/TEMPLATE.md).
- **`clearbox-offer.json`** — the machine-readable version: `name`, `description` (one-liner + selling points serialized), `keywords[]`, `competitorBrands[]`, `ownBrands[]`, `trackedSubreddits[]`, `domains[]`. Exact assembly in [`skills/clearbox-onboard/SKILL.md`](../skills/clearbox-onboard/SKILL.md), step 7.

Any agent that can read JSON can consume the pack. That's the point: the interview runs once, carefully, and everything downstream — matching, content, enrichment, audits — reads its output instead of re-asking.

## Runs anywhere

- **Claude Code:** the skill itself — [`skills/clearbox-onboard/`](../skills/clearbox-onboard/).
- **Cursor, Codex, any coding agent:** paste [`skills/clearbox-onboard/PROMPT.md`](../skills/clearbox-onboard/PROMPT.md) (published identically as [`prompts/clearbox-onboarding.md`](../prompts/clearbox-onboarding.md) — same file, duplicated on purpose so it's one click from the README).
- **Deepline, Freckle, or custom agents:** feed `clearbox-offer.json` in as workflow input — the orchestration patterns in [`orchestrate-deepline.md`](orchestrate-deepline.md) and [`orchestrate-freckle.md`](orchestrate-freckle.md) both start from exactly this context.

## Three drop-in reuses

1. **A GEO / long-tail run.** `keywords[]` + `competitorBrands[]` + `ownBrands[]` feed the [`geo-visibility`](../skills/geo-visibility/SKILL.md) skill (which measures `retrieval_visibility` — see the language rule in [`../VERIFYING.md`](../VERIFYING.md)); the selling points plus mined buyer questions feed [`longtail-content`](../skills/longtail-content/SKILL.md) for attribution content.
2. **Agency client research.** The first deliverable of [`win-an-agency-client.md`](win-an-agency-client.md) is an offer pack built *for the prospect's client* — proof you read their market before you pitched, in an artifact they can audit line by line.
3. **A student's first GTM exercise.** Build the pack for a campus org or local business: the source-or-cut discipline is the whole lesson, and the five tracked communities map exactly onto the five-subreddit grant cap in [`../STUDENTS.md`](../STUDENTS.md).

## Related

- [`skills/clearbox-onboard/`](../skills/clearbox-onboard/) — the skill this playbook generalizes
- [`skills/clearbox-onboard/PROMPT.md`](../skills/clearbox-onboard/PROMPT.md) — the agent-agnostic pastable
- [`skills/clearbox-onboard/TEMPLATE.md`](../skills/clearbox-onboard/TEMPLATE.md) — the artifact skeleton
- [`how-to-win-on-reddit.md`](how-to-win-on-reddit.md) — the method the pack feeds
