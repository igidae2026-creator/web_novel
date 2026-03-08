# Agent Event Proposal

Implement a typed event generator.

## Event Types

- `reveal`
- `betrayal`
- `reversal`
- `loss`
- `arrival`

## Responsibilities

- choose events from state prerequisites
- attach consequence payloads
- ensure event variety
- feed prompt scaffolding and analytics

## Required Output

- `type`
- `trigger`
- `target_thread`
- `stakes`
- `consequence`
- `carryover_pressure`

## Failure To Avoid

- random event choice with no state basis
- duplicate event types without new consequences
