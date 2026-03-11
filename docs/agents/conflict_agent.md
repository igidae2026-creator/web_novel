# Agent Conflict Proposal

Design an escalation system based on consequences.

## Responsibilities

- track unresolved conflict threads
- maintain consequence ladders
- raise costs when threads are ignored
- recommend escalation mode for the next episode

## Required State

- `threads`
- `threat_pressure`
- `consequence_level`
- `recent_losses`
- `recent_reversals`
- `opposition_advantage`

## Escalation Modes

- complication
- exposure
- sacrifice
- race-against-time
- collateral-damage
- power-reversal

## Failure To Avoid

- escalation by keyword inflation
- pressure that never changes the cost structure
