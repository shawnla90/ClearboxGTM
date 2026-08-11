# The Notion command center

Every client engagement ships with one readable Notion value brief as the client-facing source of truth, plus one linked Google Sheet as the working surface. The page leads with what was uncovered, where the value is, how to work the Sheet, which offer path is recommended, and how success is measured. Internal processing surfaces stay internal. The client starts on one page and never has to guess which document is current.

Use [`../skills/reddit-agency/CLIENT-VALUE-PACK.md`](../skills/reddit-agency/CLIENT-VALUE-PACK.md) and `../engine/build_client_pack.py` to generate both surfaces from the same normalized Clearbox opportunity set.

## Required agency module

Every agency command center includes the universal **Running multiple Reddit accounts for clients** guide. The same page is reused for every client so corrections to Reddit rules, disclosure guidance, and measurement standards have one stable source of truth.

Until the public Notion URL is inserted below, an agency package is not ready to send.

- Canonical source: [`../skills/reddit-agency/MULTI-ACCOUNT-OPERATIONS.md`](../skills/reddit-agency/MULTI-ACCOUNT-OPERATIONS.md)
- Evidence ledger: [`../skills/reddit-agency/MULTI-ACCOUNT-EVIDENCE.md`](../skills/reddit-agency/MULTI-ACCOUNT-EVIDENCE.md)
- Public Notion guide: [Running multiple Reddit accounts for clients](https://fierce-camelotia-1fa.notion.site/Clearbox-Running-Multiple-Reddit-Accounts-for-Clients-3b51fb92bcd78187a212de323c577399)

The client command center must link the public Notion guide. The private evidence ledger can be linked when a client wants the full fact-check trail.

## Required value-pack structure

The page must contain, in this order:

1. The recommendation and working Sheet link.
2. A short "Start here" sequence.
3. The current opportunity, disposition, tier, and lane counts.
4. The highest-priority opportunities with exact Reddit permalinks.
5. Compact toggles explaining all eleven Sheet views.
6. The API and optional Freckle/Base Loop/Clay workflow in client-safe language.
7. Plan and offer guidance.
8. Artifact, search, AI-answer, exact-citation, and business-outcome measurement.
9. The next working session and Sheet link again.

The page does not need every Sheet row. The Sheet is the offload and operating surface; the Notion page explains the value and how to use it.

## Automated refresh

The builder can pull `GET /inbox?status=all` from the account-scoped Clearbox API, preserve each `kind` disposition and exact `url`, merge optional Freckle, Base Loop, or Clay analysis, and rebuild the Sheet and Notion page in place. Supply the existing Sheet id and Notion page id so both client URLs remain stable.

The automation may refresh data and documents. It must not publish Reddit replies, vote, send DMs, or mark opportunities complete without a human-authorized action.

## The mechanic

`../scripts/push_notion.py` converts a markdown file into a real Notion page:

```bash
python3 scripts/push_notion.py --file doc.md --title "Acme · Reddit" --parent <page_id>
```

What it handles: headings, fenced code, **colored callouts** (`> 🎯 text` — color inferred from the emoji), `- [ ]` checkboxes, `::: bookmark <url>` cards, external images, **uploaded local images** (`::: image_upload path | caption`), columns, bullets, dividers, inline bold/code/links.

## The rules that keep links stable

- **Reuse page ids.** Re-publish with `--inplace <page_id>`: it deletes the page's blocks and re-appends, so a shared URL never breaks. A rebuilt doc with a new URL is a broken promise.
- **Verify every link resolves** to a real, shared page before the command center ships. Phantom references are the fastest way to lose trust.
- **The integration must be shared into the parent page** (Notion UI → page → Connections) or the API 401s.
- **Share-to-web is a manual UI toggle.** The API cannot publish a page publicly. Flip it yourself, then send.

## Doc conventions

- The command center is plain reading: what value was uncovered, what to do next, and what each Sheet view means.
- Client-facing docs never reference scripts, filenames, or commands. The doc is the instruction; the data "can be re-queried and rebuilt on demand."
- Callout colors carry meaning consistently: 🎯 the point, ⚡ the mechanism, 🔴 the warning, 💸 the money.
- The public method is available in this repo. Agency access and multi-offer enablement currently require contacting `partners@clearbox.to`.
