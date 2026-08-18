# Changelog

All notable changes to this repo are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/); versions are announced via GitHub Releases.

## [0.11.0] - 2026-08-18

The reply pass, codified. One gated, ≤18-word suggested-reply template per classified opportunity: the agent drafts, the script checks the hard cap and the slop gate, the human edits and posts. Every skipped thread carries its reason.

### Added

- **`skills/reply-engine/`**: the batch suggested-reply skill — the ≤18-word binding cap (15–18 target, `wc -w` semantics, rendered as `<N>/18` per draft), the deterministic GO/REVIEW/NO-REPLY gate table with per-op overrides, the `suggested_replies.json` contract, the rules-pinned Suggested Replies sheet tab schema, distilled voice rules, and worked examples with word counts including a NO-REPLY and an override case.
- **`engine/replies.py`**: `scaffold` builds the replies contract from the classified ops (slots only for gated-in ops), `check` enforces the word cap, empty slots, the shared anti-slop gate, no-links, and gate validity with a nonzero exit, `sheet` adds or replaces only the Suggested Replies tab on an existing client sheet (frozen rules + header rows, gate color coding), and `angles` exports digest-compatible `engage_angles.json` so the daily digest renders the drafted replies.
- **Wiring**: README stage row, how-to-win-on-reddit motion row, and reciprocal Related links from reddit-engage (which now declares the two reply modes), personalization, and slack-digest.

### Verification

- `tests/test_replies.py`: lane-to-gate mapping across both lane vocabularies, override precedence, `wc -w`-equivalent counting, cap enforcement at 18 vs 19 words, scaffold slot selection, and digest-compatible angles output.
- `skills/reply-engine` added to the Reddit-surface source check in VERIFYING.md.

## [0.10.1] - 2026-08-10

The Reddit engine now has one explicit opportunity source: Clearbox. This patch removes the legacy parallel discovery path so the public architecture, runnable starter, and reusable agency skill all teach the same source contract.

### Changed

- **Clearbox-only source contract**: `pull.py` imports a complete Clearbox export and requires the stable opportunity id, original `lead`/`engage`/`competitor` disposition, and exact Reddit permalink.
- **Safe offline path**: the bundled synthetic Clearbox export exercises the same contract without copying over a user's live export.
- **Aligned public guidance**: the engine guide, agency skill, AI-visibility playbook, proposal skill, examples, and GTM starter language now describe Clearbox as the authoritative opportunity source.
- **Profile evidence terminology**: the optional Playwright tier is described as a rendered-profile check, not as a Reddit collection path.

### Removed

- **Legacy discovery client and configuration**: removed the external Reddit discovery client, its environment-key path, and the keyword/subreddit source files.

### Verification

- Added importer tests for complete-export handling, truncation refusal, source-field validation, and exact permalink preservation.
- Added a release scan rule that rejects the retired source path from active Reddit engine surfaces.

## [0.10.0] - 2026-08-10

The client pack you can see: a redesigned Clearbox dashboard, a real synthetic eleven-view demonstration, a guided public Notion brief, and an animated end-to-end README walkthrough backed by reproducible HyperFrames source.

### Added

- **Branded client-pack dashboard**: the Sheet builder now renders a dense Clearbox dark/purple value surface with opportunity cards, offer and analysis coverage, signal-to-receipt workflow, evidence ladder, and guided next actions.
- **Verified public demonstration**: a view-only Acme Ops Sheet and guided Notion value brief generated from the repository's synthetic fixtures, with direct links from the README and gallery.
- **End-to-end motion walkthrough**: a short silent GIF, MP4, poster, frozen screenshots, shot plan, and checked HyperFrames composition showing Dashboard → Plan Setup → Operator Console → GEO receipts → Notion.
- **Repository roadmap**: product proof, broader `gtm-coding-agent` skill distribution, and the separately approval-gated launch campaign are explicit phases.
- **Dashboard regression coverage**: tests now assert the client-pack layout contract, its key values, evidence stages, twelve-column grid, and formatting request set.

### Changed

