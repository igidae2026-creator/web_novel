# Agent Webnovel Fit

## Diagnosis

Market/platform knobs existed, but webnovel-specific serialization fitness was under-modeled.

## Ceiling Bottleneck

Reward density, expectation alignment, chemistry, and sustainability can drift apart.

## Missing Architecture

- pending vs delivered promise tracking
- chemistry signal as explicit axis
- sustainability budget
- power integrity tracking

## Proposed Subsystem

`engine/reward_serialization.py` plus serialization state in `story_state_v2`.

## Integration Points

- retention
- multi-objective evaluation
- market/operational layers later

## Regression Risks

- rewarding too aggressively and exhausting future ceiling
- overpreserving sustainability and becoming flat

## Test Plan

- false victory increases pending debt
- reward density stays above floor without collapsing sustainability
