<p align="center"><img src="assets/banner.png" alt="ClearboxGTM — how to win on Reddit" width="100%"></p>

# ClearboxGTM

**How to win on Reddit — the skills, the engine, and the playbooks, ready for your coding agent.**

Buyers ask AI first now, and AI reads Reddit to decide what to recommend. The conversations happening in your buyers' subreddits are deciding whether you get named. This repo is the complete motion for showing up there properly: real account, real replies, and everything else automated off-platform. It is what we run for clients; it is built so you (or your agency) can run it for yours.

Open this repo in [Claude Code](https://claude.ai/code) (or Codex, or Cursor) and start with:

```
read playbooks/how-to-win-on-reddit.md and tell me where to start for <my company>
```

## The fastest start: fill the form properly

Signing up at [clearbox.to](https://clearbox.to)? Don't rush the onboarding form — Clearbox scores Reddit content against what you write in it. Paste **[`prompts/clearbox-onboarding.md`](prompts/clearbox-onboarding.md)** into your coding agent, give it your domain, and it researches your company and writes every field with sources you can check.

That interview is the most portable thing in this repo. The offer pack it produces — sourced selling points, buyer-language keywords, researched competitors, verified communities — is the context every other stage consumes, and it runs in any agent: **[`playbooks/offer-context-onboarding.md`](playbooks/offer-context-onboarding.md)**.

Running the agency motion across client accounts? Start with the public [multiple Reddit accounts operating guide](https://fierce-camelotia-1fa.notion.site/Clearbox-Running-Multiple-Reddit-Accounts-for-Clients-3b51fb92bcd78187a212de323c577399). It covers the account/workspace/operator boundary, related brands, disclosure, IP and VPN myths, coordination controls, and the measurement receipts clients can see.

## What's in here

| Stage | What it does | Where |
|---|---|---|
| **Onboard the offer** ★ | Domain in → researched offer pack out — the portable interview pattern every stage below consumes, runnable in any agent | [`playbooks/offer-context-onboarding.md`](playbooks/offer-context-onboarding.md) · [`skills/clearbox-onboard/`](skills/clearbox-onboard/) |
| **Onboard a person** | A personalized route through the public playbook, from their real data, shipped as a Notion doc | [`skills/reddit-onboard/`](skills/reddit-onboard/) |
| **Read the market** | Pull → mine → score buyer signals into engage / lead / competitor lanes | [`engine/`](engine/) |
| **Engage as a human** | Value-first reply drafting with a hard approve-each-one gate | [`skills/reddit-engage/`](skills/reddit-engage/) |
| **Resolve who it is** | The disclosure gate, then enrichment (Freckle default, pluggable) | [`engine/unmask.py`](engine/unmask.py) |
| **Measure AI visibility** | GEO terms worth owning + a live retrieval-visibility score (retrieval ≠ citation) | [`skills/geo-visibility/`](skills/geo-visibility/) |
| **Win the long tail** | Buyer questions → blog/LinkedIn/Reddit drafts built for attribution, drafted never posted | [`skills/longtail-content/`](skills/longtail-content/) |
| **Orchestrate off-platform** | Enrichment, GEO terms, share of voice, lead magnets, the daily Slack digest | [`playbooks/`](playbooks/) |
| **Sell it as a service** | The agency package: buyer-signal sheet, deck, Notion command center | [`skills/reddit-agency/`](skills/reddit-agency/) |
| **Win the agency client** | The reverse-uno method: lead with a readout of their buyers, not a pitch | [`playbooks/win-an-agency-client.md`](playbooks/win-an-agency-client.md) |
| **Run multiple client accounts safely** | Client ownership, named operators, disclosure, coordination controls, and a five-level success scorecard | [`skills/reddit-agency/MULTI-ACCOUNT-OPERATIONS.md`](skills/reddit-agency/MULTI-ACCOUNT-OPERATIONS.md) |
| **Competitor intel** | Share of voice, sentiment, and where the opening is — from classified Reddit ops | [`skills/competitor-intel/`](skills/competitor-intel/) |
| **Sentiment** | Three-class LLM sentiment on every opportunity, feeding the competitor narrative | [`skills/sentiment/`](skills/sentiment/) |
| **Last 24 hours** | The morning briefing — freshest buyer signals from the last day | [`skills/last24/`](skills/last24/) |
| **Slack digest** | The daily client delivery — engage threads, leads, competitor mentions, to Slack | [`skills/slack-digest/`](skills/slack-digest/) |
| **Reddit proposals** | Pitch materials for a prospect from their buyers' Reddit conversations | [`skills/reddit-proposal/`](skills/reddit-proposal/) |
| **Dataviz** | Reference architecture for GTM dashboards — Recharts palette, patterns, examples | [`skills/dataviz/`](skills/dataviz/) |
| **Attribution tracking** | The journey materialization pattern — first/last touch, no cookies, local data | [`playbooks/attribution-tracking.md`](playbooks/attribution-tracking.md) |
| **Audit quality** | The 5-dimension pick-quality rubric | [`playbooks/account-quality-benchmark.md`](playbooks/account-quality-benchmark.md) |
| **Security** | The protection model — what is guarded, the scan gate, read-only DBs, no auto-send | [`SECURITY.md`](SECURITY.md) |
| **Students** | A free semester of Clearbox Pro + monthly group office hours, for students who build in public | [`STUDENTS.md`](STUDENTS.md) |
| **Partners** | Referral and delivery tracks — terms by email, method in the open | [`PARTNERS.md`](PARTNERS.md) |

## The playbooks

- [`how-to-win-on-reddit.md`](playbooks/how-to-win-on-reddit.md) — the thesis: do it real or not at all, karma is the currency, be natural ON Reddit and automate OFF it
- [`offer-context-onboarding.md`](playbooks/offer-context-onboarding.md) — the interview pattern as portable IP: offer context in, everything downstream inherits its quality
- [`automation-boundaries.md`](playbooks/automation-boundaries.md) — precisely what the machine may and may never do
- [`win-an-agency-client.md`](playbooks/win-an-agency-client.md) — the reverse-uno: show them their buyers instead of a pitch
- [`orchestrate-freckle.md`](playbooks/orchestrate-freckle.md) — the Reddit-to-pipeline loop: Clearbox classifies, the disclosure gate holds, Freckle enriches, four surfaces receive
- [`orchestrate-deepline.md`](playbooks/orchestrate-deepline.md) — opportunity stream → orchestration substrate, with the trust model that keeps Reddit UGC as data, never instructions
- [`notion-command-center.md`](playbooks/notion-command-center.md) — every engagement ships as real, linked, stable documents
- [`account-quality-benchmark.md`](playbooks/account-quality-benchmark.md) — score any account's picks before the client does
- [`attribution-tracking.md`](playbooks/attribution-tracking.md) — the journey materialization pattern: first/last-touch attribution from local SQLite, no cookies, no third-party tracking

## Proof

**1.5M+** tracked views on one real account, with the karma, wins, era history, and signup-attribution tables generated straight from the tracking databases — never typed by hand. The numbers, their provenance rule, and the script that enforces it: [`proof/`](proof/). Live version at [shawnos.ai/reddit](https://shawnos.ai/reddit).

## Transparency

What actually built the user base — including what failed. The honest channel ranking, and a full postmortem of the cold-email machine that produced a handful of users despite a serious engineering investment: [`transparency/`](transparency/). The failures shaped this method as much as the wins did.

## The rules this repo will not let you break

1. **Nothing posts automatically.** Every send is a human pressing send. The automation reads, drafts, scores, and digests; it does not talk.
2. **The disclosure gate refuses to guess.** Identity resolution runs only on what an author already tied to a company in public.
3. **Recency is a hard gate.** Live threads only.
4. **Every claim traces to a source.** The FACTCHECK gates in the skills are not decoration; they are the post-mortems of real mistakes.
5. **Retrieval is not citation.** Exa can show that a source is retrievable. Only a captured AI answer with an exact source receipt proves that answer named or cited it.
6. **Your data stays yours.** Every database is a local SQLite file on your machine. No cookies, no shared backend, no analytics pixel. Attribution runs locally. Client workspaces are siloed by directory. See [`SECURITY.md`](SECURITY.md).

How these rules are enforced — the provenance rule, the language boundaries, and the scan gate every release passes: [`VERIFYING.md`](VERIFYING.md).

## Related

- [gtm-coding-agent](https://github.com/shawnla90/gtm-coding-agent) — the broader build-your-GTM-engine starter kit (21 chapters, 9 starters). The Reddit engine here also lives there as the `reddit-buyer-signals` starter, documented in chapters 18–19.
- [The multi-account operations guide on Notion](https://fierce-camelotia-1fa.notion.site/Clearbox-Running-Multiple-Reddit-Accounts-for-Clients-3b51fb92bcd78187a212de323c577399) — the public, shareable version of the agency operating guide
- [shawnos.ai/reddit](https://shawnos.ai/reddit) — the public playbook with live numbers
- [shawnos.ai/vault](https://shawnos.ai/vault) — the skill tree these skills publish to
- [clearbox.to](https://clearbox.to) — the product; students see [`STUDENTS.md`](STUDENTS.md), partners see [`PARTNERS.md`](PARTNERS.md)

## License

MIT. Take it, run it, run it for clients.

---

**Powered by [Clearbox](https://clearbox.to)** — see your market, move first. Clearbox reads live Reddit conversations and returns the person, the room, the timestamp, and their exact words, classified by buying intent, every day.
