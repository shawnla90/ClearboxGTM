<p align="center"><img src="assets/banner.png" alt="ClearboxGTM — how to win on Reddit" width="100%"></p>

# ClearboxGTM

**How to win on Reddit — the skills, the engine, and the client delivery system, ready for your coding agent.**

ClearboxGTM turns live Reddit buyer signals into a human-operated growth system: classify the opportunity, preserve the source, decide what deserves a reply, and track what actually surfaced later. Reddit threads can appear in search and AI answers; this repo keeps retrieval, observed appearance, exact citation, engagement, and business outcomes as separate receipts instead of promising that every contribution will rank.

<p align="center"><a href="https://docs.google.com/spreadsheets/d/100Q4e8ZW6xIHHk4GHzFO7ONmK_1MdNhBPi0Y4TngWjc"><img src="assets/gallery/client-value-pack-tour.gif" alt="ClearboxGTM client value pack: API dispositions to eleven-view Sheet and guided Notion brief" width="100%"></a></p>

<p align="center"><strong>Clearbox API → optional Freckle, Base Loop, or Clay analysis → 11-view Sheet → guided Notion brief</strong><br><a href="https://docs.google.com/spreadsheets/d/100Q4e8ZW6xIHHk4GHzFO7ONmK_1MdNhBPi0Y4TngWjc">Open the view-only Sheet</a> · <a href="https://fierce-camelotia-1fa.notion.site/ClearboxGTM-Client-Value-Pack-Demo-Acme-Ops-3b91fb92bcd7818ca3dad03e0e21cbd0">Read the guided value brief</a> · <a href="assets/gallery/client-value-pack-tour.mp4">Watch the MP4</a></p>

The demonstration above is generated from the synthetic Acme Ops fixtures checked into [`examples/client-pack/`](examples/client-pack/). It contains no client or operator-private data.

## Start in 60 seconds

