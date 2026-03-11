# Web Novel Alignment Status

## Purpose

This document records how the imported governance stack currently aligns, or fails to align, with the actual `web_novel` repository.

It exists because the imported Layer 3 checklist is generic MetaOS repo mapping, while this repository currently exposes a different runtime structure.

## Current Canonical Runtime Mapping

- user-facing runtime entrypoint: `app.py`
- generation core: `engine/`
- market support: `market_layer/`
- portfolio support: `portfolio_layer/`
- business dashboards: `metaos_business/`
- tests: `tests/`
- configuration: `config.yaml`, `runtime_config*.json`

## Canonical Goal Mapping

- user task goal: `GOAL.md`
- system objective: `SYSTEM_OBJECTIVE.md`
- governance anchor: `METAOS_ANCHOR.md`

## Confirmed Mismatches Against Imported Layer 3

- imported Layer 3 references `tools/loop.py`, `tools/meta_loop.py`, and `tools/system_evolver.py`
- those files do not exist in this repository
- imported Layer 3 assumes a more generic MetaOS runtime topology than the current web-novel app exposes
- imported Layer 3 therefore cannot yet be treated as fully implemented repo truth for this repository

## Immediate Interpretation Rule

Until Layer 3 is rewritten through the patch method for this repository, use the imported Layer 3 as a governance target and use this document as the live mapping bridge.

## Priority Gaps

- no repo-specific canonical Layer 3 mapping yet
- no single documented quality scoring contract for hook, payoff, cliffhanger, pacing, and coherence
- no explicit coverage status proving each governance quality axis is enforced by code
- document boundaries are still loose; multiple plan/audit/proposal docs overlap without a strict canonical split

## Current Alignment Notes

- final threshold evaluation is now bundled into a single cycle artifact: `outputs/final_threshold_eval.json`
- the bundle currently evaluates closed-loop execution, fail-closed quality handling, append-only and replayable truth, MetaOS identity preservation, story stability, reader retention stability, adaptive edit governance, soak and fault evidence, human lift near zero, scope-authority-policy autonomy, control-loop closure, and market-feedback autoloop
- whole-repository planning is now also grouped in `/home/meta_os/web_novel/docs/governance/WEBNOVEL_SYSTEM_BUNDLES.md` so story quality, runtime autonomy, portfolio, operations, and business feedback are handled as one webnovel system rather than isolated subproblems
- a dedicated reader-facing quality contract now exists in `/home/meta_os/web_novel/docs/governance/WEBNOVEL_READER_PERCEPTION_CONTRACT.md`
- thin operational policy stubs are now consolidated into `/home/meta_os/web_novel/docs/policy_ops_guardrails.md`
- the canonical quality architecture and audit surfaces are now `/home/meta_os/web_novel/docs/absolute_ceiling_master_plan.md` and `/home/meta_os/web_novel/docs/absolute_ceiling_audit.md`, while former `fun_*` docs now live only as archived legacy pointers in `/home/meta_os/web_novel/docs/archive/`
- the old gap-map note is now a live gap ledger in `/home/meta_os/web_novel/docs/absolute_ceiling_gap_map.md`, and runtime scaling guidance now lives in `/home/meta_os/web_novel/docs/runtime_scaling_strategy.md`
- agent proposal docs now have a canonical entry surface in `/home/meta_os/web_novel/docs/agents/AGENT_SUBSYSTEM_CONTRACTS.md`
- agent proposal filenames are now normalized into `agent_*_audit.md` and `agent_*_contract.md`
- root-level policy and scaling stub files are now explicitly tracked as legacy shims in `/home/meta_os/web_novel/docs/legacy_root_stubs.md`
- failed bundle criteria are auto-converted into typed repair jobs in `domains/webnovel/runtime/job_queue.json`
- queued final-threshold repair jobs now execute at track runtime start and can force fail-closed hold before generation when high-risk criteria remain unresolved
- supervisor state now carries final-threshold readiness and blocking criteria
- certification report generation now re-runs the same bundled final-threshold evaluation instead of introducing a separate threshold surface
- long-run simulation now emits soak evidence, replay-consistency probing now emits fault-injection evidence, and runtime state now stores an estimated human quality lift signal for the bundled evaluator
- upper-tier reader-facing failures now emit direct `repair_context` directives from `engine/final_threshold.py`
- those directives are now consumed by `engine/final_threshold_runtime.py`, hardened by `engine/preflight_gate.py`, and applied inside `engine/pipeline.py` to generation knobs, rewrite budget, timeout, and market rebind context
- this closes a direct path from bundled threshold failure to next-cycle generation behavior rather than stopping at reports or queue metadata
- reader-facing repair jobs now outrank generation in `engine/job_queue.py`, set explicit `reader_quality_priority` in `engine/final_threshold_runtime.py`, escalate preflight risk in `engine/preflight_gate.py`, and influence portfolio ordering in `engine/track_queue.py`
- queue-loop budgeting now also treats stacked reader-facing failures as caution pressure, and safe overwrite policy now preserves in-place updates for queue/job/supervisor state files so control-loop closure does not leak into versioned side files
- episode attribution now accumulates `reader_quality` debt in story state, and that debt now feeds back into preflight risk and generation-time knob correction before the next episode is drafted
- reader-quality debt is now explicitly decomposed into `thinness_debt`, `repetition_debt`, `deja_vu_debt`, `fake_urgency_debt`, and `compression_debt`, so likely future heavy-reader complaints are tracked as runtime state instead of remaining doc-only warnings

