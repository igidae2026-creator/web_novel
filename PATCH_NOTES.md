# METAOS_REVENUE_OPTIMIZER Content Ceiling Patch

## Where it goes (recommended)
- `analytics/content_ceiling/`  ← content-only analyzers (no private/external data)
- `reports/content_ceiling_report.py` ← optional aggregated reporting
- `tests/test_content_ceiling.py` ← sanity tests

## One required integration point
Call `analytics.content_ceiling.ceiling.evaluate_episode(text, meta)` **after** an episode text is finalized
(typically right after LLM output validation, before metrics logging).

You should then:
- store returned dict into episode meta: `meta["content_ceiling"] = result`
- log key fields into metrics.jsonl (e.g. `ceiling_total`, `curve_slope`, `reward_interval_mean`, etc.)

## Why under analytics?
Because this layer is:
- deterministic
- content-only
- orthogonal to revenue/LLM/runtime
and should not create circular imports with `llm/` or `core/`.
