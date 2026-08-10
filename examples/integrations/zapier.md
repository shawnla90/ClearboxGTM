# Zapier integration guide

Catch the Clearbox inbox with a scheduled Zap and route classified opportunities to Google Sheets, Slack, HubSpot, or any Zapier-connected app.

## What this does

A Zap pulls the Clearbox inbox on a schedule, filters by `kind`, and routes each opportunity to the right destination. Simpler than the n8n flow — no AI reasoning nodes, no multi-step enrichment — but covers the 80% case: leads go to a sheet or CRM, competitor mentions go to Slack, engage ops go to a reply queue.

## Prerequisites

- A Zapier account (free tier works for low-volume inboxes)
- A Clearbox account with a configured inbox ([clearbox.to](https://clearbox.to))
- Your inbox token

## Step-by-step setup

### 1. Trigger: Schedule by Zapier

| Setting | Value |
|---------|-------|
| Trigger | Schedule by Zapier |
| Frequency | Every 6 hours |

### 2. Action: Webhooks by Zapier (GET)

| Setting | Value |
|---------|-------|
| Action | GET |
| URL | `https://api.clearbox.to/a/{YOUR_TOKEN}/inbox` |
| Headers | `User-Agent`: `Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)` |

### 3. Looping: run for each opportunity

Use **Looping by Zapier** to iterate over `opportunities[]`. Each loop iteration processes one op.

### 4. Filter by kind

Add a **Filter** step:

| Path | Route to |
|------|----------|
| `kind` = `lead` | Google Sheets row or HubSpot contact |
| `kind` = `engage` | Slack message with thread link |
| `kind` = `competitor` | Email digest or Slack alert |

### 5. Lead destination

**Google Sheets** — append a row:

| Column | Value |
|--------|-------|
| Op ID | `{{id}}` |
| Kind | `{{kind}}` |
| Summary | `{{summary}}` |
| Subreddit | `{{subreddit.name}}` |
| URL | `{{url}}` |
| Posted | `{{posted_at}}` |

**HubSpot** — create a note or task on a contact/company record if the lead matches an existing CRM record.

### 6. Engage destination

**Slack** — post to `#reddit-engage`:

```
New engage signal in r/{{subreddit.name}}:
{{summary}}
Thread: {{url}}
```

### 7. Competitor destination

**Slack** — post to `#competitor-watch`:

```
Competitor mention: {{summary}}
Thread: {{url}}
```

Or use **Digest by Zapier** to batch competitor mentions into a daily email.

## Limitations

- Zapier's free tier limits the number of Zaps and tasks per month. A 24-op inbox polled 4x/day = ~96 tasks/day.
- No AI reasoning nodes. For prospect briefs and reply drafts, use the [n8n integration](./n8n.md) instead.
- Same pull-only API limitation: no webhooks, schedule-based polling only.

## Related

- [`./clay.md`](./clay.md) — Clay HTTP column (enrichment-heavy)
- [`./n8n.md`](./n8n.md) — n8n flow with AI reasoning nodes
- [`./make.md`](./make.md) — Make (Integromat) equivalent
- [`../README.md`](../README.md) — API shape and enrichment providers
