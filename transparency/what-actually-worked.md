# What actually built the user base

The short version: a real Reddit presence and a referral relationship built the user base. Cold email, with a serious engineering effort behind it, produced a handful of users. Here is the ranking with its receipts — and its caveats.

## The attribution caveat, first

Signup attribution below is **first-touch**, from the founder-CRM journey table (the same query `../proof/generate_proof.py --with-logpose` runs — see the signups table in [`../proof/README.md`](../proof/README.md)). First-touch systematically undercounts community channels: someone who reads a Reddit thread, remembers the name, and signs up from the site a week later records as `web`. So read the channel table as a floor for community effect, not a measurement of it.

## 1. Reddit presence

The account documented in [`../proof/`](../proof/) — 1.5M+ tracked views, real replies, no automation on-platform — is the engine everything else feeds off. Its direct signup attribution is structurally invisible (Reddit does not pass clean referrers, and the win path is "saw the thread → searched the name → signed up," which lands as `web` or `search`). What is measurable: the tracked wins ledger in the proof data (leads, signups, and citations traced to specific threads), and the fact that the `web` + `search` signup rows exist at all for a product with no paid acquisition.

This is also the channel the whole repo teaches, so weigh the incentive — then check the receipts in `proof/` rather than taking the ranking on faith.

## 2. Referrals

The single largest first-touch channel in the signup table. A large share traces to one relationship: GummySearch's shutdown notice pointed its users toward alternatives, and Clearbox was one of them. Citable query against the founder CRM (events carrying the GummySearch referral marker):

```sql
SELECT COUNT(*) FROM events
WHERE kind = 'signup'
AND lower(COALESCE(metadata_json,'') || COALESCE(campaign,'')) LIKE '%gummy%';
-- 62 signup events (57 distinct people), as of 2026-08-06
```

The lesson generalizes: one well-placed relationship in the exact moment a competitor's users were looking outperformed the entire outbound machine below.

## 3. Everything else — including the cold-email machine

LinkedIn, search, and X each show up in single digits of first-touch signups. Cold email — the channel with by far the largest infrastructure investment — shows **5** first-touch signups in the same table. The full story of what was built, what the data showed, and why the effort moved elsewhere is in [`cold-email-postmortem.md`](cold-email-postmortem.md).

## What this changed

The method this repo teaches is the direct product of this ledger: be genuinely present where buyers already talk, automate the reading and the drafting off-platform, keep every send human. That allocation isn't a philosophy that happened to work — it's what the channel table said to do.
