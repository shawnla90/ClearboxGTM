# Proof

Every number below is generated from a tracking database and rendered from its export — never typed by hand. That provenance rule exists because an audit of an earlier page found hand-typed stats had drifted 2–5x in both directions; two were overstated, which a monotonic view counter makes impossible to defend. The fix was structural: a script emits the numbers, the page renders from its output, and a claim without a query behind it gets cut. The same rule is enforced across this repo (see `skills/reddit-onboard/FACTCHECK.md`, rule 1).

## One account, tracked from zero (as of 2026-08-06)

| Metric | Value |
|---|---|
| Tracked post views | **1,561,082** |
| Total karma | 2,499 (1,596 post / 903 comment) |
| Posts | 192 |
| Comments | 595 |
| Subreddits reached | 49 |
| Tracked wins (leads, signups, citations) | 25 |
| Time span | 5.2 months |

Two eras, deliberately run in sequence:

| Era | Items | Views | Days | What it proves |
|---|---|---|---|---|
| Karma-building | 422 | 1,185,453 | 38 | A real account, posting on real interests, ramps fast — and never got banned doing it |
| Working era | 365 | 375,629 | 119 | The same account then carries a professional presence: slower, steadier, compounding |

The full method with the live, self-updating numbers: **[shawnos.ai/reddit](https://shawnos.ai/reddit)**.

## The disclosure-gate numbers

From a live run of the `engine/unmask.py` gate across 720 lead-lane authors: **1.25%** had publicly self-disclosed a company (named it, linked it, or posted under a brand handle). Of those disclosed domains, enrichment resolved 44.3% to a full company record, 35.7% partial, 24.3% to contacts, 7.1% missed. The low disclosure rate is the design working: everything below the gate stays a human conversation, which is where the account grows.

## Why this is here

A repo full of method with no receipts is a pitch. The receipts are what let an operator hand this to a client — or an agency hand it to theirs — and say: this is not theory, it runs, and here is what it produced.
