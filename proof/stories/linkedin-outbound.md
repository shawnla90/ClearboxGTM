# LinkedIn outbound

The pattern: use the Clearbox playbook as proof, then ask if they want the writeup. No pitch, no features list. The playbook itself is the pitch.

## The funnel

16 days (2026-07-23 through 2026-08-07):

| Stage | Count |
|-------|-------|
| Leads sourced | 1,297 |
| Connection requests sent | 496 |
| Accepted | 238 (48%) |
| Replied | 26 |
| Calls booked | 2 |
| In booking stage | 6 |
| Trials | 2 |
| Engaged | 8 |

Numbers come from the reconciliation database, not hand-counting. Every connection request sent is screenshot-captured as evidence. Accepts and replies are confirmed by a reconciliation script that scrolls the connections page and inbox, matches by profile URL, and records evidence with integrity hashes.

## The messages

The actual messages, because why not. They are part of the method.

### Connection request note

> ${fn}, building clearbox for gtm teams. it turns reddit into leads and competitor intel, read by buying intent. would value your read. mind connecting?

### Message 1 (on accept)

> thanks ${fn}. clearbox reads reddit by buying intent and drops the threads worth acting on into your inbox, sorted lead / competitor / engage. ran it on my own account: ~1.5M views, ~2,470 karma in 4.7 months. want the writeup?

### Message 2 (follow-up)

> ${fn}, here either way. the full playbook with the live numbers: shawnos.ai/reddit. curious what you think.

## Why this works

The connection request is 29 words. It names the product, what it does, and asks permission to share. No pitch deck, no feature list, no calendly link.

Message 1 leads with proof: the account's own numbers. The ask is lightweight -- "want the writeup?" -- not "book a demo."

Message 2 drops the public playbook link and steps back. The recipient either engages or does not. No follow-up sequence, no guilt trip.

## The architecture

Playwright + Chrome headless with a persistent browser session. Anti-detection measures: random jitter between actions (30-120 seconds), typing simulation with per-character delay, business-hours-only sending (Mon-Fri, 8am-midnight), daily send caps (40 CRs, 40 messages). LaunchAgent cron scheduling: every 30 minutes for sends, every 6 hours for reconciliation (checking accepts, replies, status changes).

The reconciliation layer is read-only. It scrolls the connections page and inbox, matches leads by LinkedIn profile URL, captures screenshot evidence of confirmed replies, and stores everything in a SQLite database with SHA-256 integrity hashes.

## What this proves

LinkedIn outbound with the Clearbox playbook as the message produces real pipeline. 48% accept rate on cold connection requests. The playbook itself -- the public numbers, the transparent method -- is the differentiator. Nobody asks "what does your product do?" because the connection request already told them, and Message 1 proved it with receipts.

## Related

- [No backlinks needed](no-backlinks-needed.md) -- the Reddit presence that produces the numbers Message 1 cites
- [Inbound from content](inbound-from-content.md) -- the inbound side of the same account
- [proof/README.md](../README.md) -- the generated stats behind the 1.5M+ claim
