# Absolute Ceiling Master Plan

## Canonical Architecture

The canonical runtime architecture is now:

1. Unified story state initialization
2. Character / relationship pressure refresh
3. Conflict escalation refresh
4. Typed event selection
5. Information / emotion state refresh
6. Cliffhanger planning
7. Retention state refresh
8. LLM plan + draft + rewrite
9. Structural evaluation + multi-objective scoring
10. World mutation, reward/serialization mutation, tension update
11. Regression guard check and metrics persistence

## Canonical State Schema

Primary runtime container: `state["story_state_v2"]`

Top-level domains:

- `cast`
- `relationships`
- `world`
- `conflict`
- `unresolved_threads`
- `pacing`
- `rewards`
- `serialization`
- `information`
- `history`
- `control`

Compatibility projections remain available:

- `character_arcs`
- `conflict_engine`
- `tension_wave`
- `retention_engine`
- `story_events`

## Keep / Wrap / Refactor / Replace

### Keep

- Streamlit app shell
- pipeline orchestration shell
- metrics logging
- market/portfolio operational modules

### Wrap

- legacy state access via alias projection from `story_state_v2`
- old tests through backward-compatible payloads

### Refactor

- character arc engine
- conflict engine
- event generator
- cliffhanger generator
- tension wave
- retention engine
- ceiling evaluator
- multi-objective score aggregation

### Replace

- single scalar multi-objective balance heuristic
- content-only ceiling weighting as canonical decision metric

## Implementation Order

1. Unified state architecture
2. Character / relationship / desire engine
3. Conflict escalation engine
4. Typed event generator
5. Information design + emotional payoff engine
6. Tension wave + cliffhanger generator
7. World change / world logic engine
8. Reward density + expectation management + power integrity
9. Retention / serialization / long-run sustainability
10. Adaptation / exploration / regression guard
11. Market fitness and operational control integration

This order was mostly preserved. The main adaptation was implementing world/reward/serialization in the same pass as evaluation because the repo already had a stable pipeline shell and the critical blocker was shared state.

## Regression Gates

Protected axes:

- fun
- coherence
- character persuasiveness
- pacing
- retention
- emotional payoff
- long-run sustainability
- world logic
- chemistry
- stability

Acceptance rule:

- reject a change when balanced total improves only by sacrificing one or more protected axes beyond tolerance

## Balancing Principle

The system does not locally maximize cliff intensity, reward density, or novelty. It maximizes balanced profile quality:

- short-run heat must not bankrupt long-run trust
- chemistry must remain consequence-driven
- world change must be visible but rule-bounded
- retention pressure must come from meaningful unresolved cost, not empty withholding

## Remaining Structural Work

- scene-level causality validation against actual LLM outputs
- explicit antagonist planner separate from protagonist pressure model
- memory-guided adaptation loop beyond fixed-state heuristics
- portfolio-level cross-track learning

## Recent Architecture Extensions

- causal repair now runs as a bounded closed loop with retry budget, re-validation, closure scoring, and final accept/fail state
- portfolio memory now ingests real track metrics logs and learns crowded/winning/fatigue patterns from observed outcomes
- cross-track portfolio metrics are translated into coordination state and policy directives rather than only direct score penalties
- post-repair diff audit now performs semantic scene-structure comparison, intent-preservation scoring, failure-type classification, and strategy effectiveness learning across retries
- release scheduling is now enforced at runtime through queue-level accelerate/stagger/hold behavior instead of remaining a planning-only layer
- runtime release outcomes now feed story-state learning for retention, pacing, trust, fatigue, and coordination so later release policy is shaped by executed results
- platform-aware slot policy now uses adaptive outcome-weighted allocation with strong-window anti-monopoly guards instead of fixed retention ordering alone
- promise/payoff state is now tracked as a cross-episode graph with unresolved debt, payoff integrity, and corruption detection feeding evaluation
- episode-level attribution now records retention, pacing, fatigue, and payoff signals per episode for downstream repair and release decisions
- release planning now reserves multiple future windows so strong tracks can claim high-value slots without monopolizing long-horizon opportunity
- promise state now carries character-specific ownership and dependency edges, causal attribution now identifies high-impact scene units, and long-horizon allocation now accounts for platform seasonality across six windows

## Commercial Serialization Audit

The current repository already had usable support modules for the studio-OS shift, but they were still biased toward general story quality instead of platform-native commercial serialization.

Existing modules that support the new architecture:

