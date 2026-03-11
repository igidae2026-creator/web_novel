# WEBNOVEL_METAOS_ADAPTER

## Purpose

This document fixes how `web_novel` attaches to the MetaOS runtime core as a project adapter.

The adapter should keep project-specific details out of the shared runtime contracts.

## Adapter Role

`web_novel` should supply:

- source material normalization
- track payload normalization
- episode artifact normalization
- project-specific metadata packing

The adapter should not redefine:

- core event taxonomy
- queue state semantics
- supervisor semantics
- policy verdict semantics

## Canonical Mapping

- intake source -> `material_from_source(...)`
- episode result -> `artifact_from_episode_result(...)`
- track queue entry -> `track_job_payload(...)`

## Boundary Rule

If `web_novel` needs project-specific logic, it should be implemented in the adapter first.

Core MetaOS runtime files should only change when the contract itself changes.
