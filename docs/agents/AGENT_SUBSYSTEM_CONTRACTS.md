# Agent Subsystem Contracts

## Purpose

This file is the canonical contract surface for agent-style subsystem proposals in this directory.
It consolidates the duplicated diagnosis and responsibility documents into one reading surface without renaming files yet.

## Canonical Subsystem Contracts

### Character

Purpose:

- maintain protagonist and rival motivational pressure that can drive differentiated scenes

Core contract:

- maintain desire, fear, weakness, misbelief, urgency, relationship pressure, progress, and backlash
- expose current dominant motivation and cost of success or failure
- prevent timer-based character growth

Source docs:

- audit: `/home/meta_os/web_novel/docs/agents/agent_character_audit.md`
- contract: `/home/meta_os/web_novel/docs/agents/agent_character_contract.md`

### Conflict

Purpose:

- escalate through consequences rather than empty intensity inflation

Core contract:

- track unresolved threads, consequence ladders, threat pressure, reversals, and opposition advantage
- propagate fallout into world and payoff systems
- avoid escalation that never changes cost structure

Source docs:

- audit: `/home/meta_os/web_novel/docs/agents/agent_conflict_audit.md`
- contract: `/home/meta_os/web_novel/docs/agents/agent_conflict_contract.md`

### Event

Purpose:

- choose typed events from story state instead of prompt luck or periodicity

Core contract:

- choose events from prerequisites
- attach consequence and carryover payloads
- preserve event variety without breaking causality

Source docs:

- audit: `/home/meta_os/web_novel/docs/agents/agent_event_audit.md`
- contract: `/home/meta_os/web_novel/docs/agents/agent_event_contract.md`

### Cliffhanger And Tension

Purpose:

- preserve addictive endings while managing serialization rhythm

Core contract:

- derive cliffhanger mode from event and consequence state
- preserve irreversible or withheld cost at the cut
- manage spike and release rhythm rather than permanent max intensity

Source docs:

- audit: `/home/meta_os/web_novel/docs/agents/agent_cliffhanger_tension_audit.md`
- contracts: `/home/meta_os/web_novel/docs/agents/agent_cliffhanger_contract.md`, `/home/meta_os/web_novel/docs/agents/agent_tension_contract.md`

### Information And Emotion

Purpose:

- control reveal pacing and emotional payoff through state rather than prompt luck

Core contract:

- maintain hidden-truth and revealed-truth ledgers
- manage foreshadow queue and dramatic irony
- prevent reveal spam and payoff starvation

Source docs:

- audit: `/home/meta_os/web_novel/docs/agents/agent_information_emotion_audit.md`

### Retention

Purpose:

- estimate and manage next-click pressure through unresolved consequence quality

Core contract:

- combine unresolved thread pressure, threat proximity, payoff debt, and curiosity debt
- identify weak continuation hooks before generation passes
- avoid retention predicted only from score summaries

Source docs:

- contract: `/home/meta_os/web_novel/docs/agents/agent_retention_contract.md`

### State Architecture

Purpose:

- keep subsystem state unified enough that all major engines can optimize the same story machine

Core contract:

- preserve `story_state_v2` as the primary runtime state
- maintain compatibility projections only as secondary views
- avoid drift between canonical state and alias projections

Source docs:

- audit: `/home/meta_os/web_novel/docs/agents/agent_state_architecture_audit.md`

### Adaptation And Exploration

Purpose:

- improve novelty and pattern control without random collapse

Core contract:

- maintain novelty budget and exploration budget
- tie exploration to serialization and portfolio memory
- avoid random novelty spikes that break stability

Source docs:

- audit: `/home/meta_os/web_novel/docs/agents/agent_adaptation_exploration_audit.md`

### Regression Guard

Purpose:

- reject one-axis gains that damage the protected quality profile

Core contract:

- maintain protected axis list
- make before or after decisions explicit
- reject bad tradeoffs rather than reporting them as wins

Source docs:

- audit: `/home/meta_os/web_novel/docs/agents/agent_regression_guard_audit.md`

### Tests And Docs

Purpose:

- prevent subsystem drift between code, tests, and documents

Core contract:

- keep deterministic fixtures for state mutation and evaluation
- keep canonical docs aligned with code authority
- avoid shallow test surfaces that only cover first-pass functionality

Source docs:

- audit: `/home/meta_os/web_novel/docs/agents/agent_tests_docs_audit.md`

### Webnovel Fit

Purpose:

- keep serialization, reward pacing, chemistry, and sustainability aligned with commercial webnovel expectations

Core contract:

- track pending vs delivered promises
- keep chemistry and sustainability explicit
- avoid short-run reward spikes that bankrupt long-run trust

Source docs:

- audit: `/home/meta_os/web_novel/docs/agents/agent_webnovel_fit_audit.md`

## Reading Rule

Use this file first.
Use the linked audit and contract docs only when deeper subsystem detail is needed.

## Future Normalization

The eventual target remains:

- `agent_<name>_audit.md`
- `agent_<name>_contract.md`

That naming family is now in use.
This file remains the canonical overview.
