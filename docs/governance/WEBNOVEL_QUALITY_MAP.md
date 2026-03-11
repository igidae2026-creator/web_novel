# Web Novel Quality Map

This document maps product-quality targets to concrete repository modules and current tests.
It is a repository implementation map, not the primary semantic contract.

Reader-facing semantic contract:

- `/home/meta_os/web_novel/docs/governance/WEBNOVEL_READER_PERCEPTION_CONTRACT.md`

## Reader-Perceived Hook

- modules: `engine/pipeline.py`, `engine/event_generator.py`, `engine/quality_gate.py`
- supporting tests: `tests/test_content_ceiling.py`, `tests/test_absolute_ceiling_regression.py`

## Cliffhanger and Episode-End Addiction

- modules: `engine/cliffhanger_engine.py`, `engine/tension_wave.py`, `engine/predictive_retention.py`
- supporting tests: `tests/test_fun_cliffhanger_engine.py`, `tests/test_fun_tension_wave.py`, `tests/test_fun_retention_engine.py`

## Character Persuasiveness

- modules: `engine/character_arc.py`, `engine/antagonist_planner.py`, `engine/information_emotion.py`
- supporting tests: `tests/test_fun_character_engine.py`, `tests/test_absolute_ceiling_regression.py`

## Conflict Heat and Escalation

- modules: `engine/conflict_memory.py`, `engine/event_generator.py`, `engine/promise_graph.py`
- supporting tests: `tests/test_fun_conflict_engine.py`, `tests/test_quality_gate.py`, `tests/test_absolute_ceiling_regression.py`

## Long-Run Coherence and World Logic

- modules: `engine/world_logic.py`, `engine/scene_causality.py`, `engine/story_state.py`, `engine/causal_repair.py`
- supporting tests: `tests/test_absolute_ceiling_regression.py`

## Reader Retention and Serialization Pressure

- modules: `engine/predictive_retention.py`, `engine/reward_serialization.py`, `engine/market_serialization.py`, `engine/pattern_memory.py`
- supporting tests: `tests/test_fun_retention_engine.py`, `tests/test_content_ceiling.py`, `tests/test_absolute_ceiling_regression.py`, `tests/test_quality_gate.py`

## Readable Prose and Low Friction

- modules: `engine/quality_gate.py`, `engine/prose_guard.py`, `engine/prompts.py`
- supporting tests: `tests/test_quality_gate.py`

## Regression Safety and Reliability

- modules: `engine/regression_guard.py`, `engine/reliability.py`, `engine/integrated_validator.py`
- supporting tests: `tests/test_absolute_ceiling_regression.py`

## Current Gaps

- `engine/quality_gate.py` still does not encode every desired product quality, but it now gates prose readability in addition to protagonist momentum, direct cliffhanger validity, carryover pressure, live conflict-thread continuity, serialization novelty drift, payoff integrity, world instability, score, retention, ceiling, and causality checks
- repair guidance now covers the current gate failure codes in `engine/prompts.py`, but repair quality still depends on the model actually executing those directives well at generation time
- imported generic governance text still remains below the repo-specific Layer 3 override as reference-only material
