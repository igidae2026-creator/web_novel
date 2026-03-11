# Absolute Ceiling Audit

This is the canonical quality-audit surface.
It supersedes the older parallel archived audit surface `docs/archive/archive_fun_ceiling_audit.md`.

## Summary

The repository started as a mixed analytics + generation tool with a strong bias toward content scoring, dashboarding, and platform knobs. It had useful runtime hooks for character pressure, conflict memory, event typing, cliffhanger shaping, tension waves, and retention prediction, but those systems were shallow and only partially state-driven.

The main ceiling blockers were:

- generation logic was still largely guided by outline + knobs + score history
- state was fragmented and lacked a canonical schema for characters, relationships, world change, unresolved promises, and serialization pressure
- conflict and pacing logic relied on coarse counters and episode/modulo triggers
- evaluation favored weighted sums over protected multi-objective balancing
- world logic, chemistry, and long-run sustainability had no regression protection

## Repository Scan

### Generation Entrypoints

- [app.py](/mnt/c/Users/LG/Desktop/METAOS_FINAL_FULL_BUILD/app.py): Streamlit entrypoint, outline generation, episode generation controls, track orchestration UI.
- [engine/pipeline.py](/mnt/c/Users/LG/Desktop/METAOS_FINAL_FULL_BUILD/engine/pipeline.py): main runtime path for outline -> plan -> draft -> rewrite -> score -> metrics/state update.
- [engine/prompts.py](/mnt/c/Users/LG/Desktop/METAOS_FINAL_FULL_BUILD/engine/prompts.py): LLM prompt assembly layer.

### State Schemas

- [engine/state.py](/mnt/c/Users/LG/Desktop/METAOS_FINAL_FULL_BUILD/engine/state.py): generic JSON store only, no domain schema.
- [docs/state_schema.yaml](/mnt/c/Users/LG/Desktop/METAOS_FINAL_FULL_BUILD/docs/state_schema.yaml): legacy state schema doc, not enough for multi-objective webnovel optimization.
- Previous runtime state lived in ad hoc dicts: `character_arcs`, `conflict_engine`, `tension_wave`, `retention_engine`, `story_events`.

### Story Logic

- [engine/character_arc.py](/mnt/c/Users/LG/Desktop/METAOS_FINAL_FULL_BUILD/engine/character_arc.py): had desire/fear/weakness/misbelief, but lacked wound, lie, moral limit, obsession, contradiction, explicit relationship debt.
- [engine/conflict_memory.py](/mnt/c/Users/LG/Desktop/METAOS_FINAL_FULL_BUILD/engine/conflict_memory.py): escalated pressure from recent weak scores and open threads, but world consequences were shallow.
- [engine/event_generator.py](/mnt/c/Users/LG/Desktop/METAOS_FINAL_FULL_BUILD/engine/event_generator.py): typed events existed, but selection was still partly modulo-driven and narrow.
- [engine/cliffhanger_engine.py](/mnt/c/Users/LG/Desktop/METAOS_FINAL_FULL_BUILD/engine/cliffhanger_engine.py): worked on withheld consequence/open question, but not enough irreversible cost modeling.

### Pacing / Retention / Cliffhanger Logic

- [engine/tension_wave.py](/mnt/c/Users/LG/Desktop/METAOS_FINAL_FULL_BUILD/engine/tension_wave.py): had spike/release/pressure bands, but no serialization sustainability feedback.
- [engine/predictive_retention.py](/mnt/c/Users/LG/Desktop/METAOS_FINAL_FULL_BUILD/engine/predictive_retention.py): modeled unresolved pressure, but not chemistry or information asymmetry.
- [analytics/content_ceiling/cliffhanger.py](/mnt/c/Users/LG/Desktop/METAOS_FINAL_FULL_BUILD/analytics/content_ceiling/cliffhanger.py): analyzed closing structure, but still with simple keyword checks.

### Analytics Modules

- [analytics/content_ceiling/ceiling.py](/mnt/c/Users/LG/Desktop/METAOS_FINAL_FULL_BUILD/analytics/content_ceiling/ceiling.py): central evaluator, previously a weighted content-only score.
- [analytics/content_ceiling/axes.py](/mnt/c/Users/LG/Desktop/METAOS_FINAL_FULL_BUILD/analytics/content_ceiling/axes.py): lexical proxy metrics.
- [reports/content_ceiling_report.py](/mnt/c/Users/LG/Desktop/METAOS_FINAL_FULL_BUILD/reports/content_ceiling_report.py): reporting layer.

