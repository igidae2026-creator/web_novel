# Content Ceiling (Top 5% Tier) — Content-only

This module provides deterministic, content-only scoring and diagnostics:
- emotional curve statistics
- reward interval distribution
- dialogue ratio proxy (available from your existing pressure module)
- tension tempo proxy (via rhythm + curve)
- cliffhanger type frequency
- protagonist status-rise interval
- conflict escalation steps
- genre micro-pattern clustering (offline)

Integration: call `analytics.content_ceiling.evaluate_episode(text, meta)` after episode generation.
