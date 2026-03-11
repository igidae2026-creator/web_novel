# AUTONOMY_TARGET

## Purpose

This document isolates the autonomy and quality bar for the repository.
It defines the unattended execution standard separately from broader product or governance goals.

## Target Standard

- The target is a 24-hour autonomous loop that keeps producing high-quality outputs with minimal human micromanagement.
- Human involvement is allowed, but it must not be required for routine continuation.
- The desired steady state is that human intervention adds little or no meaningful quality gain over the system's default output.
- Human involvement should progressively shift from active production to approval, audit, and rare correction.
- Automation limited only to already-included scope is not enough; the outer loop must also evaluate newly arriving material, decide whether it belongs in scope, and promote it automatically when it clears quality and relevance gates.
- The system should continuously raise, reject, defer, or promote work items and source material without waiting for manual triage.
- The default unattended loop should trend toward `final_threshold_ready=true` instead of oscillating around repeated rescue states.
- Reader-facing debt, arc debt, market pressure, and soak history must automatically alter the next cycle without operator interpretation.
- Hidden heavy-reader complaints such as thinness, repetition fatigue, deja-vu rhythm, fake urgency, payoff distrust, tonal flattening, and protagonist-fantasy thinning must be treated as autonomy failures if the loop keeps reproducing them unattended.

## Evaluation Gate

- If the system still depends on frequent operator steering to maintain quality, the target has not yet been met.
- Scope expansion, batching, filtering, validation, and writeback rules should be judged by unattended operation without quality collapse.
- Quality gates should prefer low review noise, stable rerun behavior, and no append-style degradation of canonical outputs.
- If newly ingested material still needs a person to decide routine scope selection, prioritization, or promotion into the active loop, the target has not yet been met.

## Operational Implications

- Persist intent, progress, and resume state in repository files instead of relying on chat memory.
- Prefer resumable loops, manifests, ledgers, checkpoints, and structured artifacts over conversational continuation.
- Treat automation changes as suspect if they increase dependence on manual steering.
- Favor replayable, auditable output paths over one-off operator-guided production.
- Add an outer ingestion and triage layer that can classify new inputs, bind them to the right subsystem, and either reject, sandbox, or promote them without operator involvement.
- Judge autonomy progress against the stricter bar of "human intervention produces negligible additional quality gain," not merely "the existing loop runs unattended."
- A loop that runs unattended while repeatedly emitting thin, repetitive, low-trust chapters has not met the autonomy target; unattended operation without reader-facing convergence is not success.

## Canonical Runtime Stack

The preferred runtime stack for this autonomy target is:

1. `event log`
2. `typed snapshots`
3. `job queue`
4. `supervisor`

This repository should not jump directly from local loop scripts to background supervision without first locking replayable logs, validated snapshots, and typed work units.

Recommended upper layers above that core stack:
- `policy engine`
- `admission gate`
- `artifact registry`
- `recovery worker`

## Contracts Governance

- Canonical runtime contracts should have exactly one lock authority.
- Other sessions should review, attack, and audit the contract instead of co-owning interpretation.
- After lock, changes should follow `proposal -> review -> version bump`.
- Version compatibility must be explicit before contract upgrades are accepted.

Reference:
- `docs/governance/AUTONOMY_RUNTIME_STACK.md`
- `docs/governance/CONTRACTS_GOVERNANCE.md`
