---
name: longtail-content
version: 1.0.0
description: Turn real buyer questions into long-tail attribution content. Wraps engine/content.py — scaffolds a three-draft pack (long-tail blog with TL;DR + FAQ schema, LinkedIn post, Reddit draft) from one mined buyer question and the offer pack's selling points, then anti-slop-checks the result. Drafted, never posted. Use when the user says "/longtail-content", "build the content pack", "answer this buyer question as content", or after a geo-visibility run surfaces terms the brand doesn't own yet.
---

# longtail-content

One real buyer question in, a checked three-draft content pack out — drafted, never posted.

The long tail is where attribution actually happens: a buyer types their exact problem, your page is the direct answer, and the visit is traceable to the question. This skill wraps [`engine/content.py`](../../engine/content.py): `scaffold` builds the pack skeleton and a generation brief from one opportunity plus the voice profile; the agent writes the words; `check` scans the drafts for slop and banned words before anything ships.

## Inputs

The canonical input is the offer pack from [`../clearbox-onboard/`](../clearbox-onboard/) — `clearbox-offer.json` supplies:

- `keywords[]` → the buyer-language terms the blog titles are phrased in
- the selling points (in `description`) → the sourced claims the drafts are allowed to make — nothing enters a draft that isn't in the pack or in the thread being answered

Plus, per pack: **one mined buyer question** — from the engine's mined topics, a live thread, or a [`geo-visibility`](../geo-visibility/SKILL.md) run's not-yet-retrieved terms (those are the content plan, pre-ranked by intent).

## How to run

```bash
# scaffold the skeleton + generation brief from one buyer question
python3 engine/content.py scaffold --client "Acme PM" --voice voice/core-voice.md \
  --topic "how to keep one source of truth across HubSpot and Salesforce" --out content/pack-01

# after writing the drafts: scan for slop and banned words
python3 engine/content.py check content/pack-01/blog.md
```

Read the module before running it. A pack is three drafts from the one question: a long-tail **blog** (buyer-query H1, TL;DR answer block up top, `## Frequently Asked Questions` with `### question` headings so it emits FAQPage schema, HowTo-shaped steps where it's a procedure), a **LinkedIn post** (hook delivers immediately, next line pays it off), and a **Reddit draft** (value-first, no pitch, no link-drop).

## The drafted-not-posted rule (binding)

The pack's manifest disables dispatch by design. Nothing this skill produces is published by automation: blogs ship through the client's own publishing flow, LinkedIn posts through a human, and the Reddit draft only ever enters the human approval queue in [`../reddit-engage/`](../reddit-engage/). Same boundary as everywhere else in this repo — the automation reads, drafts, and checks; it does not talk.

## Rules

1. **One question per pack.** A pack that answers three questions ranks for none of them.
2. **Claims trace to the offer pack or the thread.** The FACTCHECK discipline follows the content: a claim that isn't sourced in `offer-pack.md` doesn't appear in a draft.
3. **`check` before ship, always.** A draft with slop flags gets rewritten, not patched.
4. **Client-voice content stays in the client package** — it never flows to a public content channel.

## Related

- `../../engine/content.py` — the module this wraps
- `../../playbooks/offer-context-onboarding.md` — the pack the claims come from
- `../geo-visibility/` — where the term list comes from
- `../reddit-engage/` — the approval queue the Reddit draft feeds
