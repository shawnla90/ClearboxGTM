# FACTCHECK — competitor-intel

Rules for competitive claims produced by this skill. Corrections become new rules.

1. **Share of voice is classification-based.** The number reflects how Clearbox classified opportunities (engage/lead/competitor), not how many times a brand name appears in text. Always state the basis.
2. **Sentiment is generated, not observed.** Reddit opportunities carry no sentiment field. The sentiment output is an LLM or keyword heuristic read over op summaries. Label every sentiment figure with "generated."
3. **Reddit is not a census.** A competitor appearing in N% of classified ops means N% of the Reddit conversations Clearbox surfaced in the configured subreddits, not N% of the market. Never extrapolate to market share.
4. **Competitor conversations have permalinks.** Every competitor-is-the-answer op in the output traces to a Reddit permalink. A claim without a permalink is unverifiable and gets cut.
5. **No sentiment without sample size.** A sentiment distribution over fewer than 10 ops is too small to summarize as a trend. State the count, not the percentage.