- **README visual story**: the outdated five-tab screenshot and generic Notion guide no longer represent the current product. The README now leads with the animated eleven-view workflow, live synthetic demos, focused working-view captures, and the local/API build paths.
- **Client-pack gallery**: every new asset traces to the synthetic fixture build and a verified public surface; the earlier screenshots remain only as release-history references.
- **Evidence language**: the opening product explanation now states that search retrieval, observed AI appearance, exact citation, engagement, and business outcome require separate receipts.
- **Coverage documentation**: removed the stale “coming in v0.6.0” marker and linked the shipped enrichment-waterfall workflow.

## [0.9.0] - 2026-08-10

Client value-pack automation: any Clearbox user can turn the account API's classified opportunities and exact Reddit permalinks into the same guided Google Sheet and Notion delivery pattern used for agency clients.

### Added

- **API-to-client-pack builder**: `engine/build_client_pack.py` pulls the account-scoped inbox or reads an export, preserves Clearbox dispositions and permalinks, and writes a normalized pack plus guided Notion-ready brief.
- **Three interchangeable analysis adapters**: sanitized Freckle JSON, Base Loop native JSON, and Clay CSV/JSON shapes normalize to the same output contract without replacing the original Clearbox disposition.
- **Eleven-view Sheet contract**: Dashboard, Plan Setup, Operator Console, Signals, Buyer Language, Content Topics, Competitor Sentiment, GEO Terms, Disclosure Audit, Research Workflow, and Action Legend, including decision and review dropdowns.
- **Reusable client value-pack guide**: build commands, Clay automation setup, stable Sheet/Notion ids, attribution receipts, truncation handling, client-safe language, and the release checklist.
- **Pack validation tests**: source disposition and permalink preservation, backend normalization, API read-only behavior, evidence fields, and Notion safety checks.

### Changed

- **reddit-agency skill**: now generates one readable Notion value brief plus one working Sheet, with a short TLDR for sending and the detailed workflow kept in the guide.
- **Agency access boundary**: the public skill and builder are self-serve; the operated agency offering and multi-offer enablement require contacting `partners@clearbox.to`.
- **Report automation boundary**: API pulls, analysis merges, Sheet rebuilds, and Notion refreshes may be scheduled; Reddit publishing and opportunity completion remain human-authorized.

## [0.8.1] - 2026-08-10

Client-facing Plan Setup correction: the agency pack now explains the decision a client needs to make without exposing backend billing mechanics, admin controls, processing workspaces, or run identifiers.

### Added

- **Guided decision fields**: Plan Setup requires dropdowns for the offer path, who pays, and readiness; operator queues use a Review Status dropdown.
- **Collapsible Notion guides**: the publisher supports toggle blocks so a client brief can explain every Sheet tab without becoming a wall of text.
- **Client-copy release gate**: the verification rules now reject provider-specific billing mechanics and internal workspace language in the public agency skill.

### Changed

- **reddit-agency 1.2.1**: client copy now says an agency can add a separate client offer and the client can pay for it. Internal payment-provider behavior stays in admin context.
- **Plan Setup language**: one offer per client remains the operating rule, expressed through audience, queue, reporting, payer, and readiness instead of backend implementation details.

## [0.8.0] - 2026-08-10

Plan and offer setup: the agency skill now carries the actual multi-offering product behavior into every client command center instead of stopping at workflow and account guidance.

### Added

- **Plan Setup requirement**: every agency command-center Sheet must recommend a path for the existing offer and explain when to add a separate offer for another client or service line.
- **Offer and payer boundary**: the operating guide now distinguishes the dashboard account, offer, plan, Reddit identity, operator, and payer decision.
- **Verified multi-offering behavior**: the guide records that an authorized user can add offers and a client can pay for the offer created for them.

### Changed

- **reddit-agency 1.2.0**: Step 0B and the delivery checklist now require a visible Plan Setup view and one isolated offer per client or genuinely separate service line.
- **README stage table**: added the plan and offer configuration stage to the public workflow map.
- **Profile lookup secret loading**: provider keys now come from the process environment only; the public engine no longer assumes private workstation databases or guesses secret-file paths.

## [0.7.0] - 2026-08-10

Profile lookup and orchestration: an evidence-bearing review gate that separates direct Reddit-profile disclosure, search candidates, no public evidence, and lookup errors, with per-tool integration guides for every enrichment backend.

### Added

