# CONTRACTS_GOVERNANCE

## Purpose

This document fixes how canonical runtime contracts are authored, reviewed, locked, and versioned.

The goal is to prevent distributed sessions from drifting into incompatible interpretations of the same interface.

## Authority Model

- Canonical contract owner: exactly one authority session owns final interpretation and lock rights.
- Other sessions are not co-owners of the contract text.
- Other sessions act as:
  - review
  - adversarial audit
  - edge-case hunter
  - compatibility risk detector

Contracts are not democratic documents.
They are central interfaces reviewed by multiple sessions and locked by one canonical owner.

## Lock Rule

- Contracts should be locked before broad parallel implementation starts.
- The required sequence is:
  1. draft
  2. review
  3. adversarial audit
  4. lock
- After lock, implementation sessions should conform to the contract instead of reinterpreting it.

## Change Control

After lock, changes must follow:

`proposal -> review -> version bump`

No silent contract edits should be treated as valid runtime evolution.

## Required Contract Surface

The canonical owner should explicitly lock at least:

- event taxonomy
- snapshot types and minimum fields
- job types and job states
- supervisor state transitions
- policy verdict types
- adapter interface surface
- conformance checks
- version compatibility policy

## Version Compatibility

Version compatibility must be explicit.

For every contract change from `vN` to `vN+1`, the owner must state:

- which workers remain compatible
- which adapters remain compatible
- which snapshots can still be read
- whether replay is forward-compatible, backward-compatible, both, or neither
- whether migration is required before rollout

If a version change can break a worker, adapter, or replay path, that breakage should be visible before merge.

## Review Checklist

Review sessions should focus on:

- taxonomy overlap or ambiguity
- missing edge-case states
- invalid or contradictory state transitions
- overpowered supervisor authority
- weak separation between normal / hold / reject / escalate verdicts
- adapter leakage of project-specific assumptions into the core contract
- untracked version-compatibility risk

## Success Standard

The governance is working only when:

- one session can answer what the canonical contract means
- other sessions can try to break it without silently rewriting it
- version upgrades expose compatibility impact early
- integration failures are treated as conformance failures, not interpretation disputes
