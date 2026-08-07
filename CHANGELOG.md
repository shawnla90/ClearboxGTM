# Changelog

All notable changes to this repo are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/); versions are announced via GitHub Releases.

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
