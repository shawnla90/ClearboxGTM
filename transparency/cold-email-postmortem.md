# Cold email postmortem — deliverability lessons, not tactics

We built a complete cold-email stack for Clearbox: cloud sending infrastructure, a dozen dedicated sending domains, full authentication, warmup schedules, provider-aware routing, bounce ingestion, and MX classification across ten thousand prospect domains. It was real engineering, done carefully, and it produced a handful of users. This is the honest account, kept because the deliverability findings are useful to anyone weighing the same investment — not as a playbook for sending more cold email.

## What was built

- **Sending layer:** Azure Communication Services, with cheap dedicated cold domains kept fully separate from the company's real domain — the one genuinely correct decision in the project, because it meant the failures below never touched the brand's own reputation.
- **Authentication:** SPF, DKIM, and DMARC configured and verified on every domain. All of it passed, everywhere, the whole time.
- **Discipline:** slow warmup ramps, plain-text sends, per-domain volume caps, reply-to pointing at a real monitored inbox, unsubscribe footers, suppression lists fed by automated bounce ingestion.
- **Routing:** an MX-classification pass over every prospect domain, so each recipient's actual mail provider was known before a single send was staged.

That last piece is what turned the project from a failure into a dataset.

## What the data showed

Measured 2026-06-27 across 10,149 MX-classified prospect domains, bounce rates by recipient provider:

| Recipient provider | Prospects | Hard-bounce rate |
|---|---|---|
| Google Workspace / Gmail | 9,582 | **33%** |
| Microsoft 365 | 5,938 | 1% |
| Proofpoint-fronted | 208 | 1% |
| Mimecast-fronted | 110 | 0% |

Three findings that matter beyond this project:

1. **Reputation is the wall, and authentication doesn't scale it.** SPF/DKIM/DMARC were clean on every domain; Google rejected the mail anyway, verbatim "blocked due to the reputation of the sending domain" — including sends to our *own* Gmail inboxes. New cheap domains on shared cloud IPs start with no history, and one major provider treated no-history as no-entry. The other providers accepted the same mail from the same domains at ~1%.
2. **Delivery is not inbox.** A 0% bounce rate only means the receiving server didn't reject the mail — it says nothing about inbox versus spam folder. A seed test that "delivered" cleanly still landed in spam. If you don't verify placement with a real seed inbox (and search *including* the spam folder — inbox search excludes it by default), your dashboard is measuring acceptance, not attention.
3. **The clicks were security scanners.** 633 of 637 tracked link sessions were single-pageview, sub-minute visits, and 85% of clickers were recipients behind Microsoft's link-scanning protection. Human replies across the whole effort: 5 on ~4,600 sends. A click-through number on cold email is, until proven otherwise, a count of robots checking your link for malware. Headline replies, never clicks.

## What it cost versus what it returned

The per-email cost was negligible and the domains were cheap. The real cost was weeks of engineering and operator attention — the sender, the router, the bounce pipeline, the classification pass, the dashboards to un-lie the dashboards. The return, per the generated signup table in [`../proof/README.md`](../proof/README.md): **5 first-touch signups.** In the same period, one referral relationship produced more than ten times that, and the Reddit presence built the audience everything else converts from.

## The lesson

We stopped. Not because cold email can never work — provider-aware routing to the ~1% providers was functioning — but because the ledger said the same hours compounded elsewhere. Reputation-based filtering means the cold-start cost of a fresh sending identity keeps rising, while a real community presence gets *more* effective with every post that earns karma and every thread that ranks. If your buyers live behind the strict providers, the honest options are patience (real domains, real history, real volume discipline) or a different channel entirely. We chose the different channel, and this repo is the method that replaced the machine.
