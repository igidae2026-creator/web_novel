# METAOS_CONFORMANCE

## Purpose

This document fixes the minimum conformance path for MetaOS runtime reuse.

The goal is to ensure parallel sessions do not only pass unit tests in isolation, but also satisfy one integrated runtime path.

## Minimum Integrated Path

The following path must remain valid:

1. project source is normalized by the adapter
2. scope policy returns a contract-valid verdict
3. admission snapshot records the verdict
4. typed job queue records the next unit of work
5. supervisor snapshot reflects queue runtime state
6. generated artifact is normalized by the adapter
7. promotion policy returns a contract-valid verdict
8. promotion snapshot records the verdict

## Conformance Focus

The integrated path should confirm:

- contracts are the authority layer
- project adapters do not redefine contracts
- policy layer routes normal / borderline / exception correctly
- queue and supervisor snapshots remain typed
- version compatibility assumptions stay explicit

## Conformance Matrix

Every registered adapter should appear in the conformance matrix with:

- `project_type`
- `adapter_name`
- resolution status: `ready` / `missing` / `incompatible`
- default verdict
- locked contract version
- required check list

The matrix should be generated from runtime authority, not maintained as a hand-written guess.

## Failure Interpretation

If the integrated path breaks, it should be treated as:

- a conformance failure
- or a contract compatibility failure

It should not be treated as a local implementation preference issue.
