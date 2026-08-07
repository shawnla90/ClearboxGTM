# Account quality benchmark

A repeatable rubric for assessing any Clearbox account's opportunity batch — yours, or a client's before they judge it themselves. The goal is a comparable number per account over time, not a one-off vibe check.

## How to run one

1. Pull the account's brief and inbox.
2. Pull every opportunity **in full** (comment lineage and replies) — judge against the thread, never the snippet.
3. Score the five dimensions below, 0–10 each.
4. Report the worst pick first — clients judge on the floor, not the average.

## Dimensions

| # | Dimension | Question | Auto-fail |
|---|-----------|----------|-----------|
| 1 | Pick precision | What % of picks would the founder actually act on? | — |
| 2 | Label accuracy | Is each lead/engage/competitor label right vs the full thread? | "lead" with no buyer intent from the author |
| 3 | Freshness | % of picks on threads under 7 days old | Any necro pick (thread over 90 days old) caps this at 3 |
| 4 | Lead yield per sub | leads / total opportunities per subreddit — does it agree with the UI's performance ranking? | — |
| 5 | Suggestion recall | Which obvious subreddits for this offer did the suggester miss? | — |

## Known systematic issues (check every time)

- **Cold start:** subs added under 7 days ago look bad by construction — processing ramps before finds do. Never judge a new-window sub; flag it if the UI's score invites the user to.
- **Hit rate is not lead yield.** In one review, the account's worst-scoring sub held the only real lead in the batch, and its best-scoring sub held noise. A performance score built on found/processed points users at the wrong rooms; recompute yield yourself.
- **Necro threads hide:** inbox rows can show comment age, not thread age. Open the thread.
- **Shill risk:** a "lead" that names a competitor in promotional phrasing may be a seeded post. Read the author's history before acting.
- **Churn is not lead scarcity:** canceled accounts include plenty with labeled leads. Precision is what retains, not volume.
