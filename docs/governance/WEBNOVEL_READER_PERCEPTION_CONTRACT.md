# WEBNOVEL_READER_PERCEPTION_CONTRACT

## Purpose

This document defines the measurable reader-facing quality contract for the repository.
It is narrower than the constitution and more concrete than the quality map.
Its job is to answer one question:

`what must be true for heavy web-novel readers to feel that the output is upper-tier rather than merely acceptable`

## Canonical Bundles

Reader-facing quality is judged through four large bundles.

### 1. Entry Compulsion

The work must make a strong reader continue signal early.

Required qualities:

- the early chapter opening must present desire, cost, danger, or irreversible disruption quickly
- the protagonist situation must feel immediately asymmetric enough to create curiosity or hunger
- the reader must understand why this story is worth following now rather than later

Minimum contract signals:

- `early_hook_strength`
- `reader_retention_stability`

### 2. Episode Addiction

Each episode must preserve next-click pressure.

Required qualities:

- the episode ending must not collapse into generic suspense wording
- the ending must preserve a concrete withheld consequence, choice cost, reveal edge, or irreversible next-step pressure
- the episode body must not spend all tension without leaving meaningful carryover

Minimum contract signals:

- `episode_end_hook_strength`
- `reader_retention_stability`
- `quality_gate_fail_closed`

### 3. Long-Arc Trust

The series must persuade readers that staying invested will pay off.

Required qualities:

- promises must convert into payoff, escalation, or cost rather than indefinite delay
- world and character logic must remain reliable enough that tension feels earned
- long arcs must feel like accumulation, not drift

Minimum contract signals:

- `story_quality_stability`
- `long_arc_payoff_stability`
- `append_only_truth_lineage_replayability`

### 4. Serial Fantasy Endurance

The work must sustain protagonist fantasy and serialization rhythm over time.

Required qualities:

- the protagonist must keep generating persuasive momentum, not only passive suffering
- fantasy fulfilment must coexist with cost, escalation, and consequence
- the release rhythm must avoid obvious fatigue, repetition drift, or payoff bankruptcy

Minimum contract signals:

- `protagonist_fantasy_persistence`
- `serialization_fatigue_control`
- `reader_retention_stability`

## Explicit Heavy-Reader Failure Vectors

The system should assume heavy readers will later complain about the following if they are not actively suppressed:

- thinness: scenes move but do not feel dense enough in desire, cost, danger, status movement, or emotional force
- repetition fatigue: hooks, reversals, reveals, and end beats feel reused often enough to reduce addiction
- deja-vu serialization: the work keeps progressing while feeling too similar to its own recent rhythm
- fake cliffhanger pressure: episode endings imply urgency without paying with real consequence or irreversible movement
- payoff bankruptcy: promises remain legible but confidence in eventual reward decays
- protagonist fantasy thinning: the lead is present but no longer feels dominant, covetable, or meaningfully world-bending
- tonal flattening: prose remains competent while edge, surprise, and emotional contrast drain away
- over-explanation and low compression: chapters spend too much time restating known material instead of converting it into sharper pressure

These are not secondary complaints.
If they remain visible, heavy-reader trust is not upper-tier even when the work is technically coherent.

## Failure Interpretation

Fail any one of the four bundles and the output is not upper-tier from a heavy-reader perspective.

This is intentional.
The product bar is not:

- readable prose alone
- one strong hook alone
- one emotional scene alone
- high average scores with weak addiction pressure

It is bundle-complete trust and compulsion.

## Mapping To Final Threshold

The runtime final threshold must reflect this contract through explicit criteria rather than vague narrative quality claims.

Current reader-facing criteria:

- `early_hook_strength`
- `episode_end_hook_strength`
- `long_arc_payoff_stability`
- `protagonist_fantasy_persistence`
- `serialization_fatigue_control`
- `reader_retention_stability`
- `story_quality_stability`

## Required Evidence Types

The contract is not satisfied by descriptive prose in docs alone.
It should be grounded in:

- quality gate checks
- attribution signals
- retention and fatigue signals
- promise/payoff graph state
- causal and ceiling reports
- repeated unattended runtime evidence

## Non-Goals

This contract does not define:

- constitutional invariants
- job queue schema
- supervisor schema
- patch governance
- broad repo mapping

Those belong elsewhere.

## Current Gap

The repo now reflects parts of this contract in code, but not all of it is guaranteed as a canonical governance surface yet.
Until the broader governance stack is updated, use this document as the reader-facing quality contract reference and use `WEBNOVEL_ALIGNMENT_STATUS.md` as the live mismatch ledger.

## Current Implementation Direction

The canonical direction for this repo is no longer just "evaluate these bundles after generation."

The system should:

- accumulate reader-facing debt when hook, episode addiction, payoff, fatigue, or protagonist fantasy weaken
- convert that debt into repair priority, preflight pressure, prompt pressure, and generation-time knob changes
- treat thinness, repetition fatigue, deja-vu drift, fake cliffhangers, tonal flattening, and payoff trust erosion as first-class debt sources rather than vague taste complaints
- keep explicit debt memory for thinness, repetition, deja-vu drift, fake urgency, and low compression so these complaints survive beyond one bad episode and alter the next cycle
- keep doing this through unattended cycles until heavy-reader bundle closure becomes the default runtime state
- treat "looks good in the current visible scope" as insufficient until likely future heavy-reader complaints and long-run drift risks are also proactively reduced
