# Runtime Scaling Strategy

## Purpose

This document defines practical scaling strategy for the repository.
It replaces the old `scaling_notes.md` stub as the real runtime scaling reference.

## Scaling Goal

Scaling is not only higher throughput.
The correct goal is:

- more unattended cycles
- stable quality under load
- bounded cost
- preserved replayability and fail-closed behavior

## Core Rules

### 1. Quality Before Throughput

Do not add concurrency or batch expansion if it weakens:

- final-threshold closure
- append-only truth
- replayability
- fail-closed handling

### 2. Batch Where Semantics Permit

Prefer batching for:

- analysis passes
- report generation
- low-risk policy evaluation
- portfolio aggregation

Do not blindly batch:

- state mutations with ordering sensitivity
- queue/supervisor authority transitions
- repair paths that must preserve deterministic lineage

### 3. Risk-Tier Scaling

Scaling should follow runtime risk tiers.

- stable tracks can use lighter scrutiny and wider throughput
- caution tracks should keep reduced generation caps
- critical tracks should prioritize repair and may scale generation to zero

### 4. Cost-Bounded Expansion

When scaling:

- prefer deterministic preflight checks before expensive model calls
- prefer shorter smoke paths for validation
- keep request timeouts explicit
- avoid raising generation count if repair backlog is growing

### 5. Portfolio-Aware Scaling

Scale the portfolio, not only a single track.

- avoid cannibalization
- avoid over-allocation to one strong track
- widen release only when coordination, fatigue, and trust signals support it

## Current Repository Levers

- runtime control: `/home/meta_os/web_novel/engine/runtime_config.py`
- queue budget control: `/home/meta_os/web_novel/engine/track_loop.py`
- track prioritization: `/home/meta_os/web_novel/engine/track_queue.py`
- portfolio control: `/home/meta_os/web_novel/engine/portfolio_orchestrator.py`
- request timeout control: `/home/meta_os/web_novel/engine/openai_client.py`

## Immediate Scaling Policy

- prefer batch mode where generation quality is unchanged
- use explicit request timeout controls instead of hanging calls
- expand generation only after repair backlog and failed bundles are low
- keep queue/supervisor state transitions deterministic under any throughput increase

## Anti-Patterns

- scaling generation while critical bundle failures remain open
- adding async or concurrency before contract ownership is clear
- raising throughput by skipping evaluation or lineage evidence
- treating cost reduction as success when reader-quality drops
