# Agent Adaptation Exploration

## Diagnosis

The repo had little structural adaptation beyond score history.

## Ceiling Bottleneck

A high-ceiling system needs memory of what patterns were used and a controlled novelty budget.

## Missing Architecture

- novelty budget
- exploration budget
- pattern memory

## Proposed Subsystem

Use serialization state as the first bounded adaptation layer, then extend later into portfolio memory.

## Integration Points

- event selection
- reward density
- multi-objective stability

## Regression Risks

- random novelty causing collapse
- overfreezing patterns and flattening exploration

## Test Plan

- novelty budget mutates on major world-shifting events
- stability score penalizes repetition and imbalance
