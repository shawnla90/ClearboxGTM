# The Reddit AI Visibility Loop

AI decides who to recommend by reading what people say in public. For "best" and "X vs Y" buying questions, it leans on Reddit, because that is where people are honest about what they bought and what they regret. If your buyers are comparing what you sell and you are not in those threads, the model has nothing of yours to cite.

This is the open loop for fixing that the sincere way. It is the whole pipeline, not an analysis script: connect Google Workspace, research Reddit, build the sheet, build the deck. The working engine lives in the ClearboxGTM repo (`engine/`).

## The loop

1. **Connect Google Workspace over the CLI.** The OAuth step that gets skipped. Once it is connected, an agent can write your Sheets, Docs, and Slides as you.
2. **Pull recent buyer questions, guardrailed to the last 30 days.** Only live conversations enter the pipeline. Set the window to 60 days for a fuller season, never wider without a reason.
3. **Score them into a content plan.** A color-coded Google Sheet: the real questions and comparisons buyers are posting, ranked by intent and demand, with the pages and posts to publish first.
4. **Build the deck.** Slides you can present to a client or a team, generated from the same data.

## Why the guardrails matter

Two gates run on every pull, and they are the difference between growing on Reddit and getting banned.

**Recency.** If you are engaging with a thread from three years ago, you are not part of the conversation, you are digging through a graveyard. Recent-only keeps you honest and keeps you safe. It is the same instinct as reading the room before you talk.

**Relevance.** A broad keyword search drags in off-topic noise. Keep only the threads that are actually about your category. What a client sees has to be real, or the whole thing loses trust.

## The play, not the spam

The reflex when you are invisible in AI is to go post on Reddit. That is how you get banned. Reddit does not want your marketing, and the people there want it even less.

The sincere play is quieter and it works:

- Find the questions buyers already ask, and answer them where the answer actually helps.
- Build a community you own instead of renting attention in someone else's. If no good one exists for your niche and area, that is the opening.
- Comment as yourself, share real value, build karma. Karma is credibility. It is what makes your presence stick and get cited, and it is earned by being useful, not by dropping links.
- Get cited because you were the most helpful voice in the thread.

## The source contract

Clearbox is the source of record. It classifies each opportunity as `lead`, `engage`, or `competitor` and preserves the exact Reddit permalink. "Best CRM for small teams" and "frustrated with HubSpot" can both be buying signals, so the system uses offer context and classification rather than presenting a keyword pull as the product.

Freckle, Base Loop, or Clay can add analysis after the Clearbox pull. They do not replace the source disposition or the permalink. That separation is what keeps a client report traceable.

## From visibility to retrieval

Being in the thread is step one. The next question is: does the AI model actually surface your brand when someone asks? That is retrieval visibility, and it is measurable.

The [`geo-visibility` skill](../skills/geo-visibility/) checks current retrieval visibility with a hard-capped Exa pass. This shows whether the brand surfaces in Exa's result set for a given buyer question. It is a leading indicator, not proof that an answer engine named or cited you. Observed AI visibility requires a separate prompt receipt with the answer and exact citations.

The loop that compounds:

1. Post genuinely in the right threads (the thesis in [how-to-win-on-reddit.md](how-to-win-on-reddit.md))
2. Build karma by being useful, not by dropping links
3. AI models read those threads and learn who the helpful voices are
4. Over time, retrieval visibility increases for the buyer questions you answered
5. Measure with the GEO skill, adjust the content plan, repeat

## Running the loop yourself

```bash
# Clone and run the offline pipeline (no API key needed)
git clone https://github.com/shawnla90/ClearboxGTM.git
cd ClearboxGTM/engine
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
bash run.sh --offline

# Then connect Google and import a complete Clearbox export
python3 setup_oauth.py
CLEARBOX_EXPORT=/path/to/clearbox-opportunities.json bash run.sh
```

The sheet URL prints at the end. Open it. That is your content plan, scored and color-coded. For the deck, run `python3 build_deck.py`.

## Related

- [How to win on Reddit](how-to-win-on-reddit.md) -- the thesis behind everything in this repo
- [`skills/geo-visibility/`](../skills/geo-visibility/) -- measure retrieval visibility with Exa
- [`proof/`](../proof/) -- 1.5M+ tracked views on one account, generated not typed
- [`transparency/what-actually-worked.md`](../transparency/what-actually-worked.md) -- the honest channel ranking
- [`skills/reddit-engage/`](../skills/reddit-engage/) -- draft value-first replies with a human gate
