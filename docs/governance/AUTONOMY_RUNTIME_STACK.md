# AUTONOMY_RUNTIME_STACK

## Purpose

This document fixes the canonical runtime stack for unattended high-quality automation in this repository.

It exists to prevent architecture drift toward ad-hoc daemon loops or chat-dependent background operation.

## Canonical Build Order

The runtime stack should be built in this order:

1. `event log`
2. `typed snapshots`
3. `job queue`
4. `supervisor`

Do not jump directly to background daemons or supervisor-first control loops without the lower layers.

## Why This Order Wins

### 1. Event Log

The event log is the replayable truth source.

Without it:
- failures cannot be reconstructed cleanly
- promotion or rejection decisions cannot be audited
- long unattended runs become opaque

Repository interpretation:
- append-only operational events
- ingest / reject / defer / promote / generate / rewrite / certify / pause / recover should all be representable as typed events

### 2. Typed Snapshots

Typed snapshots are the stable checkpoint layer.

Without them:
- state recovery becomes implicit and brittle
- supervisors manage unknown state instead of validated state
- queue restarts rely on best-effort dict reconstruction

Repository interpretation:
- snapshot files should validate against explicit schemas
- generation state, queue state, and promotion state should be readable without replaying the whole repo by hand

### 3. Job Queue

The job queue is the unit-of-work layer.

Without it:
- outer-loop ingestion and inner-loop generation compete in one procedural loop
- retries, backoff, and pause semantics become tangled
- 24-hour automation cannot separate routine work from exceptional work

Repository interpretation:
- jobs should be typed
- examples: `ingest_material`, `scope_evaluate`, `promote_material`, `generate_episode`, `rewrite_episode`, `certify_artifact`, `recover_failed_track`

### 4. Supervisor

The supervisor is the policy executor, not the first primitive.

Without the lower three layers it becomes a fragile wrapper around uncontrolled scripts.

Repository interpretation:
- supervisor should observe event logs, read typed snapshots, dispatch queue work, and enforce stop / pause / recovery policy
- supervisor should not be the only source of runtime truth

## Recommended Upper Layers

The four-layer stack above is the core.

The preferred extensions above it are:

### `policy engine`

Decides whether a job should run, pause, retry, be sandboxed, or be promoted.

### `admission gate`

Handles newly arrived material and decides:
- out of scope
- hold
- sandbox
- active promotion

### `artifact registry`

Tracks lineage, quality status, promotion status, and current authority of generated outputs.

### `recovery worker`

Runs explicit recovery jobs rather than mixing recovery logic into every generator path.

## Contracts Governance Requirement

The runtime stack should be implemented under canonical contract governance.

- one session owns final contract interpretation
- other sessions perform review, adversarial audit, and edge-case hunting
- post-lock contract changes follow `proposal -> review -> version bump`
- version compatibility impact should be stated before rollout

Reference:
- `docs/governance/CONTRACTS_GOVERNANCE.md`

## Repository Standard

For this repository, the target runtime is not:
- a single inner generation loop
- a background process that only continues already-included work
- a supervisor with implicit memory

The target runtime is:

`event log + typed snapshots + job queue + supervisor`

plus outer-loop policy for:
- new material intake
- scope selection
- automatic promotion
- rejection and recovery routing

## Success Criterion

The stack is only considered sufficient when:
- it can run for long periods without continuous operator steering
- newly arriving material can be judged and routed without routine manual triage
- later human review adds little marginal quality
- failures are recoverable from files, not from chat context
