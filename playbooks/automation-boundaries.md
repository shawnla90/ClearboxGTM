# Automation boundaries

The single design decision everything in this repo hangs on: **be natural on Reddit, automate off it.** This page states the boundary precisely, because "we automate Reddit" and "we automate around Reddit" are opposite strategies with opposite outcomes.

## What automation CAN do

Everything that happens *off-platform*:

- **Research** — pulling threads, mining topics, tracking communities ([`../engine/`](../engine/))
- **Classification** — scoring signals into engage / lead / competitor lanes, intent tagging
- **Drafting** — reply drafts, content packs, offer packs — all of it staged for a human, none of it sent by the machine ([`../skills/reddit-engage/`](../skills/reddit-engage/), [`../skills/longtail-content/`](../skills/longtail-content/))
- **Monitoring** — GEO term checks, competitor share-of-voice, account health
- **Digests** — the daily readout of all of the above to Slack, a sheet, or a doc

## What automation CANNOT do

Anything that *acts as the account*:

- **Posting** — never automated
- **Voting** — never automated
- **DMs** — never automated

**Every send is a human pressing send.** Not as a compliance disclaimer — as the mechanism that makes the whole motion work. An account is trusted because a person is behaviorally present in it; the moment software talks as the account, the account is fake, and Reddit's systems and Reddit's users are both good at detecting fake.

## Why the boundary is where it is

The reasoning lives in the two core guides — read them rather than a summary:

- [`how-to-win-on-reddit.md`](how-to-win-on-reddit.md) — karma is the currency, do it real or not at all, and what actually gets accounts banned
- [`../skills/reddit-agency/MULTI-ACCOUNT-OPERATIONS.md`](../skills/reddit-agency/MULTI-ACCOUNT-OPERATIONS.md) — the same boundary at agency scale: named operators, disclosure, coordination controls, and the myths (IP tricks, VPNs) that don't help because behavior is what's measured

The short version of the don't-get-banned guidance: the accounts that survive are the ones where the human is real, the replies are useful, and the automation never touches the send button. Every control in this repo — the approval queues, the drafted-not-posted rules, the disclosure gate — is that one sentence, enforced.
