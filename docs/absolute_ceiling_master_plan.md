# Absolute Ceiling Master Plan

This is the canonical quality-architecture plan.
It supersedes the older parallel archived planning surface `docs/archive/archive_fun_engine_master_plan.md`.

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

This canonical stack absorbs the earlier fun-engine transition:

- outline
- character desire state
- conflict escalation state
- tension wave target
- typed event slate
- episode plan
- draft
- structural cliffhanger pass
- rewrite
- retention pressure update
- deterministic ceiling analysis

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

## Core Story-State Model

The state model must remain explicit enough to answer, before drafting:

- what the protagonist wants now
- what they fear losing now
- what weakness can sabotage them now
- what conflict worsens if they fail now
- what event type should fire now
- what cliffhanger mode should close now
- what unresolved pressure should force the next click

Required domain emphasis:

### Character State

- desire
- fear
- weakness
- misbelief
- urgency
- relationship pressure
- progress
- backlash

### Conflict State

- unresolved threads
- threat actor pressure
- consequence ladder
- recent event types
- payoff debt

### Tension State

- target band
- current band
- recent peaks
- release debt
- spike debt

### Retention State

- unresolved thread pressure
- curiosity debt
- threat proximity
- promised payoff pressure
- betrayal or reveal carryover

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

Earlier first-pass fun-engine ordering is now absorbed here:

1. Character desire engine
2. Conflict escalation engine
3. Typed event generator
4. Cliffhanger generator
5. Tension wave controller
6. Retention upgrade

The current master plan treats those six as minimum generation machinery rather than a separate architecture track.

## Generation Rules

These remain binding architecture rules:

### Rule 1

Every episode must be generated from state, not only from static outline plus platform knobs.

### Rule 2

Every major event must create either:

- a new unresolved thread
- a raised consequence
- a partial payoff with new cost

### Rule 3

Cliffhangers must point at a concrete withheld consequence, not generic suspense wording.

### Rule 4

Tension must wave.
Sustained max intensity without release burns headroom and damages long-run fun.

### Rule 5

Retention must optimize unresolved pressure quality rather than only score averages.

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
- richer relationship graph memory
- stronger opponent-side planning and counter-strategy representation

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

## Implemented Baseline

The following first-order structural layers are already implemented and should not be treated as optional side work:

- character desire engine
- conflict escalation engine
- typed event generator
- cliffhanger generator
- tension wave controller
- retention pressure engine

That means the next ceiling gains come from deeper semantics and stronger closure, not from re-arguing whether these layers should exist.
# Streamlit Runtime Control

The Streamlit entrypoint now acts as a lightweight control panel for the automated generation loop.

- `runtime_config.json` is the runtime control file shared by Streamlit and the generation pipeline.
- `engine.pipeline` loads `runtime_config.json` at episode generation startup and reflects active evaluation/runtime overrides in episode metadata.
- `outputs/system_status.json` is written as a global runtime snapshot so dashboards can read current iteration state without opening per-track state files.
- The Streamlit app can start or stop generation safely, update runtime knobs, inspect recent `metrics.jsonl` records, and preview the latest generated episode outputs across `tracks/*/outputs`.
- CLI generation still works when Streamlit is not used because missing or default runtime config falls back to deterministic defaults.