- `engine.reward_serialization`, `engine.promise_graph`, `engine.market_serialization`: already tracked reward density, payoff integrity, paywall pressure, and reader-trust style serialization signals.
- `engine.tension_wave`, `engine.fatigue`, `engine.predictive_retention`: already modeled pacing, release debt, and short-run retention pressure.
- `engine.cross_track_release`, `engine.portfolio_memory`, `engine.control_console`, `ui/panels/*`: already provided release scheduling, portfolio logic, runtime visibility, and control-plane presets.
- `engine.reliability`, `engine.regression_guard`, `engine.multi_objective`: already provided long-run simulation, drift detection, protected-axis scoring, and rollback visibility.

Modules extended in this pass:

- `engine.pipeline`: now loads platform/genre production constraints, title candidates, milestone state, monetization state, protagonist guard state, narrative debt, emotion wave, and IP readiness before evaluation and persistence.
- `engine.story_state`: now carries business-aware serialization state as first-class runtime data instead of leaving it implicit in prompts or operator intuition.
- `engine.multi_objective`, `engine.regression_guard`, `engine.reliability`: now expose and protect title fitness, milestone compliance, conversion readiness, protagonist sovereignty, narrative debt health, emotion-wave health, and IP readiness.
- `engine.runtime_config`, `engine.control_console`, `ui/panels/project_setup`, `ui/panels/shared`: now carry project title and project-level platform/genre override hooks through the runtime control plane.
- `engine.causal_repair`: now translates weak business axes into bounded revision directives and traceable revision triggers instead of treating them as read-only diagnostics.
- `ui/console_app`, `ui/panels/studio_os_dashboard`, `engine.control_console`: now expose a dedicated operator-facing Studio OS view with current values, trends, title package, and business-axis warnings.

New modules added:

- `engine/platform_genre_spec.py`
- `engine/episode_milestones.py`
- `engine/monetization_transition.py`
- `engine/protagonist_guard.py`
- `engine/title_optimizer.py`
- `engine/narrative_debt.py`
- `engine/emotion_wave.py`
- `engine/ip_expansion_readiness.py`

What still previously assumed “general story quality” more than “platform-native webnovel success”:

- title handling was effectively absent as a scored product entry point
- early-episode hook/reward, episode-10 payoff, and episode-20~25 conversion structure were not enforced as explicit milestones
- protagonist centrality risk was not guarded as a protected commercial axis
- long-run cost of short-term escalation was only partially visible through fatigue and promise debt, not tracked as narrative debt
- IP expansion readiness had no evaluation hooks despite existing long-run simulation and export surfaces

## Business-Aware Repair Extension

The repair loop is no longer purely causal/viral. After scoring, the pipeline now performs a bounded business-axis revision pass when blocking weaknesses are found in milestone compliance, conversion readiness, protagonist sovereignty, narrative debt health, or emotion-wave health.

- Failures are converted into explicit directives inside `engine.causal_repair`.
- Revision triggers are written into runtime state and `system_status`.
- Title weakness is kept visible and actionable, but non-blocking, because it is better handled through title/package updates than by forcing infinite body rewrites.
- The console now reads those same traces back through a dedicated Studio OS dashboard view instead of burying them in raw JSON.

## Operator Action Loop Extension

The Studio OS loop now closes warnings into bounded operator-style adjustments.

- `engine.business_operator` maps weak business axes into deterministic recommended actions.
- Those recommendations can be applied through the existing `policy_action` path as reversible runtime-config changes.
- Supported bounded adjustments now include title package replacement, milestone-enforcement increase, protagonist-focus increase, IP-enforcement increase, guarded release strategy suggestion, release-cadence reduction, and soft-recovery mode activation.
- Adjustment outcomes are logged with before/after business-axis snapshots and folded into lightweight learning summaries so the console can show whether those actions helped.
# Streamlit Runtime Control

The Streamlit entrypoint now acts as a lightweight control panel for the automated generation loop.

- `runtime_config.json` is the runtime control file shared by Streamlit and the generation pipeline.
- `engine.pipeline` loads `runtime_config.json` at episode generation startup and reflects active evaluation/runtime overrides in episode metadata.
- `outputs/system_status.json` is written as a global runtime snapshot so dashboards can read current iteration state without opening per-track state files.
- The Streamlit app can start or stop generation safely, update runtime knobs, inspect recent `metrics.jsonl` records, and preview the latest generated episode outputs across `tracks/*/outputs`.
- CLI generation still works when Streamlit is not used because missing or default runtime config falls back to deterministic defaults.
