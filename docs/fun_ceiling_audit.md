# Fun Ceiling Audit

## Goal

Push web novel fun generation toward the current structural ceiling by replacing timer-based heuristics and keyword proxies with explicit story-state engines.

## Repository Scan Summary

Primary generation path:

- `engine/pipeline.py`
- `engine/prompts.py`
- `engine/viral.py`

Current deterministic analysis layer:

- `analytics/content_ceiling/ceiling.py`
- `analytics/content_ceiling/event_extractor.py`
- `analytics/content_ceiling/cliffhanger.py`
- `analytics/content_ceiling/emotional_curve.py`
- `analytics/content_ceiling/cognitive_rhythm.py`

Current state holders tied to story progression:

- `engine/character_arc.py`
- `engine/conflict_memory.py`
- `engine/predictive_retention.py`

## Modules Related To Story Logic, Pacing, Retention, Cliffhangers

### Story Logic

- `engine/pipeline.py`: builds outline, plan, draft, rewrite loop, score logging
- `engine/prompts.py`: translates internal story state into model instructions
- `engine/character_arc.py`: current protagonist arc state
- `engine/conflict_memory.py`: current conflict progression state

### Pacing And Tension

- `engine/pipeline.py`: hook/payoff/compression/novelty knobs
- `engine/fatigue.py`: reset directives
- `engine/damping_controller.py`
- `engine/intensity_lock.py`
- `analytics/content_ceiling/emotional_curve.py`
- `analytics/content_ceiling/cognitive_rhythm.py`

### Retention

- `engine/predictive_retention.py`
- `engine/viral.py`
- `analytics/content_ceiling/ceiling.py`
- `analytics/content_ceiling/human_guidance.py`

### Cliffhangers

- `engine/prompts.py`
- `engine/viral.py`
- `analytics/content_ceiling/cliffhanger.py`

## Hard Fun Limits Found

### Character Engine Is Essentially A Timer

`engine/character_arc.py`:

- protagonist stage increases every 10 episodes
- no desire, fear, weakness, leverage, relationship, or pressure state
- no link between character state and generated scenes

Effect:

- growth is disconnected from consequences
- no compulsion loop around need vs cost
- characters cannot produce differentiated fun on their own

### Conflict Engine Is Also A Timer

`engine/conflict_memory.py`:

- increments one integer every 7 episodes
- no unresolved threads
- no consequences
- no cost ladder
- no opposition strategy

Effect:

- escalation is fake
- danger does not compound
- reversals and betrayals have no memory substrate

### Event Logic Is Missing

`engine/pipeline.py` currently asks the LLM for scenes directly from outline plus knobs.

Missing:

- typed event planning
- event prerequisites
- event consequences
- event role in the tension curve

Effect:

- reveals, reversals, betrayals, losses, and arrivals are left to prompt luck

### Cliffhanger Logic Is Surface-Level

`analytics/content_ceiling/cliffhanger.py`:

- classifies cliffhangers by counting punctuation and stock phrases

`engine/viral.py`:

- only checks that the string exists and is at least 8 characters

Effect:

- a technically valid but weak line passes
- no pressure propagation into the next episode
- no relation to unresolved threads or withheld consequence

### Retention Model Is Too Thin

`engine/predictive_retention.py` uses score summary plus fatigue only.

Missing:

- unresolved thread pressure
- promised payoff inventory
- threat proximity
- consequence debt
- curiosity debt

Effect:

- retention is not tied to serial compulsion

### Analytics Use Simplistic Heuristics

`analytics/content_ceiling/event_extractor.py`:

- event detection via word-list hits
- escalation steps inferred from token density spikes

`analytics/content_ceiling/ceiling.py`:

- total score is driven by keyword counts and sentence-length variance

Effect:

- the system can score “loud” text above structurally fun text
- no distinction between organic escalation and random noise

## Redesign Direction

Replace shallow proxies with six explicit subsystems:

1. Character desire engine
2. Conflict escalation engine
3. Typed event generator
4. Cliffhanger generator
5. Tension wave controller
6. Retention engine based on unresolved thread pressure

## Bottlenecks In Order

1. No durable character motivation model
2. No consequence-driven conflict graph
3. No typed event planning layer
4. No structural cliffhanger generation
5. No intentional wave control across episodes
6. No retention pressure accounting

## Ceiling Thesis

The next meaningful increase in fun potential does not come from tuning the existing knob values. It comes from giving the generator a persistent story machine that tracks desire, fear, weakness, cost, consequence, and unresolved pressure, then forcing every episode to spend or amplify those assets.
