# Agent Character Proposal

Design a desire/fear/weakness-driven character model.

## Responsibilities

- maintain protagonist and rival motivational state
- translate desire, fear, weakness, and misbelief into episode pressure
- increase or reduce urgency based on conflict outcomes
- expose clear scene goals for prompt generation

## Required State

- `core_desire`
- `surface_goal`
- `fear_trigger`
- `weakness`
- `misbelief`
- `urgency`
- `relationship_pressure`
- `progress`
- `backlash`

## Output Contract

- current dominant motivation
- what success costs
- what failure costs
- what internal contradiction can break execution

## Failure To Avoid

- milestone progression by fixed episode counts
- generic “character growth” without decision pressure
