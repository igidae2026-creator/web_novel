# WEBNOVEL_SYSTEM_BUNDLES

## Purpose

This document groups the full web-novel system into large operational bundles.
It exists to stop local optimization on one layer while ignoring adjacent layers that decide whether the whole product actually works.

The system should not be understood only as:

- generation
- evaluation
- docs

It should be understood as a full commercial web-novel machine.

## Canonical Large Bundles

### 1. Reader Quality Bundle

Purpose:

- produce output that heavy web-novel readers experience as upper-tier

Core concerns:

- early hook
- episode-end addiction
- protagonist fantasy persistence
- long-arc payoff trust
- serialization fatigue control
- prose readability
- anti-thinness, anti-repetition, anti-deja-vu pressure
- payoff trust and anti-fake-cliffhanger pressure

Primary docs:

- `/home/meta_os/web_novel/docs/governance/WEBNOVEL_READER_PERCEPTION_CONTRACT.md`
- `/home/meta_os/web_novel/docs/governance/WEBNOVEL_QUALITY_MAP.md`
- `/home/meta_os/web_novel/docs/absolute_ceiling_master_plan.md`
- `/home/meta_os/web_novel/docs/absolute_ceiling_audit.md`

Primary code zones:

- `/home/meta_os/web_novel/engine/pipeline.py`
- `/home/meta_os/web_novel/engine/quality_gate.py`
- `/home/meta_os/web_novel/engine/cliffhanger_engine.py`
- `/home/meta_os/web_novel/engine/predictive_retention.py`
- `/home/meta_os/web_novel/engine/promise_graph.py`

### 2. Story Machine Bundle

Purpose:

- maintain the internal story-state machine that lets quality repeat instead of appearing by luck

Core concerns:

- character pressure
- conflict escalation
- event typing
- world logic
- causality
- attribution

Primary docs:

- `/home/meta_os/web_novel/docs/absolute_ceiling_master_plan.md`
- `/home/meta_os/web_novel/docs/agents/README.md`

Primary code zones:

- `/home/meta_os/web_novel/engine/character_arc.py`
- `/home/meta_os/web_novel/engine/conflict_memory.py`
- `/home/meta_os/web_novel/engine/event_generator.py`
- `/home/meta_os/web_novel/engine/world_logic.py`
- `/home/meta_os/web_novel/engine/scene_causality.py`
- `/home/meta_os/web_novel/engine/episode_attribution.py`

### 3. Autonomy And Runtime Bundle

Purpose:

- run unattended for long periods without quality collapse or manual rescue

Core concerns:

- append-only truth
- replayability
- queue and supervisor closure
- fail-closed evaluation
- repair-first routing
- soak and fault recovery
- convergence toward `final_threshold_ready=true` as a default unattended state

Primary docs:

- `/home/meta_os/web_novel/docs/governance/AUTONOMY_TARGET.md`
- `/home/meta_os/web_novel/docs/governance/METAOS_RUNTIME_CONTRACTS.md`
- `/home/meta_os/web_novel/docs/governance/METAOS_CONSTITUTION.md`
- `/home/meta_os/web_novel/docs/governance/WEBNOVEL_ALIGNMENT_STATUS.md`

Primary code zones:

- `/home/meta_os/web_novel/engine/final_threshold.py`
- `/home/meta_os/web_novel/engine/final_threshold_runtime.py`
- `/home/meta_os/web_novel/engine/job_queue.py`
- `/home/meta_os/web_novel/engine/runtime_supervisor.py`
- `/home/meta_os/web_novel/engine/track_loop.py`
- `/home/meta_os/web_novel/engine/metaos_recovery.py`

### 4. Portfolio And Market Bundle

Purpose:

- decide what to run, what to hold, what to stagger, and what the market can support

Core concerns:

- portfolio slot allocation
- cannibalization control
- release timing
- market serialization
- cross-track learning
- policy response to rank or reaction shifts

Primary docs:

- `/home/meta_os/web_novel/docs/governance/WEBNOVEL_ALIGNMENT_STATUS.md`
- `/home/meta_os/web_novel/docs/absolute_ceiling_master_plan.md`

Primary code zones:

- `/home/meta_os/web_novel/engine/portfolio_orchestrator.py`
- `/home/meta_os/web_novel/engine/cross_track_release.py`
- `/home/meta_os/web_novel/engine/portfolio_memory.py`
- `/home/meta_os/web_novel/engine/portfolio_signals.py`
- `/home/meta_os/web_novel/engine/market_serialization.py`
- `/home/meta_os/web_novel/portfolio_layer/`
- `/home/meta_os/web_novel/market_layer/`

### 5. Policy And Operations Bundle

Purpose:

- keep the system safe, governable, restorable, and auditable

Core concerns:

- operator rules
- policy boundaries
- content handling
- backup discipline
- recovery discipline
- runtime runbook clarity

Primary docs:

- `/home/meta_os/web_novel/docs/policy_ops_guardrails.md`
- `/home/meta_os/web_novel/OPS_RUNBOOK.md`
- `/home/meta_os/web_novel/docs/ENV_SETUP.md`
- `/home/meta_os/web_novel/docs/governance/CONTRACTS_GOVERNANCE.md`

Primary code zones:

- `/home/meta_os/web_novel/engine/backup_manager.py`
- `/home/meta_os/web_novel/engine/backup_retention.py`
- `/home/meta_os/web_novel/engine/safe_io.py`
- `/home/meta_os/web_novel/engine/delete_guard.py`

### 6. Business And Feedback Bundle

Purpose:

- close the loop from product performance to future work generation and promotion policy

Core concerns:

- revenue and campaign dashboards
- KPI interpretation
- material admission and promotion
- business-side feedback ingestion
- human-lift minimization against actual product outcomes

Primary docs:

- `/home/meta_os/web_novel/SYSTEM_OBJECTIVE.md`
- `/home/meta_os/web_novel/docs/governance/WEBNOVEL_ALIGNMENT_STATUS.md`

Primary code zones:

- `/home/meta_os/web_novel/metaos_business/`
- `/home/meta_os/web_novel/engine/metaos_policy.py`
- `/home/meta_os/web_novel/engine/metaos_adapter_registry.py`
- `/home/meta_os/web_novel/engine/certification.py`

## Interpretation Rule

A change is not large enough if it improves one bundle while quietly degrading another bundle that the product depends on.

Examples:

- better hook generation that breaks replayability is not an acceptable gain
- better autonomy that degrades reader addiction is not an acceptable gain
- better market allocation that increases serialization fatigue is not an acceptable gain
- better throughput that increases thinness, repetition fatigue, or fake urgency is not an acceptable gain

## Current Use

Use these bundles when:

- planning roadmap work
- auditing repo coverage
- deciding document ownership
- deciding whether a refactor is product-positive

They are intentionally broader than the final-threshold capability bundles.
The final threshold is a cycle-time evaluator.
These system bundles are whole-repository planning and governance bundles.