- **Profile lookup skill**: four-tier waterfall that checks the author's own Reddit profile for exact disclosure evidence, then searches via Exa and DuckDuckGo for manual-review candidates. Every hit carries an evidence URL and excerpt; blocked checks remain lookup errors (`skills/profile-lookup/`, `engine/lib/profile_lookup.py`).
- **Orchestrate enrichment playbook**: the generic playbook describing the direct-disclosure gate, manual-review candidate path, retry path, and pluggable enrichment seam, with links to each tool's integration guide (`playbooks/orchestrate-enrichment.md`).
- **Base Loop integration guide**: typed workflow with AI-powered stages and explicit fields for lookup status, review verdict, enrichment eligibility, and evidence receipts (`examples/integrations/baseloop.md`).
- **Focused gate tests**: direct Reddit-profile disclosure, search-only candidates, no-evidence versus error states, and enrichment eligibility (`tests/test_profile_lookup.py`).

### Changed

- **engine/unmask.py**: only exact Reddit-profile company evidence can enter automatic enrichment. Search, thread-domain, and brand-handle matches are manual-review candidates. New `--profile` flag enables the full lookup waterfall; `enrich_domain()` remains the pluggable backend seam.
- **README stage table**: new rows for profile lookup and orchestration enrichment; "Resolve who it is" updated to reference the three-step gate.
- **README playbooks list**: orchestrate-enrichment.md added as the generic entry point above the tool-specific playbooks.

## [0.6.0] - 2026-08-09

Show me the workflow: step-by-step integration guides for Clay, n8n, Zapier, and Make with Mermaid diagrams, the enrichment waterfall and AEO content loop as visual node graphs, a real client deliverable example, and a live Firecrawl scrape of freckle.io.

### Added

- **Clay integration guide**: step-by-step HTTP column setup, Filter by kind, cost comparison (60-96% fewer credits), and Mermaid workflow diagram (`examples/integrations/clay.md`).
- **n8n integration guide**: HTTP Request, Switch node routing, AI Agent reasoning nodes with multi-source context (Clearbox + Firecrawl + Exa), two Mermaid diagrams (`examples/integrations/n8n.md`).
- **Zapier integration guide**: Schedule, Webhooks GET, Filter, routing to Sheets/Slack/HubSpot (`examples/integrations/zapier.md`).
- **Make integration guide**: HTTP module, Iterator, Router with Mermaid diagram (`examples/integrations/make.md`).
- **Enrichment waterfall diagram**: visual node graph from disclosure gate through Freckle, Apollo, MoltSets to T1/T2/SUPPRESS classification (`examples/workflows/enrichment-waterfall.md`).
- **AEO content loop diagram**: buyer questions to GEO terms to Exa retrieval check to content gaps to publish and re-check (`examples/workflows/aeo-content-loop.md`).
- **Client market read example**: sanitized structure of a real client deliverable showing the triage pattern, signal/win/enter triad, operating rules, and Notion delivery (`examples/client-market-read.md`).
- **Firecrawl freckle.io example**: real Firecrawl scrape of freckle.io (120,290 chars from one API call), the kind of output the onboarding research step consumes (`examples/firecrawl-freckle-site.json`).

### Changed

- **engine/README.md**: automation platform section now links to full step-by-step guides instead of single-paragraph descriptions, "future release" placeholder removed.
- **examples/README.md**: integration section links to full guides, new workflow diagrams section, client deliverable example section, freckle.io Firecrawl example added.
- **orchestrate-freckle.md**: added enrichment waterfall detail diagram (Mermaid) showing the disclosure gate to Apollo to MoltSets flow.
- **README stage table**: three new rows for integration guides, workflow diagrams, and client market read.

## [0.5.0] - 2026-08-09

The proof you can see: visual gallery, three proof stories with the LinkedIn outbound receipts, live API examples from Exa, Firecrawl, Apollo, and MoltSets, the Exa deep-dive, and the enrichment API table showing what each tool does with and without a key.

### Added

