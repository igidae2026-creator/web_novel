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
