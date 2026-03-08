# Fun Engine Master Plan

## Target Architecture

The generation stack should move from:

- outline -> plan -> draft -> rewrite

To:

- outline
- character desire state
- conflict escalation state
- tension wave target
- typed event slate
- episode plan
- draft
- structural cliffhanger pass
- rewrite
- retention pressure update
- deterministic ceiling analysis

## Core State Model

### Character State

- `desire`
- `fear`
- `weakness`
- `misbelief`
- `urgency`
- `relationship_pressure`
- `progress`
- `backlash`

### Conflict State

- unresolved threads
- threat actor pressure
- consequence ladder
- recent event types
- payoff debt

### Tension State

- target band
- current band
- recent peaks
- release debt
- spike debt

### Retention State

- unresolved thread pressure
- curiosity debt
- threat proximity
- promised payoff pressure
- betrayal/reveal carryover

## Implementation Order

1. Character desire engine
2. Conflict escalation engine
3. Typed event generator
4. Cliffhanger generator
5. Tension wave controller
6. Retention upgrade

## Integration Rules

### Rule 1

Every episode must be generated from state, not only from static outline plus platform knobs.

### Rule 2

Every major event must create either:

- a new unresolved thread
- a raised consequence
- a partial payoff with new cost

### Rule 3

Cliffhangers must point at a concrete withheld consequence, not generic suspense wording.

### Rule 4

Tension must wave. Sustained max intensity without release lowers headroom and burns fun potential.

### Rule 5

Retention should optimize for unresolved pressure quality, not just score averages.

## Iterative Ceiling Search Method

After all six subsystems are in place:

1. inspect ceiling metrics, state payloads, and test coverage
2. identify the subsystem still using the weakest abstraction
3. redesign that subsystem if the gain is structural rather than cosmetic
4. implement the redesign
5. run validation
6. stop only when remaining improvements are mostly parameter tuning, not architecture

## Planned End-State

The final generator should be able to answer, deterministically and before drafting:

- what the protagonist wants now
- what they fear losing now
- what weakness can sabotage them now
- what conflict will worsen if they fail now
- what event type should fire now
- what kind of cliffhanger should close now
- what unresolved pressure will force the next click

## Implemented Status

- character desire engine: implemented
- conflict escalation engine: implemented
- typed event generator: implemented
- cliffhanger generator: implemented
- tension wave controller: implemented
- retention pressure engine: implemented
- iterative ceiling search pass 1: implemented

## Ceiling Search Result

The strongest remaining structural gap after pass 1 is not a missing subsystem in runtime state. It is semantic depth:

- richer relationship graph memory
- scene-level causality validation against actual LLM output
- antagonist planning distinct from protagonist pressure

These are real upgrades, but they are a larger second-generation architecture rather than a missing first-order subsystem. Within the current repository shape, the highest-value structural gains have been exhausted.