Open this repo in [Claude Code](https://claude.ai/code) (or Codex, or Cursor) and start with:

```
read playbooks/how-to-win-on-reddit.md and tell me where to start for <my company>
```

Signing up at [clearbox.to](https://clearbox.to)? Don't rush the onboarding form — Clearbox scores Reddit content against what you write in it. Paste **[`prompts/clearbox-onboarding.md`](prompts/clearbox-onboarding.md)** into your coding agent, give it your domain, and it researches your company and writes every field with sources you can check.

That interview is the most portable thing in this repo. The offer pack it produces — sourced selling points, buyer-language keywords, researched competitors, verified communities — is the context every other stage consumes, and it runs in any agent: **[`playbooks/offer-context-onboarding.md`](playbooks/offer-context-onboarding.md)**.

Running the agency motion across client accounts? Start with the public [multiple Reddit accounts operating guide](https://fierce-camelotia-1fa.notion.site/Clearbox-Running-Multiple-Reddit-Accounts-for-Clients-3b51fb92bcd78187a212de323c577399). It covers the account/workspace/operator boundary, related brands, disclosure, IP and VPN myths, coordination controls, and the measurement receipts clients can see.

Already have a Clearbox inbox? The [client value-pack builder](skills/reddit-agency/CLIENT-VALUE-PACK.md) pulls its lead, engage, and competitor dispositions through the API, preserves every exact Reddit permalink, optionally merges Freckle, Base Loop, or Clay analysis, and rebuilds an 11-view Google Sheet plus a guided Notion brief. The skills and method are open. For the operated agency offering or multi-offer enablement, email **partners@clearbox.to**.

| Start with | Use it when | First command |
|---|---|---|
| **Offer-context onboarding** | You are configuring a new Clearbox offer | `read prompts/clearbox-onboarding.md and interview me for <domain>` |
| **Client value pack** | You already have classified opportunities or an export | `read skills/reddit-agency/CLIENT-VALUE-PACK.md and build the pack from <source>` |

## See the full client pack

<p align="center"><a href="https://docs.google.com/spreadsheets/d/100Q4e8ZW6xIHHk4GHzFO7ONmK_1MdNhBPi0Y4TngWjc"><img src="assets/gallery/client-pack-sheet.png" alt="ClearboxGTM eleven-view client value pack open on the branded Dashboard" width="100%"></a></p>

The Sheet is the working surface. Its Dashboard shows the current value, offer decision, processing path, and measurement ladder before the operator enters the queue. The remaining views keep plan choices, review states, original Clearbox dispositions, exact Reddit permalinks, buyer language, content direction, competitor evidence, disclosure review, and attribution receipts together.

| Plan Setup | Operator Console |
|:---:|:---:|
| [<img src="assets/gallery/client-pack-plan-setup.png" alt="Plan Setup with offer path, payer, and readiness selections">](https://docs.google.com/spreadsheets/d/100Q4e8ZW6xIHHk4GHzFO7ONmK_1MdNhBPi0Y4TngWjc/edit?gid=1428901161#gid=1428901161) | [<img src="assets/gallery/client-pack-operator-console.png" alt="Ranked Operator Console preserving Clearbox dispositions">](https://docs.google.com/spreadsheets/d/100Q4e8ZW6xIHHk4GHzFO7ONmK_1MdNhBPi0Y4TngWjc/edit?gid=318558601#gid=318558601) |
| **GEO and attribution receipts** | **Guided Notion value brief** |
| [<img src="assets/gallery/client-pack-geo-terms.png" alt="GEO Terms view with source URLs and separate receipt fields">](https://docs.google.com/spreadsheets/d/100Q4e8ZW6xIHHk4GHzFO7ONmK_1MdNhBPi0Y4TngWjc/edit?gid=401301384#gid=401301384) | [<img src="assets/gallery/client-pack-notion.png" alt="Guided Notion client value brief explaining the Sheet and next actions">](https://fierce-camelotia-1fa.notion.site/ClearboxGTM-Client-Value-Pack-Demo-Acme-Ops-3b91fb92bcd7818ca3dad03e0e21cbd0) |

The Notion page is the readable source of truth: what was uncovered, where the working data lives, what each view means, which decisions the client needs to make, and how success will be measured. The Sheet is the operational queue. Both can refresh in place at stable URLs. [Build the same pack →](skills/reddit-agency/CLIENT-VALUE-PACK.md)

## Build the eleven-view pack

The first command below is local-only: it reads the synthetic Clearbox and Clay fixtures and writes normalized JSON plus a Notion-ready Markdown brief. It does not post, DM, vote, or mark any opportunity complete.

```bash
git clone https://github.com/shawnla90/ClearboxGTM.git
cd ClearboxGTM
python3 -m venv .venv && source .venv/bin/activate
pip install -r engine/requirements.txt

python3 engine/build_client_pack.py \
  --ops examples/client-pack/clearbox-opportunities.sample.json \
  --analysis examples/client-pack/clay-analysis.sample.csv \
  --backend clay \
  --brand "Acme Ops" \
  --out /tmp/acme-client-pack
```

Use `--backend freckle` or `--backend baseloop` with the matching sanitized fixture to verify the same contract. Add `--publish-sheet` or `--publish-notion` only when you intentionally want to write those surfaces. For an account-scoped build, set `CLEARBOX_ACCOUNT_URL` and follow the [client value-pack guide](skills/reddit-agency/CLIENT-VALUE-PACK.md).

<details>
<summary><strong>Run the original offline market-signal pipeline</strong></summary>

The bundled offline path remains useful when you want to inspect the lower-level import → mine → score pipeline without a live Clearbox account. Its input is a synthetic Clearbox export with the same `id`, `kind`, and permalink contract as a real build:

Clone the repo and run the offline pipeline — no API key, no Google account needed for the first run:

```bash
git clone https://github.com/shawnla90/ClearboxGTM.git
cd ClearboxGTM/engine
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
bash run.sh --offline
```

Expected output:

```
1/5  creating the local database...
2/5  importing classified Clearbox opportunities...
     offline mode: using the bundled synthetic Clearbox export
     clearbox import: 12 opportunities read, 12 new, 12 total
3/5  mining buyer language + content topics...
     tagged 10 threads, extracted 23 buyer-language items, built 11 content topics
4/5  scoring every content topic 1 to 5...
     scored: 4 star x1, 2 star x7, 1 star x3
5/5  building the color-coded Google Sheet...
     (skipped: no Google OAuth token — run setup_oauth.py first)
done.
```

Connect Google Workspace (`python3 setup_oauth.py`) and re-run to get the sheet. To use your own market, configure the offer in Clearbox and import the complete opportunity export with `CLEARBOX_EXPORT=/path/to/export.json bash run.sh`. For a live account API build, use the [client value-pack builder](skills/reddit-agency/CLIENT-VALUE-PACK.md).

</details>

## What's in here

| Stage | What it does | You get | Where |
|---|---|---|---|
| **Onboard the offer** ★ | Domain in → researched offer pack out | Paste-ready blocks for the clearbox.to form, with sources | [`skills/clearbox-onboard/`](skills/clearbox-onboard/) |
| **Onboard a person** | Personalized route through the public playbook | A Notion doc with their real data and community rings | [`skills/reddit-onboard/`](skills/reddit-onboard/) |
| **Read the market** | Pull → mine → score buyer signals | Color-coded Google Sheet with A-D tiers and 4-dimension scores | [`engine/`](engine/) |
| **Build the client value pack** | Clearbox API → optional Freckle/Base Loop/Clay analysis → stable client surfaces | 11-view Google Sheet + guided Notion brief with exact permalinks | [`skills/reddit-agency/CLIENT-VALUE-PACK.md`](skills/reddit-agency/CLIENT-VALUE-PACK.md) |
| **Engage as a human** | Value-first reply drafting | Draft comments with per-item human approval gate | [`skills/reddit-engage/`](skills/reddit-engage/) |
| **Personalize the reply** | Three-variable model for specific, tension-creating comments | Icebreaker + poke-the-bear + pain-point per reply | [`skills/personalization/`](skills/personalization/) |
| **Batch the reply pass** | One gated ≤18-word reply template per classified op | Suggested Replies sheet tab + suggested_replies.json with GO/REVIEW/NO-REPLY gates | [`skills/reply-engine/`](skills/reply-engine/) |
| **Review company disclosure** | Exact Reddit-profile evidence first; search, thread, and handle matches stay in manual review | Verified company domain or candidate with evidence receipt | [`engine/unmask.py`](engine/unmask.py) |
| **Profile lookup** | Separate direct profile evidence, search candidates, absence, and lookup errors | Verdict, enrichment eligibility, exact URLs, domains, and bio | [`skills/profile-lookup/`](skills/profile-lookup/) |
| **Measure AI visibility** | GEO terms + live retrieval-visibility score | JSON of buyer questions with Exa retrieval status | [`skills/geo-visibility/`](skills/geo-visibility/) |
| **Win the long tail** | Buyer questions → content drafts | Blog + LinkedIn + Reddit pack with FAQ schema, drafted never posted | [`skills/longtail-content/`](skills/longtail-content/) |
| **Competitor intel** | Share of voice from classified Reddit ops | Competitor narrative with generated sentiment and openings | [`skills/competitor-intel/`](skills/competitor-intel/) |
| **Sentiment** | Three-class LLM sentiment on every opportunity | Per-op positive/neutral/negative with 1-5 score and reason | [`skills/sentiment/`](skills/sentiment/) |
| **Last 24 hours** | The morning briefing | Intent-ranked buyer signals from the last day | [`skills/last24/`](skills/last24/) |
| **Slack digest** | The daily client delivery | Slack message with engage threads, leads, competitor mentions | [`skills/slack-digest/`](skills/slack-digest/) |
| **Reddit proposals** | Pitch from buyer signals | Structured brief.json + readable BRIEF.md for a prospect | [`skills/reddit-proposal/`](skills/reddit-proposal/) |
| **Dataviz** | Reference architecture for GTM dashboards | Dark-theme Recharts palette, 3 standalone .tsx examples | [`skills/dataviz/`](skills/dataviz/) |
| **Attribution tracking** | Journey materialization pattern | First/last-touch attribution from local SQLite, no cookies | [`playbooks/attribution-tracking.md`](playbooks/attribution-tracking.md) |
| **Orchestrate enrichment** | The disclosure gate is the skill; pick your enrichment backend | Generic playbook + per-tool integration guides (Freckle, Clay, Base Loop, Deepline) | [`playbooks/orchestrate-enrichment.md`](playbooks/orchestrate-enrichment.md) |
| **Orchestrate off-platform** | Enrichment, GEO, share of voice, lead magnets, digest | Playbooks covering the full off-platform motion | [`playbooks/`](playbooks/) |
| **Sell it as a service** | The agency package | Buyer-signal Sheet, guided Notion value brief, deck, and measurement scorecard | [`skills/reddit-agency/`](skills/reddit-agency/) |
| **Win the agency client** | The reverse-uno method | A readout of their buyers, not a pitch | [`playbooks/win-an-agency-client.md`](playbooks/win-an-agency-client.md) |
| **Run multiple accounts safely** | Client ownership, named operators, disclosure controls | Five-level success scorecard with evidence ledger | [`skills/reddit-agency/MULTI-ACCOUNT-OPERATIONS.md`](skills/reddit-agency/MULTI-ACCOUNT-OPERATIONS.md) |
| **Configure plans and offers** | Keep account, offer, plan, identity, operator, and payer decisions separate | Guided Plan Setup with one offer per client and client-paid offer support | [`skills/reddit-agency/MULTI-ACCOUNT-OPERATIONS.md`](skills/reddit-agency/MULTI-ACCOUNT-OPERATIONS.md) |
| **Audit quality** | 5-dimension pick-quality rubric | Score any account's picks before the client does | [`playbooks/account-quality-benchmark.md`](playbooks/account-quality-benchmark.md) |
| **API examples** | Real API responses from Exa, Firecrawl, Apollo, MoltSets | What each enrichment step produces, with and without each API | [`examples/`](examples/) |
| **Integration guides** | Step-by-step Clay, n8n, Zapier, Make setup with Mermaid diagrams | Full workflow guides with cost comparison and reasoning node patterns | [`examples/integrations/`](examples/integrations/) |
| **Workflow diagrams** | Visual node graphs for enrichment waterfall and AEO content loop | Mermaid diagrams that render on GitHub | [`examples/workflows/`](examples/workflows/) |
| **Client market read** | What a real client deliverable looks like | The triage pattern, signal/win/enter triad, delivery to Notion | [`examples/client-market-read.md`](examples/client-market-read.md) |
| **Coverage waterfall** | Identify companies, apply the disclosure gate, enrich, grade, and deliver | Auditable route with manual-review and hold states | [`examples/workflows/enrichment-waterfall.md`](examples/workflows/enrichment-waterfall.md) |
| **Security** | The protection model | Scan gate, read-only DBs, siloed data, no auto-send | [`SECURITY.md`](SECURITY.md) |
| **Students** | Free semester of Clearbox Pro | Monthly group office hours, build-in-public track record | [`STUDENTS.md`](STUDENTS.md) |
| **Partners** | Referral and delivery tracks | Terms by email, method in the open | [`PARTNERS.md`](PARTNERS.md) |

## The playbooks

- [`how-to-win-on-reddit.md`](playbooks/how-to-win-on-reddit.md) — the thesis: do it real or not at all, karma is the currency, be natural ON Reddit and automate OFF it
- [`reddit-ai-visibility-loop.md`](playbooks/reddit-ai-visibility-loop.md) — the full open-source loop: post genuinely, AI reads Reddit, retrieval visibility compounds
- [`reddit-growth-seo.md`](playbooks/reddit-growth-seo.md) — how genuine Reddit presence compounds into organic search rankings and AI retrieval
- [`offer-context-onboarding.md`](playbooks/offer-context-onboarding.md) — the interview pattern as portable IP: offer context in, everything downstream inherits its quality
- [`automation-boundaries.md`](playbooks/automation-boundaries.md) — precisely what the machine may and may never do
- [`win-an-agency-client.md`](playbooks/win-an-agency-client.md) — the reverse-uno: show them their buyers instead of a pitch
- [`orchestrate-enrichment.md`](playbooks/orchestrate-enrichment.md) — direct profile disclosure, candidate review, retry states, and the pluggable enrichment backend
- [`orchestrate-freckle.md`](playbooks/orchestrate-freckle.md) — the Reddit-to-pipeline loop: Clearbox classifies, the disclosure gate holds, Freckle enriches, four surfaces receive
- [`orchestrate-deepline.md`](playbooks/orchestrate-deepline.md) — opportunity stream → orchestration substrate, with the trust model that keeps Reddit UGC as data, never instructions
- [`notion-command-center.md`](playbooks/notion-command-center.md) — one client-readable source of truth plus stable working surfaces
- [`skills/reddit-agency/CLIENT-VALUE-PACK.md`](skills/reddit-agency/CLIENT-VALUE-PACK.md) — automate the API-to-Sheet/Notion client pack with Freckle, Base Loop, or Clay
- [`account-quality-benchmark.md`](playbooks/account-quality-benchmark.md) — score any account's picks before the client does
- [`attribution-tracking.md`](playbooks/attribution-tracking.md) — the journey materialization pattern: first/last-touch attribution from local SQLite, no cookies, no third-party tracking

## Proof

**1.5M+** tracked views on one real account, with the karma, wins, era history, and signup-attribution tables generated straight from the tracking databases — never typed by hand. The numbers, their provenance rule, and the script that enforces it: [`proof/`](proof/). Live version at [shawnos.ai/reddit](https://shawnos.ai/reddit).

The stories behind the numbers — how genuine Reddit presence creates retrieval visibility without backlinks, and how inbound replies compound into pipeline: [`proof/stories/`](proof/stories/).

## Transparency

What actually built the user base — including what failed. The honest channel ranking, and a full postmortem of the cold-email machine that produced a handful of users despite a serious engineering investment: [`transparency/`](transparency/). The failures shaped this method as much as the wins did.

## The rules this repo will not let you break

1. **Nothing posts automatically.** Every send is a human pressing send. The automation reads, drafts, scores, and digests; it does not talk.
2. **The disclosure gate refuses to guess.** Only an exact company domain published on the author's own Reddit profile is automatically enrichment-eligible. Search, thread, and handle matches require human review.
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
