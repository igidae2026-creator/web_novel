# METAOS_RUNTIME_CONTRACTS

## Purpose

This document fixes the canonical MetaOS runtime contracts for this repository.

These contracts are the interface that parallel sessions must conform to before broader MetaOS reuse is attempted.

## Contract Version

- current contract version: `1.0.0`
- lock authority: one canonical contract owner
- post-lock changes: `proposal -> review -> version bump`

## Event Taxonomy

Canonical event types:

- `ingest_material`
- `scope_evaluate`
- `promote_material`
- `reject_material`
- `defer_material`
- `generate_episode`
- `rewrite_episode`
- `episode_rejected`
- `certify_artifact`
- `pause_queue`
- `resume_queue`
- `recover_failed_track`
- `job_queue_synced`
- `supervisor_snapshot_updated`
- `admission_decision_recorded`
- `promotion_decision_recorded`

Every event record should expose:

- `ts`
- `type`
- `payload`

## Snapshot Types

Canonical typed snapshots:

- `queue_state`
- `job_queue_state`
- `supervisor_state`
- `admission_state`
- `promotion_state`
- `story_state`

Snapshots should remain replayable and readable without chat memory.

## Job Queue Contract

Canonical job types:

- `ingest_material`
- `scope_evaluate`
- `promote_material`
- `generate_episode`
- `rewrite_episode`
- `certify_artifact`
- `recover_failed_track`
- `generate_episode_track`

Canonical job statuses:

- `queued`
- `running`
- `completed`
- `failed`
- `rejected`
- `cancelled`

Canonical queue statuses:

- `idle`
- `running`
- `paused`
- `blocked`
- `done`

## Supervisor Contract

Canonical supervisor modes:

- `observe`
- `control`
- `recovery_only`

Canonical supervisor statuses:

- `idle`
- `running`
- `paused`
- `blocked`
- `recovering`
- `stopped`
- `done`

Supervisor is a policy executor above logs, snapshots, and queue.
It is not the only source of runtime truth.

## Policy Verdict Contract

Canonical policy verdicts:

- `accept`
- `hold`
- `reject`
- `escalate`
- `sandbox`
- `promote`

Interpretation target:

- normal case: automatic `accept` or `promote`
- borderline case: automatic `hold`, `reject`, or `sandbox`
- true exception: `escalate`

## Version Compatibility

Compatibility must be explicit for every version change.

For `vN -> vN+1`, the canonical owner should state:

- worker compatibility
- adapter compatibility
- snapshot readability
- replay direction: forward / backward / both / neither
- whether migration is required

Default rule:

- `1.0.0 -> 1.0.0`: fully compatible
- any unstated version jump: incompatible until proven otherwise

## Conformance

Parallel sessions should not reinterpret these contracts locally.

They should be checked against:

- `engine/metaos_contracts.py`
- `engine/job_queue.py`
- `engine/runtime_supervisor.py`
- conformance tests
