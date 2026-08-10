---
name: personalization
version: 1.0.0
description: The 3-variable personalization model for Reddit comment drafting — icebreaker, poke-the-bear, and pain-point. Makes every drafted reply specific to the thread, the person, and the problem instead of generic value-add. Use when the user types "/personalization" or says "personalize the reply", "make the comment specific", "apply the 3-variable model".
---

# personalization

Three variables that turn a generic reply into one the reader feels was written for them. Each has a different job and a different tone.

## The model

| Variable | Job | Tone | Where it lands |
|----------|-----|------|----------------|
| **Icebreaker** | Prove you read the thread and know their context | Warm, observational, specific | Opening line of the comment |
| **Poke the bear** | Challenge their status quo — create productive tension | Edgy, confident, peer-to-peer | Mid-comment, after the icebreaker |
| **Pain point** | Name the specific problem behind the question | Direct, company- or role-specific | Body of the comment, grounding the advice |

**Key distinction**: These are not the same thing. An icebreaker says "I see you." A poke-the-bear says "I see what you are ignoring." A pain point says "Here is the problem you are dealing with."

Not every comment needs all three. A short, helpful reply might use only an icebreaker and a pain point. A longer reply in a technical thread might lead with a poke-the-bear. Use what the thread warrants.

## Inputs

- A Reddit thread (URL or full text) — the comment must respond to the actual conversation
- The buyer-language classification from the engine (intent, topic, brands mentioned) — tells you what kind of question this is
- Any company or role context visible in the thread (the author's flair, post history, self-disclosed company)

## The variables

### Icebreaker

The opening line that proves you read the thread. A specific detail from the post, a shared experience, or a real observation about their situation.

**Rules:**
1. One sentence. It opens the reply.
2. Reference something real from the thread: a specific tool they mentioned, a number they shared, a constraint they described.
3. If the author disclosed their role or company, use it. If not, infer from context and be honest about it.
4. Never generic flattery. "Great question" is a delete trigger.
5. Never fabricate. If you cannot find a specific detail, skip the icebreaker and open with the pain point.

**Good vs bad:**

| Good | Bad |
|------|-----|
| References a real detail from the post | Generic observation anyone could make |
| Feels like someone who read the whole thread | Could apply to any post in the sub |
| Conversational, natural | Sycophantic or performatively curious |

**Examples (Reddit context):**

Thread: "We just migrated from Zendesk to Jira Service Management and it's been rough"
> "The Zendesk-to-JSM path is one of the ones where month six is worse than month one — the workflows that 'mostly work' start breaking under edge cases nobody mapped."

Thread: "Scaling a DTC brand to 50K orders/month, current 3PL is falling apart"
> "50K/month is exactly the range where a 3PL that worked at 10K starts missing SLAs on the quiet — you feel it in WISMO tickets before you see it in dashboards."

### Poke the bear

A provocative observation that challenges how the reader is handling something. Creates tension without pitching a solution. The reader should think: "...that is actually true."

**Rules:**
1. One to two sentences. Slightly edgy. Should make the reader pause.
2. Specific to their vertical, role, or stated situation — not a generic industry complaint.
3. Confident peer tone, not vendor pitch. Write like someone who has watched this pattern play out fifty times.
4. Do NOT mention your product, brand, or solution. Just name the problem sharply.
5. Do NOT offer a fix. The poke is the point — sit in the discomfort.

**Examples (Reddit context):**

Thread about running omni-channel fulfillment:
> "Running fulfillment from three separate inventory pools and calling it 'operational flexibility' is a polite way of saying nobody has the budget to fix it."

Thread about tool sprawl across engineering teams:
> "Three project management tools across four teams is not a 'best of breed' strategy — it is a sign that nobody had time to consolidate after the last reorg."

### Pain point

A data point or observation that names the specific problem behind the question. Not a generic industry challenge — something that makes the reader think "how did they know that?"

**Rules:**
1. One sentence. Standalone.
2. Tie to a real signal in the thread: a tool they named, a scale they described, a constraint they mentioned.
3. Frame as observation or question — not a pitch.
4. The signal has to be real. If you cannot ground it in something from the thread, do not use it.

**Examples (Reddit context):**

Thread about Atlassian Data Center end-of-support:
> "Running Atlassian Data Center with end-of-support approaching usually means someone is quietly scoping a migration nobody wants to own."

Thread about a lean IT team doing a national rollout:
> "Rolling out new POS systems across 300 locations by Q3 with a 4-person IT team usually means someone is about to learn what scope creep really feels like."

## How to apply

When drafting a Reddit comment (via `reddit-engage` or manually):

1. **Read the full thread first.** Identify the real question, the author's context, and any disclosed details.
2. **Pick the variables the thread warrants.** Short helpful reply: icebreaker + pain point. Longer analytical reply: all three. Quick agreement or tip: just a pain point observation.
3. **Draft the comment using the variable(s) as the skeleton.** The icebreaker opens, the poke-the-bear creates tension, the pain point grounds the advice, and the rest of the comment delivers genuine value.
4. **Run the voice check.** No product mentions, no links, no generic platitudes. The comment must work as a standalone reply from someone who has been in this situation.

## Output

A drafted Reddit comment where the personalization variables are visible in the structure:
- Opening line demonstrates thread-specific awareness (icebreaker)
- A tension-creating observation if the thread warrants depth (poke-the-bear)
- A grounded, specific problem statement (pain point)
- Genuine value-add advice that follows from the pain point

The variables are structural — they do not appear as labeled sections in the final comment. The reader should not know a model was applied.

## Rules

1. **Thread-specific always.** Every variable must trace to something real in the thread. Generic variables are worse than none.
2. **Never fabricate details.** If you cannot find a real signal, skip that variable.
3. **No product mentions in any variable.** The icebreaker, poke, and pain point are problem-only.
4. **Calibrate to the thread.** A two-sentence helpful comment does not need all three variables. Over-personalizing a simple answer feels performative.
5. **The poke-the-bear is optional.** Use it when the thread is about a strategic decision, a comparison, or a "we have always done it this way" situation. Skip it for straightforward how-to questions.

## Building a pain-point library

For repeated engagement in a vertical, build a pain-point library: a table mapping known operational pressures to the signals that reveal them.

| Pain point | Vertical | Signal to look for |
|------------|----------|-------------------|
| Manual processes that break at scale | Operations, fulfillment | Hiring ops roles, negative vendor reviews |
| Tool sprawl creating integration drag | IT, engineering | Multiple overlapping platforms in stack |
| Forced migration with no clear owner | IT leadership | End-of-support announcements, admin job postings |
| Lean team stretched across too many sites | Multi-location ops | National footprint + small team signals |

This table feeds the poke-the-bear and pain-point variables. When a thread matches a row, the variable writes itself.

## Related

- [`../reddit-engage/SKILL.md`](../reddit-engage/SKILL.md) — the approval loop that uses these variables in drafted comments
- [`../../playbooks/how-to-win-on-reddit.md`](../../playbooks/how-to-win-on-reddit.md) — why the no-links, value-first rules exist
- [`../competitor-intel/SKILL.md`](../competitor-intel/SKILL.md) — competitor context feeds the poke-the-bear variable
- [`../../engine/mine.py`](../../engine/mine.py) — buyer-language extraction that identifies the question type