### Orchestration / Operations

- [engine/track_generator.py](/mnt/c/Users/LG/Desktop/METAOS_FINAL_FULL_BUILD/engine/track_generator.py), [engine/track_runner.py](/mnt/c/Users/LG/Desktop/METAOS_FINAL_FULL_BUILD/engine/track_runner.py), [engine/portfolio_orchestrator.py](/mnt/c/Users/LG/Desktop/METAOS_FINAL_FULL_BUILD/engine/portfolio_orchestrator.py): portfolio and multi-track orchestration.
- Multiple market/competition modules exist, but they mostly influence knobs and track policy, not deep story state.

### Tests

- Existing tests focused on `fun` subsystems: character, conflict, event generator, cliffhanger, tension wave, retention, ceiling loop.
- Coverage for world change, chemistry, reward density vs sustainability, and regression guard was missing.

### Docs / Dashboards

- Streamlit dashboards for revenue, KPI, campaigns.
- Existing docs were centered on `fun_ceiling` and operational notes rather than canonical narrative architecture.

## Shallow / Limiting Patterns Detected

### Keyword-only or lexical evaluation

- `analytics/content_ceiling/*` used lexical counts as primary evidence.
- This was useful as a proxy but not sufficient as the canonical objective.

### Modulo-based progression

- Event/tension cadence still used `episode % N` logic in selection.
- This hard-limits adaptive pacing and causes visible periodicity.

### Simplistic weighted sums

- [engine/multi_objective.py](/mnt/c/Users/LG/Desktop/METAOS_FINAL_FULL_BUILD/engine/multi_objective.py) originally reduced balance to `hook + emotion + escalation - repetition`.
- [analytics/content_ceiling/ceiling.py](/mnt/c/Users/LG/Desktop/METAOS_FINAL_FULL_BUILD/analytics/content_ceiling/ceiling.py) originally produced a large weighted total without regression protection.

### State without real desire / consequence / relationship pressure

- Character state lacked explicit wound/lie/moral limit/obsession/contradiction.
- Relationship state was implicit or absent.
- Conflict consequences existed, but irreversible outcomes were weakly modeled.

### Pacing without rhythm control strong enough for serialization

- Tension wave existed, but long-run sustainability was not used to modulate intensity.

### Retention without unresolved pressure quality

- Retention mostly counted unresolved pressure and tension, not chemistry, information gaps, or payoff portfolio shape.

### World logic without real state transitions

- Major events did not consistently mutate world order, instability, change rate, or timer structures.

### Market logic without serialization dynamics

- Market/portfolio layers were strong operationally, but generation-side serialization state was shallow.

## First-Order Fun Bottlenecks

The following limits were originally severe enough to cap reader-facing fun:

### Character state acting like a timer

- growth divorced from consequences
- weak desire, fear, leverage, and relationship pressure
- limited conversion from character state into scene compulsion

### Conflict escalation acting like a timer

- shallow unresolved-thread memory
- weak cost ladders
- weak consequence compounding
- little substrate for betrayal, reversal, or opponent pressure

### Missing typed event planning

- too much dependence on outline plus prompt luck
- weak event prerequisite tracking
- weak consequence binding

### Surface-level cliffhanger validation

- generic suspense wording could pass
- next-episode pressure was weakly tied to withheld consequence

### Thin retention model

- unresolved pressure quality, curiosity debt, and payoff inventory were under-modeled

### Simplistic analytics heuristics

- loud text could score above structurally strong text
- keyword and density proxies could overstate fun

## Audit Conclusion

The repo was not a toy. It already had enough structure to be upgraded rather than discarded wholesale. The correct move was:

- keep the generation pipeline shell
- introduce a canonical unified story state
- upgrade character/conflict/event/cliffhanger/tension/retention around that state
- add information/emotion, world logic, reward/serialization, and regression guard subsystems
- upgrade evaluation to protect a balanced system profile instead of a single-axis ceiling

The remaining ceiling blockers are now mostly second-generation:

- richer relationship graph memory
- opponent-side planning and counter-strategy
- scene-level realization checks against drafted output
