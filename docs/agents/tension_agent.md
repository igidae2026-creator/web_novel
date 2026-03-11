# Agent Tension Proposal

Implement tension wave control.

## Responsibilities

- target episode tension bands
- alternate compression, release, and spike windows
- prevent flatlining at low or high intensity
- guide event selection toward wave needs

## Required State

- `target_tension`
- `recent_tension`
- `peak_count`
- `release_debt`
- `spike_debt`

## Failure To Avoid

- constant escalation
- constant release
- no distinction between local spike and arc-level wave
