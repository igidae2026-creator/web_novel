# Agent Regression Guard

## Diagnosis

The old system could report a higher score while silently harming other axes.

## Ceiling Bottleneck

Absolute ceiling optimization is impossible without rejecting bad tradeoffs.

## Missing Architecture

- protected axis list
- balanced profile computation
- before/after decision contract

## Proposed Subsystem

`engine/regression_guard.py`

## Integration Points

- pipeline post-generation update
- analytics evaluator
- deterministic fixtures

## Regression Risks

- guard too strict and blocks progress
- guard too lenient and allows one-axis gaming

## Test Plan

- single-axis overoptimization must be rejected
- balanced uplift with no harmed axis must pass
