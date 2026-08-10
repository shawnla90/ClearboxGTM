# Security

How this repo protects your data, your clients' data, and your Reddit accounts.

This is not a checkbox. The security model is built into the architecture — read-only databases, a scan gate that blocks every release, a private denylist that lives outside the repo, and a data model where nothing leaves your machine unless you send it. The goal is to make thoughtful use of Reddit the default, not an afterthought.

## Your data stays yours

The engine runs on your infrastructure. Every database is a local SQLite file. Every engine script reads data and writes only to an explicit `--out` file or to `data/signals.db`. No cloud backend, no analytics pixel, no shared tenant database.

What this means in practice:

- **No cookies.** Attribution tracking (see `playbooks/attribution-tracking.md`) materializes journeys from a local events table. Your visitors are not tracked by a third party. You do not need to set up cookie consent because there are no third-party cookies.
- **No shared data.** When you run the engine for a client, their data stays in their workspace directory. Clearbox classifies Reddit content and returns the signal; the raw data, the scored results, and the client context never leave your disk.
- **Siloed by design.** Each client workspace is a separate directory with its own `data/signals.db`, its own ops files, its own output. The `.gitignore` excludes `workspaces/*` (except the example) so client data is never committed.

This is the point of running it yourself instead of using a hosted analytics platform: the join between Reddit usernames, CRM emails, and deal outcomes happens locally, under your control, and no vendor sits in the middle.

## What is protected

### `.gitignore`

The `.gitignore` excludes:

- **Secrets:** environment files, key files, `credentials.json`, `secrets.json`
- **Client data:** `workspaces/*` (except `workspaces/example-acme-pm/`), `social/`
- **Caches:** `__pycache__/`, `*.py[cod]`, `venv/`, `node_modules/`
- **Scratch:** `*.tmp`, `*.bak`, `scratch/`, `proof/.cache/`
- **IDE state:** `.vscode/`, `.idea/`, `*.swp`, `*.swo`
- **Local config:** `CLAUDE.local.md`

### The private denylist

The scan gate reads a denylist from a file that lives **outside** this repo — by design, because publishing the denylist would defeat it. The file contains client names, PII patterns, private identifiers, and terms that must never appear in a public commit. The gate hard-fails if the file is missing: you cannot release without it.

### The blocklist

A second denylist is read from a separate location if present, providing a layered defense. Both lists are checked independently.

## The scan gate

Every release passes a 12-check gate before the tag is pushed. The gate is a runnable bash script in `VERIFYING.md`. What it checks:

1. **Private denylist terms** — every term in the external denylist is grepped against the entire repo
2. **Second blocklist** — a separate list, if present
3. **Absolute home paths** — patterns that would leak local filesystem structure
4. **Environment file references** — `.env.*` patterns (except `.env.notion`, which is the Notion push tool's documented config)
5. **Private org tokens** — long alphanumeric strings after `org_`
6. **Views claim language** — the exact claim is "1.5M+"; the gate blocks any higher rounding
7. **PARTNERS.md numbers** — the partners page must contain no percentages, dollar amounts, or durations
8. **Evasion language** — the transparency folder teaches deliverability lessons, never filter circumvention
9. **Python compilation** — all `.py` files must compile cleanly
10. **Proof idempotency** — re-running the proof generator must produce zero diff
11. **Link resolution** — every relative link in playbooks must point to a real file
12. **Public URL health** — referenced URLs must return HTTP 200

Running the gate:

```
$ cd /path/to/ClearboxGTM
$ bash -c "$(sed -n '/^```bash/,/^```/p' VERIFYING.md | sed '1d;$d')"
SCAN GATE: all green
```

## Read-only databases

Every database connection in the engine opens read-only or writes only to a named output file:

```python
# proof/generate_proof.py — the proof pipeline
con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
```

The engine scripts that write to `signals.db` (`init_db.py`, `pull.py`, `mine.py`, `score.py`) write to their own local database, not to an upstream source. The client-service scripts (`geo.py`, `competitor.py`, `digest.py`, `sentiment.py`, `last24.py`, `proposal.py`) read from the database and write to JSON files via `--out`.

The dashboard (see `skills/dataviz/`) reads engine output — it never writes to any database.

## No auto-send

The automation boundary is absolute: the engine reads, drafts, scores, and digests. It does not post, reply, vote, or send DMs.

- `engine/digest.py` renders to a text file by default. The `--post` flag is required to send to Slack, and even then it uses an incoming webhook (push), not a bot token (pull).
- `skills/reddit-engage/` drafts reply angles but gates every one on explicit per-item human approval.
- `engine/content.py` scaffolds content packs but sets `dispatch: false` in the manifest.
- `engine/unmask.py` runs the disclosure gate by default — enrichment requires `--enrich`.

Every send is a human pressing send. This is rule #1 of the repo, and it is enforced structurally, not by policy.

## Terminal examples

### Running the scan gate

```
$ cd /path/to/ClearboxGTM
$ bash -c "$(sed -n '/^```bash/,/^```/p' VERIFYING.md | sed '1d;$d')"
SCAN GATE: all green
```

### Compiling all Python

```
$ python3 -m compileall -q engine proof scripts
$   (no output = all clean)
```

### Running the engine offline

```
$ cd engine
$ bash run.sh --offline
1/5  creating the local database...
2/5  pulling recent buyer threads from Reddit...
offline mode: seeding data/clearbox_export.json from the bundled sample
pulled 12 threads (6 relevant, 6 skipped) from sample export
3/5  mining buyer language + content topics...
tagged 6 threads, extracted 14 buyer-language items, built 8 content topics
4/5  scoring every content topic 1 to 5...
scored 8 topics: 2A 3B 2C 1D
5/5  building the color-coded Google Sheet...
(skipped: no Google OAuth token found — run setup_oauth.py first)
done. optional next step: python3 build_deck.py
```

### Checking a draft for slop

```
$ python3 engine/content.py check content/pack-01/linkedin.md
content check: content/pack-01/linkedin.md — clean (0 flags)
```

## Using Reddit the right way

This repo exists because there is a right way to do Reddit for GTM, and it is not what the growth-hack playbooks teach. The right way is: one real account, real replies written by a human who knows the product, karma earned by being useful, and everything else (research, classification, drafting, monitoring) automated off-platform.

The security model supports this: the automation boundary keeps the machine from ever posting. The disclosure gate refuses to guess who someone is. The recency gate keeps you in live conversations, not necro-posting. The scan gate keeps client names out of public code. And the data stays on your machine, so a compromised vendor cannot leak your client list or your Reddit strategy.

The thoughtfulness is the point. If you are going to show up in the places your buyers talk, do it in a way you would be comfortable explaining in public — because this repo already does.