- **Visual proof gallery**: fresh Playwright screenshots of real outputs (Google Sheet, Notion operating guide) committed to `assets/gallery/`, with `scripts/screenshot.py` for reproducibility.
- **Reddit AI visibility loop playbook**: the full open-source loop -- post genuinely, AI reads Reddit, retrieval visibility compounds.
- **Reddit growth and SEO playbook**: how genuine Reddit presence compounds into organic search rankings and AI retrieval without backlink games.
- **Personalization skill**: the 3-variable model (icebreaker, poke-the-bear, pain-point) for thread-specific Reddit comment drafting.
- **Exa retrieval guide**: practical SDK guide for API key setup, query construction, interpreting retrieval results, the hard cap, and the Firecrawl companion section (`skills/geo-visibility/EXA-GUIDE.md`).
- **API examples**: real API responses from Exa, Firecrawl, Apollo, and MoltSets -- actual calls, not mocks -- with pipeline diagrams and automation platform integration guides (`examples/`).
- **LinkedIn outbound proof story**: 16-day outbound funnel (1,297 leads, 496 CRs, 238 accepted at 48%, 2 calls booked) with the exact messages revealed (`proof/stories/linkedin-outbound.md`).
- **No-backlinks-needed proof story**: AI citations come from being helpful, not from SEO link-building (`proof/stories/no-backlinks-needed.md`).
- **Inbound-from-content proof story**: genuine replies compound into pipeline -- 724 inbound replies, 25 tracked wins (`proof/stories/inbound-from-content.md`).
- **STORY.md**: founding story skeleton (content ships when ready).

### Changed

- **README overhauled**: "What it looks like" gallery with real screenshots, "Quick walkthrough" with expected output, restructured stage table with "You get" column, personalization row, API examples row, coverage waterfall forward reference, proof/stories link.
- **reddit-proposal skill enhanced**: Clearbox integration section with classify-to-pitch workflow diagram, "What the prospect sees" section, cross-links to sentiment.
- **geo-visibility skill extended**: "Deep dive" link to the new Exa guide, "Other enrichment tools" section covering Firecrawl.
- **Signup integration**: `open https://clearbox.to` added as explicit final step in clearbox-onboard skill and onboarding prompt.
- **engine/README.md**: first-time setup callout, build-vs-buy CTA moved earlier, enrichment API table (with/without comparison for Exa, Firecrawl, Apollo, MoltSets), automation platform integration guides (Clay, n8n, Zapier, Make).

## [0.4.0] - 2026-08-09

The skills drop: six new skills, three new engine scripts, a security showcase, and the attribution tracking pattern.

### Added

- **Competitor intel skill**: share of voice, generated sentiment, and where the opening is — from classified Reddit ops. Includes FACTCHECK.md enforcing the classification-not-counting rule. Wraps `engine/competitor.py` + the new `engine/sentiment.py`.
- **Sentiment skill**: three-class (positive/neutral/negative) thread-level sentiment classification, LLM-powered with heuristic fallback. Output feeds competitor-intel and the daily digest.
- **Dataviz skill**: reference architecture for GTM dashboards with Recharts — the dark-theme palette, the component patterns, and three standalone `.tsx` examples (ChannelBars, ImpressionsLine, FunnelBars) plus a bootstrapping guide.
- **Last 24 hours skill**: the morning briefing — freshest buyer signals from the last day, ranked by intent and engagement.
- **Reddit proposal skill**: pitch materials for a prospect from their buyers' Reddit conversations. The reverse-uno applied to a single prospect.
- **Slack digest skill**: wraps `engine/digest.py` as a proper skill with setup, chaining, and the render-vs-post boundary.
- **Three engine scripts**: `sentiment.py` (thread-level sentiment from classified ops), `last24.py` (24h buyer signal feed), `proposal.py` (Reddit-sourced pitch brief).
- **SECURITY.md**: the protection model — siloed-by-design architecture (no cookies, no shared backend, local SQLite), the scan gate explained, read-only databases, the no-auto-send boundary, terminal examples, and the "using Reddit the right way" thesis.
- **Attribution tracking playbook**: the journey materialization pattern — identity spine, events table, first/last-touch channel attribution, and the "your data stays yours" architecture. Documents how the proof pipeline's signup-attribution tables are produced.

### Changed

- README expanded with 8 new stage table rows (6 skills, attribution playbook, security doc) and rule #6 ("your data stays yours").
- ENGINE.md expanded with 3 new client-service modules.
- `engine/digest.py` now credits Lucas for the original daily digest pattern.

## [0.3.0] - 2026-08-07

The flagship drop: release hygiene, real branding, generated proof, transparency, and three new tracks (agency, students, partners).

