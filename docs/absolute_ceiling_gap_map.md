# Absolute Ceiling Gap Map

## Already Partially Covered

- Fun: hook/escalation-oriented generation already existed.
- Coherence: weakly covered by outline anchoring and prompt scaffolding.
- Pacing / rhythm: tension wave and cliffhanger modules existed.
- Reader retention: predictive retention module existed.
- Operational controllability: config-heavy pipeline, metrics logging, track tooling.
- Throughput / iteration efficiency: deterministic state file + metrics JSONL + UI controls.

## Weakly Represented

- Character persuasiveness: desire/fear existed, but not enough contradiction, wound, moral limit, relationship debt.
- Emotional immersion: partly proxied by `emotion_density`, not structurally driven.
- World logic: consequences were local; world-state mutation was under-modeled.
- Expectation management: pending promise accounting was missing.
- Reward density: not tracked as a controlled subsystem.
- Power-system integrity: no dedicated pressure on rule consistency.
- Character chemistry: absent as a first-class state/eval axis.
- Long-run sustainability: only loosely implied by fatigue and pacing.
- Adaptation / exploration: almost no structural memory or mutation budget.

## Missing Before This Pass

- Canonical state architecture spanning character, relationship, world, conflict, pacing, reward, serialization, information.
- Real regression guard that rejects one-axis wins harming total profile.
- Information asymmetry subsystem.
- World change engine.
- Reward density / expectation / sustainability balancing subsystem.
- Chemistry-aware retention state.

## Bottlenecks Blocking The Absolute Ceiling

- No single source of truth for story state.
- Too much dependence on recent score heuristics.
- No protected balance across fun/coherence/retention/emotion/sustainability/world logic.
- No explicit modeling of irreversible costs.
- No durable serialization memory for promises paid vs promises deferred.

## Improvements That Risk Harming Other Axes

- More cliffhangers can raise retention while destroying payoff trust if unresolved debt grows too fast.
- More reward density can raise short-run fun while collapsing long-run sustainability.
- Faster escalation can improve click-through while harming coherence and world logic.
- More chemistry can raise interaction value while causing tonal drift or melodrama if not bounded by conflict/state logic.
- More novelty can help exploration while harming stability and expectation management.

## Gap Resolution Strategy

1. Install unified state architecture first.
2. Move all major engines to read/write that state.
3. Add missing subsystems for information, world change, reward/serialization.
4. Replace single scalar balance logic with protected multi-objective scoring.
5. Add deterministic tests for exactly the axes that used to drift silently.
