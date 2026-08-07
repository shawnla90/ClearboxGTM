# How to win on Reddit

The thesis behind everything in this repo. The full method, with the live numbers, is public at [shawnos.ai/reddit](https://shawnos.ai/reddit). This page is the compressed version.

## The rules that are not negotiable

**Do it real or don't do it at all.** New accounts are dead on arrival for promotion. Bought accounts and "warmed" accounts get detected — Reddit runs its own AI detection, and the platform reads behavior long before it reads your words. There is no shortcut that survives. The account that wins is a real person's account with real karma earned on real interests.

**Karma is the currency, and you earn it on your own curiosity.** The fastest ramp is posting about things you genuinely care about, in rooms you genuinely read. Karma earned anywhere counts everywhere. A gaming sub, a hobby sub, an anime sub — all of it builds the account that later carries your professional presence.

**Be natural ON Reddit. Use the data OFF Reddit.** This is the split that makes the whole system work. On the platform: human replies, genuine value, no links in comments, no product drops. Off the platform: pull the data through the API and orchestrate everything — signal classification, buyer-language mining, content plans, enrichment, digests. Automate the reading, never the talking.

**Value first, links almost never.** A URL in a post body gets auto-removed in many subs; describe the artifact and put the link in a comment if asked. No hard CTAs. Your profile bio does the discovery work. Comments that read like marketing get an account flagged; comments that solve the problem build the karma that compounds.

**Recency is a hard gate.** Engage with live threads only. Necro-posting on old threads reads as scraping-and-spamming and is the fast lane to a ban.

**Know the gates before you post.** Karma minimums, account-age gates, sub-specific rules. Check them; never assume them. A removed post is not neutral — a slow post decays, a removed post stops dead, and views that stop dead a few hours in are your shadowban tell.

## Why this matters more now

AI assistants read Reddit heavily when buyers ask "best X", "X vs Y", "should I buy". The conversations happening there decide what AI recommends. A consistent, current, real presence in the right rooms is how a brand becomes the answer — and none of it works from a fake account.

## The motion, mapped to this repo

| Stage | What happens | Where |
|---|---|---|
| Write the offer properly | One-liner, selling points, keywords, subs — researched, not rushed | `skills/clearbox-onboard/` |
| Onboard a person | Their route through the playbook, from their real data | `skills/reddit-onboard/` |
| Read the market | Pull, mine, score buyer signals into action lanes | `engine/` |
| Engage as a human | Draft value-first replies, approve one by one | `skills/reddit-engage/` |
| Resolve who it is | The disclosure gate, then enrichment | `engine/unmask.py` + `playbooks/orchestrate-freckle.md` |
| Orchestrate the rest | Enrichment, scoring, magnets, digests — off-platform | `playbooks/orchestrate-deepline.md` |
| Deliver as a service | The agency package: sheet, deck, command center | `skills/reddit-agency/` |
| Audit quality | Score any account's picks before the client does | `playbooks/account-quality-benchmark.md` |