### Added

- **Generated-not-typed proof pipeline**: `proof/generate_proof.py` reads the tracking databases read-only and rewrites the stats block in `proof/README.md` between markers — with hard assertions on freshness (≤14 days), the exact views-claim language, and privacy. Includes the signup-attribution and inbound-engagement tables. No statistic in this repo is typed by hand anymore.
- **Transparency**: `transparency/` — the honest channel ranking of what actually built the user base ([what-actually-worked.md](transparency/what-actually-worked.md)) and a full cold-email postmortem with the deliverability findings worth keeping ([cold-email-postmortem.md](transparency/cold-email-postmortem.md)).
- **Offer-context onboarding as portable IP**: [`playbooks/offer-context-onboarding.md`](playbooks/offer-context-onboarding.md) — the interview pattern behind `clearbox-onboard`, generalized so any research agent can run it and any downstream system can consume the pack. `clearbox-onboard` bumped to 1.1.0 with the cross-links.
- **Agency track**: [`playbooks/win-an-agency-client.md`](playbooks/win-an-agency-client.md) — the reverse-uno method: lead with a readout of the client's buyers, not a pitch.
- **Students**: [`STUDENTS.md`](STUDENTS.md) — a free semester of Clearbox Pro plus monthly group office hours for students who build in public, with the semester arc that produces a public track record.
- **Partners**: [`PARTNERS.md`](PARTNERS.md) — referral and delivery tracks; terms by email.
- **Two new skills**: [`skills/geo-visibility/`](skills/geo-visibility/) (GEO term plan + retrieval-visibility score, wrapping `engine/geo.py`) and [`skills/longtail-content/`](skills/longtail-content/) (buyer question → checked three-draft attribution pack, wrapping `engine/content.py`).
- **Automation boundaries**: [`playbooks/automation-boundaries.md`](playbooks/automation-boundaries.md) — precisely what the machine may and may never do.
- **Release hygiene**: `RELEASING.md`, `VERIFYING.md` (the provenance rule, language boundaries, and the runnable scan gate every release passes), and a CI workflow that drafts a release when skills, playbooks, engine, proof, or transparency change.
- **Brand assets**: banner, social preview, and the official logo pack in `assets/`.

### Changed

- README rebuilt as the flagship map: the full stage table (onboarding featured as the differentiator), transparency section, and consolidated related links.
- The public multi-account guide on Notion and this repo now link to each other bidirectionally.

## [0.2.0] - 2026-08-06

### Added

- A research-backed multi-account operations guide for agencies, with client ownership, named-operator, credential, browser, IP/VPN, disclosure, coordination, ramp, incident, and offboarding controls.
- A dated evidence ledger separating official facts, public practitioner observations, Clearbox rules, fiction, and unproven claims.
- A five-level success model covering Reddit artifact health, search discovery, observed AI answer receipts, retrieval visibility, and business outcomes.
- A reusable CSV receipt schema for repeated buyer-question benchmarks across answer engines.
- A required universal multi-account module in every future `reddit-agency` command center.

### Changed

- Exa checks are now labeled `retrieval_visibility` throughout the engine. They are no longer presented as proof of an AI answer mention or citation.
- Agency positioning now treats AI visibility as a measured outcome with exact receipts, not a guaranteed consequence of posting.

## [0.1.0] - 2026-08-06

### Added

- **Four skills**: `clearbox-onboard` (domain → researched offer pack, with the pastable `PROMPT.md` for any coding agent), `reddit-onboard` (personalized route through the public playbook, pushed to Notion), `reddit-engage` (value-first reply drafting with a per-item human gate), `reddit-agency` (the win-a-client package: sheet, deck, command center).
- **The engine**: the full pull → mine → score → unmask → geo → competitor → content → digest → sheet pipeline, self-contained, env-var configured.
- **Five playbooks**: how-to-win-on-reddit (the thesis), orchestrate-freckle (the Reddit-to-pipeline loop with real gate numbers), orchestrate-deepline (opportunity orchestration with the UGC trust model), notion-command-center, account-quality-benchmark.
- **Proof**: 1.5M+ tracked views on one account, generated-not-typed, with the disclosure-gate numbers from a live run.
- `scripts/push_notion.py` — markdown → real Notion pages with stable URLs.