## Conservative Completion Estimate

- conservative whole-goal completion against a "catch likely future criticism too" standard: `45-50%`
- upper-tier reader-perceived overall completion: `45%`
- operations and control completion: `60-70%`
- story output quality completion against upper-tier heavy-reader expectations: `35-45%`

## Estimate Basis

- the working standard is intentionally harsher than "current visible scope looks decent"
- the score assumes there are still unmeasured heavy-reader complaints, long-run drift failures, market shifts, and hidden side effects that would likely be raised later unless proactively closed now
- the system is materially stronger at fail-closed rejection, repair-first routing, bundle-level gating, and queue/supervisor closure than before
- the system is not yet consistently stronger at the reader-facing layer that matters most: early hook, addictive episode ending, long-arc payoff pressure, and low-fatigue serialization rhythm
- `final_threshold_ready=true` is not yet the default operating state
- human intervention still appears to have non-trivial lift in some paths
- long unattended runs have not yet proven repeated upper-tier reader satisfaction as a stable default

## Likely Future Criticism Vectors To Pre-Close

Treat the following as expected future criticism, not optional polish.
The conservative completion bar assumes these are either already closed or explicitly being driven toward low risk:

- perceived thinness: scenes technically progress but feel too light, too obvious, or too low-density in tension, cost, desire, or character pressure
- repetition fatigue: cliffhangers, beats, emotional turns, or conflict shapes repeat often enough that heavy readers feel serialization drag
- deja-vu drift: the series keeps moving but feels structurally familiar, recycled, or too similar to its own recent chapters
- fake urgency: chapters sound urgent without forcing meaningful irreversible choice, loss, escalation, or payoff movement
- payoff trust erosion: setup is visible but readers stop believing that promised rewards will land soon enough or hard enough
- protagonist fantasy thinning: the lead remains present but stops feeling like the center of force, agency, or aspirational momentum
- tonal flattening: prose remains readable while emotional temperature, contrast, or edge becomes too even to sustain addiction pressure
- compression failure: chapters spend too many words on already-understood beats and lose narrative density
- market adaptation lag: the system notices weakening response too slowly and keeps shipping the same pressure profile
- hidden control-loop leakage: quality appears stable locally while queue, supervisor, repair, or state drift quietly reduce convergence odds

## Conservative 100% Definition

This repo should treat `100%` as a deliberately conservative ceiling, not a flattering milestone.

The `100%` bar means all of the following are true at once:

- `final_threshold_ready=true` is the default runtime state over repeated unattended cycles
- heavy web-novel readers would continue reading for hook, payoff, episode addiction, and protagonist fantasy reasons without a person rescuing weak episodes
- reader-quality debt, arc debt, market pressure, soak evidence, and repair state all close automatically into the next cycle
- long unattended runs keep quality from drifting down into repeated rescue states
- human intervention produces near-zero marginal quality gain
- likely future criticism vectors such as perceived thinness, repetition fatigue, deja-vu drift, fake urgency, delayed payoff trust, protagonist fantasy thinning, tonal flattening, market shift response, and control-loop leakage have already been proactively closed or reduced to low risk

## Remaining Mismatches

- the reader-facing semantic contract now exists, but the broader governance stack and checklist references have not yet been updated to include it as a fully patched canonical layer
- some bundle axes still depend on runtime evidence only when soak, fault injection, or human-lift measurements are actually produced; the repo does not yet guarantee those measurements on every unattended run
- the repository still contains duplicate documentation surfaces for quality architecture, audits, and agent proposals; see `/home/meta_os/web_novel/docs/document_system_audit.md`
- non-canonical document filenames are still not normalized for fast model retrieval; see `/home/meta_os/web_novel/docs/doc_naming_standard.md`

## Next Structural Work

- rewrite Layer 3 through the patch method for this repository
- map each quality axis to concrete `engine/` modules and tests
- define measurable pass criteria for upper-tier web-novel quality
- merge overlapping doc families into one canonical quality-plan surface and one canonical audit surface
