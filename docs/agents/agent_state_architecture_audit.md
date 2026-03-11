# Agent State Architecture

## Diagnosis

Runtime state was fragmented and lacked a canonical schema.

## Ceiling Bottleneck

No subsystem could reliably optimize or protect all narrative axes together because they read/write different partial dicts.

## Missing Architecture

- unified cast state
- relationship graph
- world state
- unresolved thread ledger
- pacing and reward portfolios
- serialization memory

## Proposed Subsystem

`story_state_v2` in [engine/story_state.py](/mnt/c/Users/LG/Desktop/METAOS_FINAL_FULL_BUILD/engine/story_state.py)

## Integration Points

- consumed by character/conflict/event/tension/retention logic
- projected back to legacy aliases for compatibility

## Regression Risks

- migration bugs from old state
- stale alias state if sync is skipped

## Test Plan

- initialize from empty state
- initialize from legacy partial state
- verify alias projection stays consistent after updates
