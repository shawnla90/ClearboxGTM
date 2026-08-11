"""Pure normalization and rendering for the Clearbox client value pack.

Clearbox owns the source opportunity, disposition, and Reddit permalink. Optional
Freckle, Base Loop, or Clay rows add analysis without replacing that source record.
The functions in this module do no network or Google/Notion writes, which keeps the
contract easy to test and reuse from other automation tools.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Optional, Union


DISPOSITIONS = {"lead", "engage", "competitor"}
BACKENDS = {"none", "freckle", "baseloop", "clay"}
TIER_ORDER = {"A": 0, "B": 1, "C": 2, "D": 3, "UNSCORED": 4}

TAB_GUIDANCE = [
    ("Dashboard", "The answer first", "Shows the opportunity mix, priority picture, strongest plays, and recommended offer path."),
    ("Plan Setup", "Choose the commercial path", "Records the offer path, who pays, and whether the team is ready."),
    ("Operator Console", "Work the queue", "Shows where to go, what to do, why the row matters, and its review status."),
    ("Signals", "Inspect the source evidence", "Keeps the original Clearbox disposition, exact buyer language, timing, and permalink."),
    ("Buyer Language", "Use the words buyers use", "Organizes pain, questions, jobs, desired outcomes, and objections."),
    ("Content Topics", "Answer recurring questions", "Turns buyer conversations into source-backed content and reply directions."),
    ("Competitor Sentiment", "Read category pressure", "Separates competitor-classified opportunities from generated sentiment and positioning notes."),
    ("GEO Terms", "Measure search and AI visibility", "Stores buyer questions and receipts while keeping retrieval, answers, citations, and outcomes separate."),
    ("Disclosure Audit", "Apply the enrichment gate", "Keeps direct disclosure, manual-review candidates, no evidence, and lookup errors distinct."),
    ("Research Workflow", "Audit the recommendation", "Shows the client-safe source and analysis fields without exposing private workspaces or run identifiers."),
    ("Action Legend", "Use one vocabulary", "Defines dispositions, tiers, lanes, evidence levels, and review states."),
]


def load_payload(path: Union[str, Path]) -> Any:
    """Load JSON or CSV input. CSV is useful for a Clay table export."""
    source = Path(path)
    if source.suffix.lower() == ".csv":
        with source.open(newline="", encoding="utf-8-sig") as handle:
            return list(csv.DictReader(handle))
    return json.loads(source.read_text())


def _norm_key(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()


def _flat(row: dict) -> dict:
    cells = row.get("cells")
    return cells if isinstance(cells, dict) else row


def _index(row: dict) -> dict[str, Any]:
    return {_norm_key(key): value for key, value in _flat(row).items()}


def _pick(index: dict[str, Any], *names: str, default: Any = "") -> Any:
    for name in names:
        key = _norm_key(name)
        if key in index and index[key] not in (None, ""):
            return index[key]
    return default


def _number(value: Any) -> Optional[float]:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _rows(payload: Any, *, analysis: bool = False) -> list[dict]:
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if not isinstance(payload, dict):
        raise ValueError("input must be a JSON object, JSON array, or CSV")
    keys = ("rows", "outputs", "results", "entries") if analysis else ("opportunities", "rows", "results")
    for key in keys:
        value = payload.get(key)
        if isinstance(value, list):
            return [row for row in value if isinstance(row, dict)]
    if analysis and isinstance(payload.get("data"), list):
        return [row for row in payload["data"] if isinstance(row, dict)]
    raise ValueError(f"could not find a row array in input; checked {', '.join(keys)}")


def normalize_clearbox(payload: Any) -> tuple[list[dict], dict]:
    """Normalize an account API response or exported opportunity list."""
    raw_rows = _rows(payload)
    meta = {
        "counts": payload.get("counts", {}) if isinstance(payload, dict) else {},
        "truncated": bool(payload.get("truncated")) if isinstance(payload, dict) else False,
        "returned": len(raw_rows),
    }
    output: list[dict] = []
    seen: set[str] = set()
    for raw in raw_rows:
        idx = _index(raw)
        op_id = str(_pick(idx, "id", "op id", "opportunity id", "external id")).strip()
        if not op_id:
            raise ValueError("every Clearbox opportunity needs an id")
        if op_id in seen:
            raise ValueError(f"duplicate Clearbox opportunity id: {op_id}")
        seen.add(op_id)

        disposition = str(_pick(idx, "kind", "disposition", "label", "signal type")).lower().strip()
        if disposition not in DISPOSITIONS:
            raise ValueError(f"opportunity {op_id} has unsupported disposition: {disposition!r}")

        subreddit = raw.get("subreddit")
        if isinstance(subreddit, dict):
            subreddit = subreddit.get("name") or subreddit.get("display_name") or ""
        if not subreddit:
            subreddit = _pick(idx, "subreddit", "community")
        source_url = str(_pick(idx, "url", "permalink", "reddit url", "source url")).strip()
        if not source_url.startswith(("http://", "https://")):
            raise ValueError(f"opportunity {op_id} is missing an exact source permalink")

        output.append({
            "op_id": op_id,
            "source_disposition": disposition,
            "status": str(_pick(idx, "status", default="todo")),
            "subreddit": str(subreddit or ""),
            "author": str(_pick(idx, "author", "reddit author")),
            "summary": str(_pick(idx, "summary")),
            "snippet": str(_pick(idx, "snippet", "reddit text", "text")),
            "source_url": source_url,
            "posted_at": str(_pick(idx, "posted at", "posted_at", "created at", "created_utc")),
            "thread_last_active_at": str(_pick(idx, "thread last active at", "thread_last_active_at")),
            "thread_id": str(_pick(idx, "thread id", "thread_id")),
        })
    return output, meta


ANALYSIS_FIELDS: dict[str, tuple[str, ...]] = {
    "analysis_disposition": ("kind", "disposition", "signal type"),
    "tier": ("tier",),
    "priority_score": ("priority score", "ai priority score", "baseline priority", "total score"),
    "total_score": ("total score", "priority score", "ai priority score"),
    "intent_score": ("intent score",),
    "demand_score": ("demand score",),
    "competitive_fit_score": ("competitive fit score", "offer fit score"),
    "engagement_score": ("engagement score",),
    "action_lane": ("action lane", "ai lane", "baseline lane", "lane"),
    "buyer_language": ("buyer language", "ai buyer language", "pain quote", "reddit text"),
    "buyer_question": ("buyer question", "title", "job to be done"),
    "job_to_be_done": ("job to be done",),
    "desired_outcome": ("desired outcome",),
    "objection_or_risk": ("objection or risk",),
    "content_topic": ("content topic", "content theme"),
    "content_angle": ("content angle",),
    "helpful_reply_angle": ("helpful reply angle", "reply angle"),
    "analysis_reason": ("analysis reason", "ai rationale", "baseline reason"),
    "operator_action": ("operator action", "ai team play"),
    "outreach_safety": ("outreach safety",),
    "competitor_name": ("competitor name", "competitor mentions"),
    "competitor_sentiment": ("competitor sentiment", "competitor signal"),
    "search_query": ("search query",),
    "measurement_stage": ("measurement stage",),
    "recommended_identity": ("recommended identity",),
    "disclosure_status": ("disclosure status", "disclosure state", "profile lookup status"),
    "profile_review_verdict": ("profile review verdict",),
    "disclosure_evidence": ("disclosure evidence", "profile bio evidence", "profile bio / evidence"),
    "profile_evidence_urls": ("profile evidence urls", "other public links", "reddit profile url"),
    "enrichment_eligibility": ("enrichment eligibility",),
}


def normalize_analysis(payload: Any, backend: str) -> dict[str, dict]:
    """Normalize Freckle, Base Loop, or Clay rows into one optional overlay."""
    backend = backend.lower().replace(" ", "")
    if backend == "base-loop":
        backend = "baseloop"
    if backend not in BACKENDS - {"none"}:
        raise ValueError(f"backend must be freckle, baseloop, or clay; received {backend!r}")
    output: dict[str, dict] = {}
    for raw in _rows(payload, analysis=True):
        idx = _index(raw)
        op_id = str(_pick(idx, "opportunity id", "op id", "id", "clearbox id")).strip()
        if not op_id:
            raise ValueError(f"{backend} analysis row is missing the Clearbox opportunity id")
        if op_id in output:
            raise ValueError(f"duplicate {backend} analysis row for opportunity {op_id}")
        row = {"analysis_backend": backend}
        for field, aliases in ANALYSIS_FIELDS.items():
            value = _pick(idx, *aliases)
            if value not in (None, ""):
                row[field] = value
        for field in ("priority_score", "total_score", "intent_score", "demand_score", "competitive_fit_score", "engagement_score"):
            if field in row:
                row[field] = _number(row[field])
        output[op_id] = row
    return output


def _derived_tier(row: dict) -> str:
    tier = str(row.get("tier") or "").upper().strip()
    if tier in {"A", "B", "C", "D"}:
        return tier
    priority = _number(row.get("priority_score"))
    if priority is not None and 1 <= priority <= 5:
        return "A" if priority >= 5 else "B" if priority >= 4 else "C" if priority >= 3 else "D"
    return "UNSCORED"


def merge_rows(clearbox_rows: list[dict], analysis_by_id: Optional[dict[str, dict]] = None) -> tuple[list[dict], dict]:
    analysis_by_id = analysis_by_id or {}
    merged: list[dict] = []
    conflicts = 0
    for source in clearbox_rows:
        row = dict(source)
        analysis = analysis_by_id.get(source["op_id"], {})
        row.update(analysis)
        proposed = str(row.get("analysis_disposition") or "").lower().strip()
        conflict = bool(proposed and proposed != source["source_disposition"])
        row["disposition_conflict"] = conflict
        conflicts += int(conflict)
        row["tier"] = _derived_tier(row)
        row["action_lane"] = str(row.get("action_lane") or {
            "lead": "lead_review",
            "engage": "engage_now",
            "competitor": "competitor_watch",
        }[source["source_disposition"]])
        row["review_status"] = "not_started"
        row["analysis_backend"] = row.get("analysis_backend") or "clearbox_only"
        merged.append(row)

    def sort_key(row: dict) -> tuple:
        score = _number(row.get("total_score")) or _number(row.get("priority_score")) or 0
        return (TIER_ORDER.get(row["tier"], 9), -score, row.get("op_id", ""))

    merged.sort(key=sort_key)
    for rank, row in enumerate(merged, 1):
        row["rank"] = rank
    return merged, {
        "analysis_rows": len(analysis_by_id),
        "matched_analysis_rows": sum(1 for row in clearbox_rows if row["op_id"] in analysis_by_id),
        "unmatched_analysis_rows": len(set(analysis_by_id) - {row["op_id"] for row in clearbox_rows}),
        "disposition_conflicts": conflicts,
    }


def _clean(value: Any) -> Any:
    return "" if value is None else value


def _project(rows: Iterable[dict], fields: list[str]) -> list[dict]:
    return [{field: _clean(row.get(field)) for field in fields} for row in rows]


def build_pack(
    brand: str,
    rows: list[dict],
    *,
    api_meta: Optional[dict] = None,
    merge_meta: Optional[dict] = None,
    existing_offer: Optional[str] = None,
    plan_path: str = "Keep current offer",
    payer: str = "Decision together",
    readiness: str = "Reviewing",
) -> dict:
    """Build the backend-neutral value-pack model and all eleven Sheet views."""
    if not brand.strip():
        raise ValueError("brand is required")
    api_meta = api_meta or {}
    merge_meta = merge_meta or {}
    dispositions = Counter(row["source_disposition"] for row in rows)
    tiers = Counter(row["tier"] for row in rows)
    lanes = Counter(row["action_lane"] for row in rows)
    backends = sorted({row["analysis_backend"] for row in rows})

    plan_rows = [
        {"setting": "Offer path", "selection": plan_path, "guidance": "Keep the current offer, add a separate client offer, or upgrade capacity and add a client."},
        {"setting": "Who pays", "selection": payer, "guidance": "Record whether the agency, client, or both will decide together."},
        {"setting": "Readiness", "selection": readiness, "guidance": "Record whether the team is reviewing, ready to configure, or asking for guidance."},
    ]

    tabs = {
        "Plan Setup": plan_rows,
        "Operator Console": _project(rows, [
            "rank", "op_id", "source_disposition", "tier", "action_lane", "review_status", "subreddit",
            "posted_at", "summary", "helpful_reply_angle", "operator_action", "outreach_safety", "source_url",
        ]),
        "Signals": _project(rows, [
            "op_id", "source_disposition", "status", "subreddit", "author", "posted_at", "thread_last_active_at",
            "summary", "snippet", "source_url",
        ]),
        "Buyer Language": _project(rows, [
            "op_id", "source_disposition", "buyer_language", "buyer_question", "job_to_be_done", "desired_outcome",
            "objection_or_risk", "source_url",
        ]),
        "Content Topics": _project(rows, [
            "op_id", "tier", "content_topic", "content_angle", "buyer_question", "helpful_reply_angle", "source_url",
        ]),
        "Competitor Sentiment": _project(
            [row for row in rows if row["source_disposition"] == "competitor" or row.get("competitor_name")],
            ["op_id", "competitor_name", "competitor_sentiment", "analysis_reason", "source_url"],
        ),
        "GEO Terms": _project(rows, [
            "op_id", "search_query", "buyer_question", "measurement_stage", "source_url",
            "benchmark_run", "answer_engine", "run_date", "prompt", "usable_receipt", "brand_named",
            "answer_receipt_url", "reddit_cited", "exact_reddit_artifact_cited", "google_thread_found",
            "google_exact_comment_phrase_found", "retrieval_visibility", "reddit_referral_sessions",
            "ai_referral_sessions", "qualified_conversations", "sourced_opportunities", "influenced_pipeline",
            "revenue", "notes",
        ]),
        "Disclosure Audit": _project(
            [row for row in rows if row["source_disposition"] == "lead"],
            ["op_id", "author", "disclosure_status", "profile_review_verdict", "enrichment_eligibility",
             "disclosure_evidence", "profile_evidence_urls", "source_url"],
        ),
        "Research Workflow": _project(rows, [
            "op_id", "source_disposition", "analysis_backend", "tier", "priority_score", "intent_score", "demand_score",
            "competitive_fit_score", "engagement_score", "action_lane", "analysis_reason", "disposition_conflict", "source_url",
        ]),
        "Action Legend": [
            {"field": "lead", "meaning": "Clearbox classified a buying, comparison, or recommendation signal. Apply the disclosure gate before enrichment."},
            {"field": "engage", "meaning": "A useful public reply is the next action. A human reviews and publishes."},
            {"field": "competitor", "meaning": "A competitor or alternative is relevant. Monitor the conversation and use it as market evidence."},
            {"field": "Tier A/B/C/D", "meaning": "Analysis priority. It never replaces the original Clearbox disposition."},
            {"field": "retrieval visibility", "meaning": "A directional search result, not proof of an AI answer or citation."},
            {"field": "observed AI answer", "meaning": "A dated answer receipt with engine and prompt."},
            {"field": "exact citation", "meaning": "The captured answer cites the exact Reddit artifact URL."},
            {"field": "business outcome", "meaning": "A source-linked reply, referral, meeting, opportunity, pipeline, or revenue event."},
        ],
    }

    return {
        "brand": brand.strip(),
        "existing_offer": (existing_offer or brand).strip(),
        "plan": {"path": plan_path, "payer": payer, "readiness": readiness},
        "metrics": {
            "total": len(rows),
            "dispositions": dict(dispositions),
            "tiers": dict(tiers),
            "lanes": dict(lanes),
            "analysis_backends": backends,
            "api_counts": api_meta.get("counts", {}),
            "api_truncated": bool(api_meta.get("truncated")),
            **merge_meta,
        },
        "tabs": tabs,
        "rows": rows,
    }


def render_notion_markdown(pack: dict, sheet_url: str = "") -> str:
    """Render the guided client brief. Keep processing details out of this surface."""
    brand = pack["brand"]
    metrics = pack["metrics"]
    dispositions = metrics["dispositions"]
    tiers = metrics["tiers"]
    rows = pack["rows"]
    top = rows[:7]
    backend_labels = {"clearbox_only": "Clearbox only", "freckle": "Freckle", "baseloop": "Base Loop", "clay": "Clay"}
    backend_names = [backend_labels.get(name, name) for name in metrics["analysis_backends"]]
    workflow = ", ".join(backend_names) if backend_names else "Clearbox"
    lines = [
        f"# {brand} x Clearbox: GTM Value Brief",
        "",
        f"> 🎯 **Recommendation:** keep {pack['existing_offer']} as its own offer. Add a separate offer when another client or genuinely different service line is ready. Contact **partners@clearbox.to** for agency access or multi-offer enablement.",
        "",
    ]
    if sheet_url:
        lines += [f"::: bookmark {sheet_url}", ""]
    lines += [
        "## Start here",
        "",
        "1. Open **Dashboard** to see what was uncovered.",
        "2. Open **Plan Setup** and choose the offer path, who pays, and readiness.",
        "3. Open **Operator Console**, start with Tier A, and update **Review Status** as each row moves.",
        "4. Use the remaining tabs for source evidence, buyer language, content direction, visibility checks, and disclosure review.",
        "",
        f"## What {brand} has now",
        "",
        f"- **{metrics['total']} current opportunities organized into one working queue.**",
        f"- **{dispositions.get('lead', 0)} lead, {dispositions.get('engage', 0)} engage, and {dispositions.get('competitor', 0)} competitor dispositions from Clearbox.**",
        f"- **{tiers.get('A', 0)} Tier A, {tiers.get('B', 0)} Tier B, {tiers.get('C', 0)} Tier C, {tiers.get('D', 0)} Tier D, and {tiers.get('UNSCORED', 0)} unscored rows.**",
        f"- **One repeatable delivery contract:** Clearbox supplies the disposition and permalink; the current analysis layer is {workflow}; the Sheet and this brief refresh from the normalized result.",
        "",
        "> ✅ The value is the worked opportunity queue and the decisions it supports. The Sheet contains the rows and exact source URLs; this page explains how to use it.",
        "",
        "## Highest-priority opportunities to review",
        "",
    ]
    if metrics.get("api_truncated"):
        lines += [
            "> 🔴 This is a partial API snapshot. The returned rows did not represent the complete reported inbox, so totals and recommendations must be refreshed from a complete export before final delivery.",
            "",
        ]
    if top:
        for row in top:
            label = row.get("buyer_question") or row.get("content_topic") or row.get("summary") or f"Opportunity {row['op_id']}"
            label = str(label).replace("\n", " ").replace("[", "(").replace("]", ")").strip()[:140]
            lines.append(f"- [{label}]({row['source_url']}): {row['source_disposition']} | {row['tier']} | {row['action_lane']}.")
    else:
        lines.append("- No current opportunities were supplied.")
    lines += ["", "## What each Sheet tab is for", ""]
    for title, subtitle, description in TAB_GUIDANCE:
        lines += [f"::: toggle {title}: {subtitle}", description, ":::", ""]
    lines += [
        "## How the automated workflow works",
        "",
        "1. Pull the current opportunity inbox through the account-scoped Clearbox API.",
        "2. Preserve each Clearbox disposition and exact Reddit permalink as the source record.",
        "3. Optionally add analysis from Freckle, Base Loop, or Clay through the same normalized fields.",
        "4. Rebuild the Google Sheet in place so the client link remains stable.",
        "5. Rebuild this Notion brief in place from the same rows and Sheet URL.",
        "6. Keep publishing and account actions behind human review. The report can refresh automatically; Reddit participation does not auto-send.",
        "",
        "## Plan and offer guidance",
        "",
        f"- **Current selection:** {pack['plan']['path']}.",
        f"- **Who pays:** {pack['plan']['payer']}.",
        f"- **Readiness:** {pack['plan']['readiness']}.",
        "- Keep each unrelated client in its own offer, audience, queue, reporting line, and evidence ledger.",
        "- The public repo contains the skills and build method. Agency access and multi-offer enablement currently require contacting **partners@clearbox.to**.",
        "",
        "## How success is measured",
        "",
        "1. **Artifact health:** save the exact Reddit URL, live state, identity, disclosure, date, and screenshot.",
        "2. **Search discovery:** record the query, date, position, and exact Reddit URL.",
        "3. **Observed AI answer:** save the engine, prompt, date, full answer, and whether the client appeared.",
        "4. **Exact citation:** record whether the answer cites the exact Reddit artifact URL.",
        "5. **Business outcome:** connect replies, referrals, meetings, opportunities, pipeline, and revenue to the original artifact.",
        "",
        "Retrieval visibility is a useful leading indicator. It is not the same as an observed AI answer or an exact citation.",
        "",
        "## Recommended working session",
        "",
        "1. Choose the offer path in **Plan Setup**.",
        "2. Review the Tier A rows and assign owners.",
        "3. Work the strongest opportunities and update **Review Status**.",
        "4. Capture search, AI-answer, citation, and business-outcome receipts separately.",
    ]
    if sheet_url:
        lines += ["", f"::: bookmark {sheet_url}"]
    return "\n".join(lines).rstrip() + "\n"
