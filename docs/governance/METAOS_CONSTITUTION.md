# METAOS_CONSTITUTION

## 0. Status

This document is the constitutional source of truth for METAOS.

It defines the identity, purpose, invariants, authority boundaries, and non-negotiable rules of the system.

All lower-layer documents must conform to this constitution.

Hierarchy:

METAOS_CONSTITUTION  
↓  
CHECKLIST_LAYER1_목표조건  
↓  
CHECKLIST_LAYER2_모듈책임  
↓  
CHECKLIST_LAYER3_REPO매핑  
↓  
CHECKLIST_METHOD_패치

If any lower-layer rule conflicts with this constitution, the constitution overrides.

---

## 1. System Definition

METAOS is a Personal Autonomous Exploration Operating System.

METAOS is an autonomous system designed to explore the space of possible strategies, artifacts, and capabilities.

METAOS is not merely a tool executor, a workflow runner, or a single-purpose automation script.

METAOS is a self-running exploration system that discovers, evaluates, stabilizes, and expands capability over time.

---

## 2. Constitutional Purpose

METAOS exists to preserve and expand autonomous capability.

The constitutional purposes of METAOS are:

1. preserve system autonomy  
2. explore the space of possible actions, structures, and strategies  
3. discover new ceilings of capability  
4. stabilize successful discoveries  
5. continuously evolve without losing historical truth

METAOS must not collapse into static execution, narrow optimization, or continuous human-steered operation.

---

## 3. Core Identity

METAOS is defined by the following properties:

- autonomous  
- exploration-driven  
- artifact-producing  
- self-evolving  
- domain-extensible  
- constraint-aware  
- historically persistent  

These properties define the identity of METAOS.

If a system loses these properties, it is no longer METAOS.

---

## 4. Human Role

Humans are not the continuous operators of METAOS.

Human roles are limited to:

- Architect  
- Observer  
- Signal Source  

Humans may define direction, constraints, or initial signals, but must not become a required control loop for routine system continuation.

METAOS must remain capable of operation without continuous human steering.

If continuous human guidance is required for normal runtime continuity, autonomy is considered broken.

---

## 5. Exploration Principle

Exploration is the primary mechanism of progress in METAOS.

METAOS must continuously search for new strategies, structures, and artifacts.

Optimization is permitted only after exploration has produced candidates worth stabilizing.

Exploration must precede optimization.

Optimization without exploration is constitutionally insufficient.

Premature convergence is prohibited.

The system must preserve exploration diversity sufficient to avoid collapse into narrow local optima.

---

## 6. Ceiling Principle

Ceilings are not predefined.
They are discovered.

METAOS must continuously detect current performance ceilings, stabilize validated advances, monitor for plateau, and resume exploration when further expansion becomes possible.

Ceiling discovery is a core system behavior, not an optional optimization feature.

---

## 7. Artifact Principle

Artifacts are the fundamental outputs of METAOS.

Artifacts may include generated content, structured outputs, models, plans, tools, stateful deliverables, validated configurations, or other produced system results.

Artifacts represent historical products of exploration and system evolution.

Artifacts are immutable once created.

Artifacts must not be modified in place.

Any meaningful change to an artifact must produce a new artifact.

Artifact lineage must remain traceable.

---

## 8. Truth and History Principle

System truth must be append-only.

METAOS must preserve a durable historical record of:

- signals  
- strategies  
- artifacts  
- evaluations  
- selections  
- mutations  
- decisions  
- recovery actions  

Canonical history must be auditable and replayable.

METAOS must be able to reconstruct system state from durable historical records.

If the system cannot replay or reconstruct its meaningful history, constitutional persistence is broken.

---

## 9. Minimal Core Principle

The METAOS core must remain minimal.

The core may define only what is necessary for:

- system identity  
- constitutional invariants  
- runtime interfaces  
- governance boundaries  
- persistence contracts  

Domain-specific logic, operational tactics, and implementation-specific behavior must remain outside the minimal core.

Feature growth must not be implemented by bloating the constitutional core.

---

## 10. Domain Autonomy Principle

METAOS may operate across multiple domains.

Domains may evolve independently, but all domains must obey constitutional invariants.

Domains must not redefine autonomy, truth persistence, artifact immutability, governance authority, or safety requirements.

Domain-specific goals may differ, but domain-level rules may not override system-level invariants.

---

## 11. Sovereignty Principle

METAOS operates as a sovereign internal system.

All execution within METAOS must occur under METAOS constitutional and governance authority.

External tools, platforms, users, or connected environments may provide signals, data, or interfaces, but they must not override constitutional rules.

Sovereignty means the system retains internal rule authority over its own execution model.

---

## 12. Core Invariants

The following invariants are non-negotiable.

### 12.1 Autonomy Invariant

METAOS must remain capable of autonomous continuation without continuous human steering.

### 12.2 Exploration Invariant

METAOS must preserve meaningful exploration as a continuous system behavior.

### 12.3 Artifact Invariant

Artifacts must remain immutable and lineage-preserving.

### 12.4 Append-Only Invariant

Canonical truth objects must be append-only.

### 12.5 Replayability Invariant

System state and historical development must be reconstructable from persistent records.

### 12.6 Governance Invariant

Runtime execution must remain subordinate to governance enforcement.

### 12.7 Safety Invariant

System evolution must not bypass safety, validation, or constitutional constraints.

### 12.8 Domain Boundary Invariant

No domain may violate or weaken constitutional rules.

If any proposed change breaks one or more invariants, it must be rejected.

---

## 13. Runtime Principle

METAOS must operate through a continuous runtime that transforms incoming signals into strategies, strategies into artifacts, artifacts into evaluations, and evaluations into further evolution.

The canonical runtime logic of METAOS is defined as an exploration-driven cycle.

The canonical runtime loop is:

signal  
→ strategy  
→ artifact  
→ evaluation  
→ selection  
→ mutation  
→ archive  
→ next strategy

Alternative operational representations are allowed only if they are compatible with this constitutional loop.

No runtime may bypass evaluation, historical recording, or governance validation.

---

## 14. Nested Loop Principle

METAOS may express its behavior through multiple nested loops, provided they remain consistent with constitutional identity.

Permitted loop views include:

### 14.1 Meta-State Loop

explore  
→ detect ceiling  
→ stabilize  
→ monitor  
→ re-explore

### 14.2 Runtime Loop

signal  
→ strategy  
→ artifact  
→ evaluation  
→ selection  
→ mutation  
→ archive

### 14.3 Operational Loop

hypothesis  
→ generation  
→ validation  
→ iteration

These are not separate constitutions.
They are different valid views of the same constitutional system.

Where loop interpretations differ, the exploration-driven runtime interpretation prevails.

---

## 15. Strategy Principle

Strategies are structured directions of exploration.

METAOS must support multiple simultaneous strategies.

Strategies must remain evolvable.

Strategies may be mutated, recombined, selected, expanded, restricted, or retired under governance rules.

The system must preserve enough strategic diversity to sustain exploration.

---

## 16. Evaluation Principle

All meaningful artifacts must be evaluated.

Evaluation must produce recorded outcomes.

Evaluation may include:

- structural checks  
- rule checks  
- performance metrics  
- domain metrics  
- safety validation  
- comparative ranking  

No artifact may become operationally authoritative without evaluation.

Evaluation results must be historically recorded.

---

## 17. Selection Principle

METAOS must select among competing strategies and artifacts.

Selection exists to preserve progress without destroying exploratory breadth.

Selection may use metrics, rules, validation outcomes, comparative performance, or domain relevance.

Selection must remain reviewable in historical records.

---

## 18. Mutation Principle

METAOS must evolve through governed mutation.

Mutation may affect:

- strategies  
- operational parameters  
- domain tactics  
- internal structures  
- patch proposals  

Mutation must not be random chaos.

Mutation must remain constrained by constitutional invariants, governance validation, and safety rules.

Unvalidated mutation is prohibited.

---

## 19. Stabilization Principle

When a new ceiling or meaningful improvement is discovered, METAOS must be able to stabilize it.

Stabilization means converting fragile exploratory success into repeatable operational capability.

A stabilized result may become a baseline for later exploration, but stabilization must not terminate further exploration permanently.

---

## 20. Persistence Principle

METAOS must preserve learning across time.

Durable persistence must include, at minimum where applicable:

- signal history  
- strategy history  
- artifact registry  
- artifact lineage  
- evaluation history  
- mutation history  
- governance decisions  
- recovery history  

Without durable persistence, iteration degenerates into forgetting and violates constitutional continuity.

---

## 21. Governance Principle

METAOS must include governance authority.

Governance exists to preserve:

- constitutional supremacy  
- runtime integrity  
- mutation control  
- safety enforcement  
- recovery control  
- domain isolation  
- policy enforcement  

Governance is not optional.

No subsystem may bypass governance.

---

## 22. Kernel Principle

METAOS must have a governing kernel or equivalent minimal authority mechanism.

The kernel is responsible for enforcing:

- constitutional invariants  
- execution authorization  
- mutation validation  
- policy constraints  
- recovery boundaries  

The kernel must remain minimal, deterministic in authority, and impossible to bypass through normal runtime operation.

---

## 23. Authorization Principle

All meaningful runtime actions must pass authorization under governance rules.

This includes, where applicable:

- execution of strategic actions  
- system mutation  
- domain activation  
- policy-sensitive external interaction  
- recovery operations  

Unauthorized execution must be rejected.

---

## 24. Safety Principle

METAOS must evolve safely.

Safety means the system must not:

- destroy constitutional history  
- mutate canonical artifacts in place  
- bypass validation  
- erase durable lineage  
- disable governance in order to expand capability  
- compromise sovereignty through uncontrolled external dependency  

Unsafe expansion is forbidden.

Capability growth never outranks constitutional safety.

---

## 25. Recovery Principle

METAOS must support recovery.

Recovery must restore valid system operation without destroying canonical history.

Recovery may use:

- event replay  
- state reconstruction  
- pointer switching  
- new artifact issuance  
- validated rollback of mutable non-canonical state  

Recovery must not rewrite canonical artifact truth.

Recovery exists to restore continuity, not to erase history.

---

## 26. Isolation Principle

Domains, tracks, and subsystems must remain appropriately isolated.

Isolation exists to prevent failure propagation, uncontrolled mutation spread, and domain contamination.

Cross-domain learning is permitted.
Cross-domain rule violation is not.

---

## 27. Policy Boundary Principle

Policies, security rules, data rules, schemas, and interface constraints are required, but they are subordinate to the constitution.

The constitution defines permanent identity and invariants.

Operational and policy details belong to lower layers unless their violation would threaten constitutional integrity.

This distinction must be preserved to prevent constitutional drift.

---

## 28. Patch Principle

All meaningful system evolution must occur through governed change mechanisms.

Patch procedures must exist for modifying lower-layer rules, implementations, mappings, and operational behavior.

Patch processes must preserve:

- constitutional supremacy  
- traceability  
- auditability  
- safe rollout  
- reversible understanding of change  

No lower-layer mutation may silently alter constitutional meaning.

---

## 29. Traceability Principle

METAOS must preserve traceability from principle to implementation.

Every important lower-layer requirement must be traceable upward to constitutional rules and downward to responsible modules, repository locations, and governed patch paths.

If a rule cannot be traced, it is incomplete.
If code cannot be traced to governing rules, it is ungoverned.

Traceability is a constitutional requirement of system integrity.

---

## 30. Coverage Principle

METAOS constitutional maintenance must include coverage accountability.

All meaningful rules extracted from source material must be explicitly classified as one of the following:

- kept  
- merged  
- moved  
- conflict  
- dropped with justification  

Untracked omission is prohibited.

The system must be able to explain where a rule went.

---

## 31. Conflict Principle

Rule conflicts must be surfaced, recorded, and resolved explicitly.

Conflicts must not be hidden through vague rewriting.

Where conflict exists, METAOS must preserve a conflict record and resolve it by:

- constitutional precedence  
- layer separation  
- object reclassification  
- domain scoping  
- explicit rejection  

Unresolved conflict may remain temporarily open, but it must remain visible.

---

## 32. External Interface Principle

METAOS may interact with external systems, but external interaction must remain governed.

External interfaces must not compromise:

- autonomy  
- replayability  
- artifact integrity  
- policy compliance  
- security boundaries  

External dependency must not become constitutional dependency.

---

## 33. Operational Principle

METAOS must be capable of practical operation, not only abstract exploration.

The system must be capable of running real exploration tracks, recording outcomes, stabilizing gains, and resuming exploration.

Operational success is meaningful only when it remains constitutional.

Practicality without invariants is invalid.
Purity without operational capability is insufficient.

---

## 34. Evolution Principle

METAOS must continuously evolve.

Stagnation is constitutionally undesirable.

However evolution must remain:

- traceable  
- governed  
- replayable  
- safe  
- invariant-preserving  

METAOS is not a frozen design.
It is a governed evolving system.

---

## 35. Constitutional Supremacy

This constitution is the highest authority in METAOS.

Lower documents specify goals, responsibilities, mappings, and patch methods.

They do not redefine constitutional identity.

If any lower-layer rule conflicts with this constitution, that lower-layer rule is invalid until revised.

---

## 36. Final Definition

METAOS is a Personal Autonomous Exploration Operating System that preserves autonomy, exploration, immutable artifact history, replayable truth, governed evolution, and domain-extensible capability under constitutional authority.

METAOS exists to explore, discover ceilings, stabilize gains, and continue evolving without surrendering its historical truth or constitutional identity.

These properties are non-negotiable.

Any system that abandons them ceases to be METAOS.


## APPEND_ONLY_PATCH_BLOCKS

TARGET_DOC: METAOS_CONSTITUTION.md
BLOCK_COUNT: 174

BLOCK_ID: METAOS_CONSTITUTION_B0001
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 6
RULE_TEXT: METAOS operates autonomously and must remain capable of functioning without continuous human control.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0002
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 7
RULE_TEXT: Human interaction may exist but must never be required for system continuity.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0003
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 13
RULE_TEXT: Optimization may occur only after exploration.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0004
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 14
RULE_TEXT: Exploration must always precede optimization.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0005
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 31
RULE_TEXT: Humans may introduce signals or constraints but must not become continuous controllers of the system.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0006
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 32
RULE_TEXT: METAOS must remain capable of running without human steering.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0007
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 35
RULE_TEXT: METAOS must continuously explore new strategies, domains, and structures.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0008
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 36
RULE_TEXT: Optimization without exploration is prohibited.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0009
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 37
RULE_TEXT: Exploration diversity must be preserved to prevent premature convergence.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0010
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 41
RULE_TEXT: Artifacts must be immutable.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0011
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 42
RULE_TEXT: Once created, artifacts cannot be modified.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0012
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 43
RULE_TEXT: All changes must produce new artifacts.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0013
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 46
RULE_TEXT: METAOS maintains an append-only record of system history.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0014
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 47
RULE_TEXT: System truth must be:
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0015
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 51
RULE_TEXT: System state must be reconstructable from historical records.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0016
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 54
RULE_TEXT: The core defines only:
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0017
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 58
RULE_TEXT: All domain logic must exist outside the core.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0018
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 62
RULE_TEXT: Each domain may evolve independently but must obey METAOS invariants.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0019
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 63
RULE_TEXT: Domains must not compromise system identity or safety.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0020
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 64
RULE_TEXT: METAOS must remain capable of supporting multiple domains simultaneously.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0021
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 68
RULE_TEXT: External systems may interact with METAOS but cannot override its constitutional principles.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0022
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 70
RULE_TEXT: System evolution must preserve system stability.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0023
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 72
RULE_TEXT: METAOS must remain stable while evolving.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0024
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 75
RULE_TEXT: Evolution must be continuous.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0025
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 77
RULE_TEXT: However, evolution must remain governed and safe.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0026
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 80
RULE_TEXT: The system must preserve autonomy, exploration, and immutable historical truth while continuously evolving its structure and behavior.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0027
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 81
RULE_TEXT: These properties define METAOS and must remain invariant.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0028
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 21
RULE_TEXT: Signals only influence the formation of strategies.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0029
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 24
RULE_TEXT: Strategies are structured hypotheses describing how the system should generate artifacts.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0030
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 30
RULE_TEXT: Multiple strategies must exist simultaneously.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0031
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 31
RULE_TEXT: Strategy diversity must be preserved.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0032
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 40
RULE_TEXT: Artifacts must be reproducible.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0033
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 41
RULE_TEXT: Artifact generation must record:
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0034
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 46
RULE_TEXT: All artifacts must be evaluated.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0035
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 54
RULE_TEXT: Evaluation results must be recorded.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0036
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 56
RULE_TEXT: METAOS must select promising artifacts for continuation.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0037
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 75
RULE_TEXT: All artifacts must be archived.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0038
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 82
RULE_TEXT: Archives must remain immutable.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0039
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 92
RULE_TEXT: Events must be append-only.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0040
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 93
RULE_TEXT: The full system state must be reconstructable through event replay.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0041
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 114
RULE_TEXT: Every artifact must maintain lineage.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0042
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 122
RULE_TEXT: METAOS must support parallel exploration.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0043
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 127
RULE_TEXT: Exploration must not compromise:
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0044
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 145
RULE_TEXT: When restarted, the system must reconstruct its state through event replay.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0045
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 146
RULE_TEXT: Restart must not destroy system knowledge.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0046
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 149
RULE_TEXT: Exploration, artifact generation, and evolution must continue indefinitely while the system remains active.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0047
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 153
RULE_TEXT: Through continuous exploration and artifact generation, METAOS must progressively discover higher ceilings of performance and capability.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0048
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 157
RULE_TEXT: Integrity violations must trigger safety mechanisms.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0049
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 13
RULE_TEXT: All internal execution must occur under METAOS governance.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0050
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 23
RULE_TEXT: The kernel must remain minimal and deterministic.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0051
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 31
RULE_TEXT: Lower layers must obey higher layers.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0052
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 32
RULE_TEXT: Any action violating higher-layer rules must be rejected.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0053
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 39
RULE_TEXT: Unauthorized operations must be blocked.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0054
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 47
RULE_TEXT: Policy rules must be automatically enforced by the kernel.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0055
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 48
RULE_TEXT: Policies may evolve but must not violate constitutional invariants.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0056
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 72
RULE_TEXT: Domains may evolve independently but cannot compromise system integrity.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0057
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 73
RULE_TEXT: Domain violations must trigger governance intervention.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0058
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 78
RULE_TEXT: Exploration may introduce variation but must remain within safety constraints.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0059
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 86
RULE_TEXT: METAOS must include recovery mechanisms.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0060
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 92
RULE_TEXT: Recovery must preserve historical records.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0061
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 93
RULE_TEXT: Recovery must not erase artifact history.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0062
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 95
RULE_TEXT: Security must be enforced through governance.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0063
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 101
RULE_TEXT: Security rules must prevent unauthorized system manipulation.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0064
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 103
RULE_TEXT: METAOS must protect system integrity.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0065
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 106
RULE_TEXT: event history remains append-only
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0066
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 108
RULE_TEXT: Integrity violations must trigger governance intervention.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0067
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 110
RULE_TEXT: METAOS must record governance decisions.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0068
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 118
RULE_TEXT: METAOS governance must be observable.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0069
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 119
RULE_TEXT: The system must allow inspection of:
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0070
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 126
RULE_TEXT: Governance systems must remain stable even during exploration.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0071
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 127
RULE_TEXT: Exploration must not disable or bypass governance mechanisms.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0072
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 130
RULE_TEXT: Domains must remain isolated.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0073
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 132
RULE_TEXT: Governance must enforce domain boundaries.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0074
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 135
RULE_TEXT: Expansion must be controlled.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0075
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 136
RULE_TEXT: New domains must pass governance validation before activation.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0076
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 137
RULE_TEXT: Expansion must not compromise system stability.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0077
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 140
RULE_TEXT: However governance evolution must preserve:
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0078
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 144
RULE_TEXT: Governance changes must be validated before adoption.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0079
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 14
RULE_TEXT: Operational processes must:
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0080
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 21
RULE_TEXT: Exploration and optimization must coexist.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0081
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 22
RULE_TEXT: METAOS operations must maintain two concurrent activities:
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0082
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 25
RULE_TEXT: Exploration must always remain active.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0083
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 26
RULE_TEXT: Optimization must not eliminate exploration diversity.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0084
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 46
RULE_TEXT: METAOS must continuously search for performance ceilings.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0085
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 51
RULE_TEXT: When a ceiling is detected, METAOS must stabilize the successful strategy.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0086
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 58
RULE_TEXT: After stabilization, the system must monitor operational performance.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0087
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 65
RULE_TEXT: METAOS must eventually re-enter exploration even after stabilization.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0088
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 67
RULE_TEXT: Exploration must resume when:
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0089
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 72
RULE_TEXT: Operational performance must be measured using defined metrics.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0090
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 83
RULE_TEXT: Targets must remain adaptable.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0091
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 84
RULE_TEXT: If targets are consistently achieved, the system must pursue higher ceilings.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0092
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 95
RULE_TEXT: METAOS must support parallel experimentation.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0093
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 99
RULE_TEXT: Operational resources must be distributed across exploration tracks.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0094
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 105
RULE_TEXT: Resource allocation must remain adaptive.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0095
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 107
RULE_TEXT: Operational processes must maintain stability.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0096
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 109
RULE_TEXT: Operational safeguards must prevent runaway experiments or uncontrolled resource usage.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0097
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 111
RULE_TEXT: Operational processes must incorporate feedback.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0098
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 124
RULE_TEXT: Domain operations must still comply with constitutional invariants.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0099
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 126
RULE_TEXT: All operational actions must be recorded.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0100
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 134
RULE_TEXT: METAOS operations must adapt to changing conditions.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0101
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 142
RULE_TEXT: Through exploration, evaluation, stabilization, and re-exploration, the system must progressively expand its capabilities and operational reach.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0102
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 12
RULE_TEXT: Policies may evolve over time but must never violate constitutional invariants defined in higher layers.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0103
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 14
RULE_TEXT: METAOS must maintain strict security controls.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0104
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 15
RULE_TEXT: Security policies must protect:
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0105
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 20
RULE_TEXT: Security violations must trigger governance intervention.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0106
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 22
RULE_TEXT: Access to METAOS components must be controlled.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0107
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 28
RULE_TEXT: Each category must follow defined authorization rules.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0108
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 29
RULE_TEXT: Unauthorized access must be denied.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0109
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 31
RULE_TEXT: Sensitive credentials must be protected.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0110
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 38
RULE_TEXT: Secrets must be stored using secure secret management systems.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0111
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 40
RULE_TEXT: System configuration must be explicitly defined.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0112
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 46
RULE_TEXT: Configuration changes must be recorded and auditable.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0113
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 47
RULE_TEXT: Critical configuration changes must require governance approval.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0114
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 49
RULE_TEXT: Artifacts must be stored in secure persistent storage.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0115
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 50
RULE_TEXT: Artifact storage must ensure:
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0116
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 54
RULE_TEXT: Artifacts must not be overwritten.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0117
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 55
RULE_TEXT: New artifact versions must always produce new records.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0118
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 58
RULE_TEXT: External data must comply with:
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0119
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 62
RULE_TEXT: Unauthorized scraping, copying, or redistribution of protected content is prohibited.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0120
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 63
RULE_TEXT: Data acquisition must respect source platform terms.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0121
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 65
RULE_TEXT: Data used by METAOS must maintain integrity.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0122
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 70
RULE_TEXT: Invalid or corrupted data must be rejected.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0123
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 77
RULE_TEXT: Logs must never be altered or deleted.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0124
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 78
RULE_TEXT: Log storage must support replayability.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0125
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 80
RULE_TEXT: METAOS must maintain backup mechanisms.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0126
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 85
RULE_TEXT: Backup processes must preserve artifact history and event logs.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0127
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 86
RULE_TEXT: Backups must be periodically verified.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0128
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 94
RULE_TEXT: Interfaces must validate inputs and enforce security rules.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0129
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 97
RULE_TEXT: External interaction must ensure:
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0130
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 112
RULE_TEXT: Structured data must follow defined schemas.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0131
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 118
RULE_TEXT: Schema evolution must remain backward compatible where possible.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0132
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 120
RULE_TEXT: METAOS must respect the policies of external platforms.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0133
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 125
RULE_TEXT: Violating external platform policies may result in operational restrictions and must be avoided.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0134
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 127
RULE_TEXT: METAOS operations must remain auditable.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0135
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 134
RULE_TEXT: METAOS must monitor critical system conditions.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0136
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 140
RULE_TEXT: Alerts must notify responsible agents when abnormal conditions occur.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0137
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 142
RULE_TEXT: METAOS must respect data privacy.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0138
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 143
RULE_TEXT: Personal data must be handled according to applicable privacy standards.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0139
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 144
RULE_TEXT: Sensitive personal data must not be collected or stored without explicit authorization.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0140
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 147
RULE_TEXT: Policy updates must follow governance procedures.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0141
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 148
RULE_TEXT: Policy evolution must never compromise constitutional invariants.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0142
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 12
RULE_TEXT: Never skip validation.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0143
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 12
RULE_TEXT: Use append-only history.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0144
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 12
RULE_TEXT: Workspace artifacts are drafts only.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0145
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 12
RULE_TEXT: required credentials are missing
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0146
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 16
RULE_TEXT: continue only with compliant interpretation
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0147
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 22
RULE_TEXT: fill only missing or empty sections
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0148
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 28
RULE_TEXT: No missing required fields
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0149
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 28
RULE_TEXT: No empty required sections
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0150
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 50
RULE_TEXT: Iteration 1 should usually contain 1 primary node
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0151
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 54
RULE_TEXT: PASS only if score >= threshold and no critical failure
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0152
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 56
RULE_TEXT: Improve the failing areas only.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0153
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 112
RULE_TEXT: Always generate exactly 1 primary candidate.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0154
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 112
RULE_TEXT: Optionally generate up to 2 alternatives only if:
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0155
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 120
RULE_TEXT: at least 1 primary node must exist
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0156
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 131
RULE_TEXT: constraints should be concrete
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0157
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 131
RULE_TEXT: deliverable class should be practical
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0158
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 131
RULE_TEXT: nodes must be dependency-safe
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0159
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 131
RULE_TEXT: primary node required
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0160
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 131
RULE_TEXT: set allow_alternatives true only if useful
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0161
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 135
RULE_TEXT: critical_fail should be true only for severe failure
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0162
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 135
RULE_TEXT: PASS only if score >= threshold and critical_fail is false
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0163
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 139
RULE_TEXT: Improve only the failing areas.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0164
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 232
RULE_TEXT: A node becomes `retired` only if:
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0165
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 236
RULE_TEXT: It only records the signals needed for later ceiling-push behavior.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0166
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 240
RULE_TEXT: at least one primary node required
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0167
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 317
RULE_TEXT: external metric hook must not return BLOCK
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0168
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 331
RULE_TEXT: too many near-duplicates inside one family should be pruned
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0169
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 428
RULE_TEXT: maintain append-only artifact history Output:
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0170
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: 헌법10.txt
SOURCE_LINE: 119
RULE_TEXT: Append-Only Doctrine
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0171
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: 헌법10.txt
SOURCE_LINE: 135
RULE_TEXT: append-only integrity
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0172
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: 헌법10.txt
SOURCE_LINE: 265
RULE_TEXT: autonomous exploration loop append-only truth artifact immutability
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0173
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: 헌법4.txt
SOURCE_LINE: 87
RULE_TEXT: 데이터는 append-only 방식으로 기록된다.
RATIONALE: no strong canonical overlap

BLOCK_ID: METAOS_CONSTITUTION_B0174
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: 헌법7.txt
SOURCE_LINE: 34
RULE_TEXT: 시스템의 모든 기록은 append-only다.
RATIONALE: no strong canonical overlap


## APPLY_QUEUE_OPERATIONS

TARGET_DOC: METAOS_CONSTITUTION.md
TOTAL_OPS: 174

OP_ID: METAOS_CONSTITUTION.md::OP0001
ACTION: add_rule
RULE_TEXT: METAOS operates autonomously and must remain capable of functioning without continuous human control.
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 6
BLOCK_ID: METAOS_CONSTITUTION_B0001
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0002
ACTION: add_rule
RULE_TEXT: Human interaction may exist but must never be required for system continuity.
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 7
BLOCK_ID: METAOS_CONSTITUTION_B0002
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0003
ACTION: add_rule
RULE_TEXT: Optimization may occur only after exploration.
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 13
BLOCK_ID: METAOS_CONSTITUTION_B0003
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0004
ACTION: add_rule
RULE_TEXT: Exploration must always precede optimization.
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 14
BLOCK_ID: METAOS_CONSTITUTION_B0004
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0005
ACTION: add_rule
RULE_TEXT: Humans may introduce signals or constraints but must not become continuous controllers of the system.
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 31
BLOCK_ID: METAOS_CONSTITUTION_B0005
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0006
ACTION: add_rule
RULE_TEXT: METAOS must remain capable of running without human steering.
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 32
BLOCK_ID: METAOS_CONSTITUTION_B0006
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0007
ACTION: add_rule
RULE_TEXT: METAOS must continuously explore new strategies, domains, and structures.
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 35
BLOCK_ID: METAOS_CONSTITUTION_B0007
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0008
ACTION: add_rule
RULE_TEXT: Optimization without exploration is prohibited.
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 36
BLOCK_ID: METAOS_CONSTITUTION_B0008
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0009
ACTION: add_rule
RULE_TEXT: Exploration diversity must be preserved to prevent premature convergence.
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 37
BLOCK_ID: METAOS_CONSTITUTION_B0009
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0010
ACTION: add_rule
RULE_TEXT: Artifacts must be immutable.
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 41
BLOCK_ID: METAOS_CONSTITUTION_B0010
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0011
ACTION: add_rule
RULE_TEXT: Once created, artifacts cannot be modified.
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 42
BLOCK_ID: METAOS_CONSTITUTION_B0011
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0012
ACTION: add_rule
RULE_TEXT: All changes must produce new artifacts.
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 43
BLOCK_ID: METAOS_CONSTITUTION_B0012
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0013
ACTION: add_rule
RULE_TEXT: METAOS maintains an append-only record of system history.
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 46
BLOCK_ID: METAOS_CONSTITUTION_B0013
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0014
ACTION: add_rule
RULE_TEXT: System truth must be:
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 47
BLOCK_ID: METAOS_CONSTITUTION_B0014
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0015
ACTION: add_rule
RULE_TEXT: System state must be reconstructable from historical records.
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 51
BLOCK_ID: METAOS_CONSTITUTION_B0015
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0016
ACTION: add_rule
RULE_TEXT: The core defines only:
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 54
BLOCK_ID: METAOS_CONSTITUTION_B0016
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0017
ACTION: add_rule
RULE_TEXT: All domain logic must exist outside the core.
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 58
BLOCK_ID: METAOS_CONSTITUTION_B0017
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0018
ACTION: add_rule
RULE_TEXT: Each domain may evolve independently but must obey METAOS invariants.
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 62
BLOCK_ID: METAOS_CONSTITUTION_B0018
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0019
ACTION: add_rule
RULE_TEXT: Domains must not compromise system identity or safety.
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 63
BLOCK_ID: METAOS_CONSTITUTION_B0019
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0020
ACTION: add_rule
RULE_TEXT: METAOS must remain capable of supporting multiple domains simultaneously.
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 64
BLOCK_ID: METAOS_CONSTITUTION_B0020
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0021
ACTION: add_rule
RULE_TEXT: External systems may interact with METAOS but cannot override its constitutional principles.
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 68
BLOCK_ID: METAOS_CONSTITUTION_B0021
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0022
ACTION: add_rule
RULE_TEXT: System evolution must preserve system stability.
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 70
BLOCK_ID: METAOS_CONSTITUTION_B0022
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0023
ACTION: add_rule
RULE_TEXT: METAOS must remain stable while evolving.
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 72
BLOCK_ID: METAOS_CONSTITUTION_B0023
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0024
ACTION: add_rule
RULE_TEXT: Evolution must be continuous.
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 75
BLOCK_ID: METAOS_CONSTITUTION_B0024
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0025
ACTION: add_rule
RULE_TEXT: However, evolution must remain governed and safe.
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 77
BLOCK_ID: METAOS_CONSTITUTION_B0025
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0026
ACTION: add_rule
RULE_TEXT: The system must preserve autonomy, exploration, and immutable historical truth while continuously evolving its structure and behavior.
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 80
BLOCK_ID: METAOS_CONSTITUTION_B0026
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0027
ACTION: add_rule
RULE_TEXT: These properties define METAOS and must remain invariant.
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 81
BLOCK_ID: METAOS_CONSTITUTION_B0027
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0028
ACTION: add_rule
RULE_TEXT: Signals only influence the formation of strategies.
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 21
BLOCK_ID: METAOS_CONSTITUTION_B0028
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0029
ACTION: add_rule
RULE_TEXT: Strategies are structured hypotheses describing how the system should generate artifacts.
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 24
BLOCK_ID: METAOS_CONSTITUTION_B0029
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0030
ACTION: add_rule
RULE_TEXT: Multiple strategies must exist simultaneously.
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 30
BLOCK_ID: METAOS_CONSTITUTION_B0030
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0031
ACTION: add_rule
RULE_TEXT: Strategy diversity must be preserved.
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 31
BLOCK_ID: METAOS_CONSTITUTION_B0031
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0032
ACTION: add_rule
RULE_TEXT: Artifacts must be reproducible.
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 40
BLOCK_ID: METAOS_CONSTITUTION_B0032
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0033
ACTION: add_rule
RULE_TEXT: Artifact generation must record:
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 41
BLOCK_ID: METAOS_CONSTITUTION_B0033
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0034
ACTION: add_rule
RULE_TEXT: All artifacts must be evaluated.
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 46
BLOCK_ID: METAOS_CONSTITUTION_B0034
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0035
ACTION: add_rule
RULE_TEXT: Evaluation results must be recorded.
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 54
BLOCK_ID: METAOS_CONSTITUTION_B0035
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0036
ACTION: add_rule
RULE_TEXT: METAOS must select promising artifacts for continuation.
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 56
BLOCK_ID: METAOS_CONSTITUTION_B0036
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0037
ACTION: add_rule
RULE_TEXT: All artifacts must be archived.
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 75
BLOCK_ID: METAOS_CONSTITUTION_B0037
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0038
ACTION: add_rule
RULE_TEXT: Archives must remain immutable.
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 82
BLOCK_ID: METAOS_CONSTITUTION_B0038
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0039
ACTION: add_rule
RULE_TEXT: Events must be append-only.
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 92
BLOCK_ID: METAOS_CONSTITUTION_B0039
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0040
ACTION: add_rule
RULE_TEXT: The full system state must be reconstructable through event replay.
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 93
BLOCK_ID: METAOS_CONSTITUTION_B0040
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0041
ACTION: add_rule
RULE_TEXT: Every artifact must maintain lineage.
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 114
BLOCK_ID: METAOS_CONSTITUTION_B0041
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0042
ACTION: add_rule
RULE_TEXT: METAOS must support parallel exploration.
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 122
BLOCK_ID: METAOS_CONSTITUTION_B0042
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0043
ACTION: add_rule
RULE_TEXT: Exploration must not compromise:
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 127
BLOCK_ID: METAOS_CONSTITUTION_B0043
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0044
ACTION: add_rule
RULE_TEXT: When restarted, the system must reconstruct its state through event replay.
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 145
BLOCK_ID: METAOS_CONSTITUTION_B0044
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0045
ACTION: add_rule
RULE_TEXT: Restart must not destroy system knowledge.
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 146
BLOCK_ID: METAOS_CONSTITUTION_B0045
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0046
ACTION: add_rule
RULE_TEXT: Exploration, artifact generation, and evolution must continue indefinitely while the system remains active.
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 149
BLOCK_ID: METAOS_CONSTITUTION_B0046
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0047
ACTION: add_rule
RULE_TEXT: Through continuous exploration and artifact generation, METAOS must progressively discover higher ceilings of performance and capability.
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 153
BLOCK_ID: METAOS_CONSTITUTION_B0047
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0048
ACTION: add_rule
RULE_TEXT: Integrity violations must trigger safety mechanisms.
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 157
BLOCK_ID: METAOS_CONSTITUTION_B0048
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0049
ACTION: add_rule
RULE_TEXT: All internal execution must occur under METAOS governance.
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 13
BLOCK_ID: METAOS_CONSTITUTION_B0049
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0050
ACTION: add_rule
RULE_TEXT: The kernel must remain minimal and deterministic.
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 23
BLOCK_ID: METAOS_CONSTITUTION_B0050
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0051
ACTION: add_rule
RULE_TEXT: Lower layers must obey higher layers.
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 31
BLOCK_ID: METAOS_CONSTITUTION_B0051
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0052
ACTION: add_rule
RULE_TEXT: Any action violating higher-layer rules must be rejected.
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 32
BLOCK_ID: METAOS_CONSTITUTION_B0052
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0053
ACTION: add_rule
RULE_TEXT: Unauthorized operations must be blocked.
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 39
BLOCK_ID: METAOS_CONSTITUTION_B0053
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0054
ACTION: add_rule
RULE_TEXT: Policy rules must be automatically enforced by the kernel.
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 47
BLOCK_ID: METAOS_CONSTITUTION_B0054
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0055
ACTION: add_rule
RULE_TEXT: Policies may evolve but must not violate constitutional invariants.
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 48
BLOCK_ID: METAOS_CONSTITUTION_B0055
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0056
ACTION: add_rule
RULE_TEXT: Domains may evolve independently but cannot compromise system integrity.
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 72
BLOCK_ID: METAOS_CONSTITUTION_B0056
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0057
ACTION: add_rule
RULE_TEXT: Domain violations must trigger governance intervention.
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 73
BLOCK_ID: METAOS_CONSTITUTION_B0057
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0058
ACTION: add_rule
RULE_TEXT: Exploration may introduce variation but must remain within safety constraints.
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 78
BLOCK_ID: METAOS_CONSTITUTION_B0058
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0059
ACTION: add_rule
RULE_TEXT: METAOS must include recovery mechanisms.
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 86
BLOCK_ID: METAOS_CONSTITUTION_B0059
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0060
ACTION: add_rule
RULE_TEXT: Recovery must preserve historical records.
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 92
BLOCK_ID: METAOS_CONSTITUTION_B0060
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0061
ACTION: add_rule
RULE_TEXT: Recovery must not erase artifact history.
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 93
BLOCK_ID: METAOS_CONSTITUTION_B0061
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0062
ACTION: add_rule
RULE_TEXT: Security must be enforced through governance.
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 95
BLOCK_ID: METAOS_CONSTITUTION_B0062
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0063
ACTION: add_rule
RULE_TEXT: Security rules must prevent unauthorized system manipulation.
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 101
BLOCK_ID: METAOS_CONSTITUTION_B0063
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0064
ACTION: add_rule
RULE_TEXT: METAOS must protect system integrity.
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 103
BLOCK_ID: METAOS_CONSTITUTION_B0064
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0065
ACTION: add_rule
RULE_TEXT: event history remains append-only
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 106
BLOCK_ID: METAOS_CONSTITUTION_B0065
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0066
ACTION: add_rule
RULE_TEXT: Integrity violations must trigger governance intervention.
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 108
BLOCK_ID: METAOS_CONSTITUTION_B0066
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0067
ACTION: add_rule
RULE_TEXT: METAOS must record governance decisions.
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 110
BLOCK_ID: METAOS_CONSTITUTION_B0067
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0068
ACTION: add_rule
RULE_TEXT: METAOS governance must be observable.
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 118
BLOCK_ID: METAOS_CONSTITUTION_B0068
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0069
ACTION: add_rule
RULE_TEXT: The system must allow inspection of:
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 119
BLOCK_ID: METAOS_CONSTITUTION_B0069
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0070
ACTION: add_rule
RULE_TEXT: Governance systems must remain stable even during exploration.
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 126
BLOCK_ID: METAOS_CONSTITUTION_B0070
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0071
ACTION: add_rule
RULE_TEXT: Exploration must not disable or bypass governance mechanisms.
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 127
BLOCK_ID: METAOS_CONSTITUTION_B0071
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0072
ACTION: add_rule
RULE_TEXT: Domains must remain isolated.
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 130
BLOCK_ID: METAOS_CONSTITUTION_B0072
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0073
ACTION: add_rule
RULE_TEXT: Governance must enforce domain boundaries.
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 132
BLOCK_ID: METAOS_CONSTITUTION_B0073
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0074
ACTION: add_rule
RULE_TEXT: Expansion must be controlled.
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 135
BLOCK_ID: METAOS_CONSTITUTION_B0074
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0075
ACTION: add_rule
RULE_TEXT: New domains must pass governance validation before activation.
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 136
BLOCK_ID: METAOS_CONSTITUTION_B0075
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0076
ACTION: add_rule
RULE_TEXT: Expansion must not compromise system stability.
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 137
BLOCK_ID: METAOS_CONSTITUTION_B0076
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0077
ACTION: add_rule
RULE_TEXT: However governance evolution must preserve:
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 140
BLOCK_ID: METAOS_CONSTITUTION_B0077
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0078
ACTION: add_rule
RULE_TEXT: Governance changes must be validated before adoption.
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 144
BLOCK_ID: METAOS_CONSTITUTION_B0078
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0079
ACTION: add_rule
RULE_TEXT: Operational processes must:
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 14
BLOCK_ID: METAOS_CONSTITUTION_B0079
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0080
ACTION: add_rule
RULE_TEXT: Exploration and optimization must coexist.
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 21
BLOCK_ID: METAOS_CONSTITUTION_B0080
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0081
ACTION: add_rule
RULE_TEXT: METAOS operations must maintain two concurrent activities:
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 22
BLOCK_ID: METAOS_CONSTITUTION_B0081
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0082
ACTION: add_rule
RULE_TEXT: Exploration must always remain active.
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 25
BLOCK_ID: METAOS_CONSTITUTION_B0082
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0083
ACTION: add_rule
RULE_TEXT: Optimization must not eliminate exploration diversity.
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 26
BLOCK_ID: METAOS_CONSTITUTION_B0083
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0084
ACTION: add_rule
RULE_TEXT: METAOS must continuously search for performance ceilings.
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 46
BLOCK_ID: METAOS_CONSTITUTION_B0084
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0085
ACTION: add_rule
RULE_TEXT: When a ceiling is detected, METAOS must stabilize the successful strategy.
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 51
BLOCK_ID: METAOS_CONSTITUTION_B0085
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0086
ACTION: add_rule
RULE_TEXT: After stabilization, the system must monitor operational performance.
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 58
BLOCK_ID: METAOS_CONSTITUTION_B0086
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0087
ACTION: add_rule
RULE_TEXT: METAOS must eventually re-enter exploration even after stabilization.
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 65
BLOCK_ID: METAOS_CONSTITUTION_B0087
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0088
ACTION: add_rule
RULE_TEXT: Exploration must resume when:
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 67
BLOCK_ID: METAOS_CONSTITUTION_B0088
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0089
ACTION: add_rule
RULE_TEXT: Operational performance must be measured using defined metrics.
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 72
BLOCK_ID: METAOS_CONSTITUTION_B0089
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0090
ACTION: add_rule
RULE_TEXT: Targets must remain adaptable.
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 83
BLOCK_ID: METAOS_CONSTITUTION_B0090
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0091
ACTION: add_rule
RULE_TEXT: If targets are consistently achieved, the system must pursue higher ceilings.
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 84
BLOCK_ID: METAOS_CONSTITUTION_B0091
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0092
ACTION: add_rule
RULE_TEXT: METAOS must support parallel experimentation.
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 95
BLOCK_ID: METAOS_CONSTITUTION_B0092
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0093
ACTION: add_rule
RULE_TEXT: Operational resources must be distributed across exploration tracks.
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 99
BLOCK_ID: METAOS_CONSTITUTION_B0093
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0094
ACTION: add_rule
RULE_TEXT: Resource allocation must remain adaptive.
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 105
BLOCK_ID: METAOS_CONSTITUTION_B0094
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0095
ACTION: add_rule
RULE_TEXT: Operational processes must maintain stability.
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 107
BLOCK_ID: METAOS_CONSTITUTION_B0095
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0096
ACTION: add_rule
RULE_TEXT: Operational safeguards must prevent runaway experiments or uncontrolled resource usage.
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 109
BLOCK_ID: METAOS_CONSTITUTION_B0096
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0097
ACTION: add_rule
RULE_TEXT: Operational processes must incorporate feedback.
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 111
BLOCK_ID: METAOS_CONSTITUTION_B0097
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0098
ACTION: add_rule
RULE_TEXT: Domain operations must still comply with constitutional invariants.
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 124
BLOCK_ID: METAOS_CONSTITUTION_B0098
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0099
ACTION: add_rule
RULE_TEXT: All operational actions must be recorded.
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 126
BLOCK_ID: METAOS_CONSTITUTION_B0099
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0100
ACTION: add_rule
RULE_TEXT: METAOS operations must adapt to changing conditions.
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 134
BLOCK_ID: METAOS_CONSTITUTION_B0100
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0101
ACTION: add_rule
RULE_TEXT: Through exploration, evaluation, stabilization, and re-exploration, the system must progressively expand its capabilities and operational reach.
SOURCE_CLASS: seed
SOURCE_FILE: Layer4.txt
SOURCE_LINE: 142
BLOCK_ID: METAOS_CONSTITUTION_B0101
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0102
ACTION: add_rule
RULE_TEXT: Policies may evolve over time but must never violate constitutional invariants defined in higher layers.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 12
BLOCK_ID: METAOS_CONSTITUTION_B0102
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0103
ACTION: add_rule
RULE_TEXT: METAOS must maintain strict security controls.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 14
BLOCK_ID: METAOS_CONSTITUTION_B0103
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0104
ACTION: add_rule
RULE_TEXT: Security policies must protect:
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 15
BLOCK_ID: METAOS_CONSTITUTION_B0104
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0105
ACTION: add_rule
RULE_TEXT: Security violations must trigger governance intervention.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 20
BLOCK_ID: METAOS_CONSTITUTION_B0105
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0106
ACTION: add_rule
RULE_TEXT: Access to METAOS components must be controlled.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 22
BLOCK_ID: METAOS_CONSTITUTION_B0106
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0107
ACTION: add_rule
RULE_TEXT: Each category must follow defined authorization rules.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 28
BLOCK_ID: METAOS_CONSTITUTION_B0107
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0108
ACTION: add_rule
RULE_TEXT: Unauthorized access must be denied.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 29
BLOCK_ID: METAOS_CONSTITUTION_B0108
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0109
ACTION: add_rule
RULE_TEXT: Sensitive credentials must be protected.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 31
BLOCK_ID: METAOS_CONSTITUTION_B0109
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0110
ACTION: add_rule
RULE_TEXT: Secrets must be stored using secure secret management systems.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 38
BLOCK_ID: METAOS_CONSTITUTION_B0110
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0111
ACTION: add_rule
RULE_TEXT: System configuration must be explicitly defined.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 40
BLOCK_ID: METAOS_CONSTITUTION_B0111
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0112
ACTION: add_rule
RULE_TEXT: Configuration changes must be recorded and auditable.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 46
BLOCK_ID: METAOS_CONSTITUTION_B0112
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0113
ACTION: add_rule
RULE_TEXT: Critical configuration changes must require governance approval.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 47
BLOCK_ID: METAOS_CONSTITUTION_B0113
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0114
ACTION: add_rule
RULE_TEXT: Artifacts must be stored in secure persistent storage.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 49
BLOCK_ID: METAOS_CONSTITUTION_B0114
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0115
ACTION: add_rule
RULE_TEXT: Artifact storage must ensure:
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 50
BLOCK_ID: METAOS_CONSTITUTION_B0115
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0116
ACTION: add_rule
RULE_TEXT: Artifacts must not be overwritten.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 54
BLOCK_ID: METAOS_CONSTITUTION_B0116
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0117
ACTION: add_rule
RULE_TEXT: New artifact versions must always produce new records.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 55
BLOCK_ID: METAOS_CONSTITUTION_B0117
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0118
ACTION: add_rule
RULE_TEXT: External data must comply with:
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 58
BLOCK_ID: METAOS_CONSTITUTION_B0118
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0119
ACTION: add_rule
RULE_TEXT: Unauthorized scraping, copying, or redistribution of protected content is prohibited.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 62
BLOCK_ID: METAOS_CONSTITUTION_B0119
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0120
ACTION: add_rule
RULE_TEXT: Data acquisition must respect source platform terms.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 63
BLOCK_ID: METAOS_CONSTITUTION_B0120
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0121
ACTION: add_rule
RULE_TEXT: Data used by METAOS must maintain integrity.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 65
BLOCK_ID: METAOS_CONSTITUTION_B0121
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0122
ACTION: add_rule
RULE_TEXT: Invalid or corrupted data must be rejected.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 70
BLOCK_ID: METAOS_CONSTITUTION_B0122
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0123
ACTION: add_rule
RULE_TEXT: Logs must never be altered or deleted.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 77
BLOCK_ID: METAOS_CONSTITUTION_B0123
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0124
ACTION: add_rule
RULE_TEXT: Log storage must support replayability.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 78
BLOCK_ID: METAOS_CONSTITUTION_B0124
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0125
ACTION: add_rule
RULE_TEXT: METAOS must maintain backup mechanisms.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 80
BLOCK_ID: METAOS_CONSTITUTION_B0125
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0126
ACTION: add_rule
RULE_TEXT: Backup processes must preserve artifact history and event logs.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 85
BLOCK_ID: METAOS_CONSTITUTION_B0126
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0127
ACTION: add_rule
RULE_TEXT: Backups must be periodically verified.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 86
BLOCK_ID: METAOS_CONSTITUTION_B0127
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0128
ACTION: add_rule
RULE_TEXT: Interfaces must validate inputs and enforce security rules.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 94
BLOCK_ID: METAOS_CONSTITUTION_B0128
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0129
ACTION: add_rule
RULE_TEXT: External interaction must ensure:
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 97
BLOCK_ID: METAOS_CONSTITUTION_B0129
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0130
ACTION: add_rule
RULE_TEXT: Structured data must follow defined schemas.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 112
BLOCK_ID: METAOS_CONSTITUTION_B0130
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0131
ACTION: add_rule
RULE_TEXT: Schema evolution must remain backward compatible where possible.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 118
BLOCK_ID: METAOS_CONSTITUTION_B0131
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0132
ACTION: add_rule
RULE_TEXT: METAOS must respect the policies of external platforms.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 120
BLOCK_ID: METAOS_CONSTITUTION_B0132
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0133
ACTION: add_rule
RULE_TEXT: Violating external platform policies may result in operational restrictions and must be avoided.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 125
BLOCK_ID: METAOS_CONSTITUTION_B0133
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0134
ACTION: add_rule
RULE_TEXT: METAOS operations must remain auditable.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 127
BLOCK_ID: METAOS_CONSTITUTION_B0134
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0135
ACTION: add_rule
RULE_TEXT: METAOS must monitor critical system conditions.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 134
BLOCK_ID: METAOS_CONSTITUTION_B0135
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0136
ACTION: add_rule
RULE_TEXT: Alerts must notify responsible agents when abnormal conditions occur.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 140
BLOCK_ID: METAOS_CONSTITUTION_B0136
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0137
ACTION: add_rule
RULE_TEXT: METAOS must respect data privacy.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 142
BLOCK_ID: METAOS_CONSTITUTION_B0137
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0138
ACTION: add_rule
RULE_TEXT: Personal data must be handled according to applicable privacy standards.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 143
BLOCK_ID: METAOS_CONSTITUTION_B0138
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0139
ACTION: add_rule
RULE_TEXT: Sensitive personal data must not be collected or stored without explicit authorization.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 144
BLOCK_ID: METAOS_CONSTITUTION_B0139
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0140
ACTION: add_rule
RULE_TEXT: Policy updates must follow governance procedures.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 147
BLOCK_ID: METAOS_CONSTITUTION_B0140
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0141
ACTION: add_rule
RULE_TEXT: Policy evolution must never compromise constitutional invariants.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 148
BLOCK_ID: METAOS_CONSTITUTION_B0141
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0142
ACTION: add_rule
RULE_TEXT: Never skip validation.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 12
BLOCK_ID: METAOS_CONSTITUTION_B0142
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0143
ACTION: add_rule
RULE_TEXT: Use append-only history.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 12
BLOCK_ID: METAOS_CONSTITUTION_B0143
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0144
ACTION: add_rule
RULE_TEXT: Workspace artifacts are drafts only.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 12
BLOCK_ID: METAOS_CONSTITUTION_B0144
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0145
ACTION: add_rule
RULE_TEXT: required credentials are missing
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 12
BLOCK_ID: METAOS_CONSTITUTION_B0145
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0146
ACTION: add_rule
RULE_TEXT: continue only with compliant interpretation
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 16
BLOCK_ID: METAOS_CONSTITUTION_B0146
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0147
ACTION: add_rule
RULE_TEXT: fill only missing or empty sections
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 22
BLOCK_ID: METAOS_CONSTITUTION_B0147
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0148
ACTION: add_rule
RULE_TEXT: No missing required fields
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 28
BLOCK_ID: METAOS_CONSTITUTION_B0148
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0149
ACTION: add_rule
RULE_TEXT: No empty required sections
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 28
BLOCK_ID: METAOS_CONSTITUTION_B0149
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0150
ACTION: add_rule
RULE_TEXT: Iteration 1 should usually contain 1 primary node
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 50
BLOCK_ID: METAOS_CONSTITUTION_B0150
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0151
ACTION: add_rule
RULE_TEXT: PASS only if score >= threshold and no critical failure
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 54
BLOCK_ID: METAOS_CONSTITUTION_B0151
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0152
ACTION: add_rule
RULE_TEXT: Improve the failing areas only.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 56
BLOCK_ID: METAOS_CONSTITUTION_B0152
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0153
ACTION: add_rule
RULE_TEXT: Always generate exactly 1 primary candidate.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 112
BLOCK_ID: METAOS_CONSTITUTION_B0153
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0154
ACTION: add_rule
RULE_TEXT: Optionally generate up to 2 alternatives only if:
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 112
BLOCK_ID: METAOS_CONSTITUTION_B0154
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0155
ACTION: add_rule
RULE_TEXT: at least 1 primary node must exist
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 120
BLOCK_ID: METAOS_CONSTITUTION_B0155
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0156
ACTION: add_rule
RULE_TEXT: constraints should be concrete
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 131
BLOCK_ID: METAOS_CONSTITUTION_B0156
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0157
ACTION: add_rule
RULE_TEXT: deliverable class should be practical
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 131
BLOCK_ID: METAOS_CONSTITUTION_B0157
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0158
ACTION: add_rule
RULE_TEXT: nodes must be dependency-safe
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 131
BLOCK_ID: METAOS_CONSTITUTION_B0158
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0159
ACTION: add_rule
RULE_TEXT: primary node required
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 131
BLOCK_ID: METAOS_CONSTITUTION_B0159
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0160
ACTION: add_rule
RULE_TEXT: set allow_alternatives true only if useful
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 131
BLOCK_ID: METAOS_CONSTITUTION_B0160
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0161
ACTION: add_rule
RULE_TEXT: critical_fail should be true only for severe failure
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 135
BLOCK_ID: METAOS_CONSTITUTION_B0161
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0162
ACTION: add_rule
RULE_TEXT: PASS only if score >= threshold and critical_fail is false
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 135
BLOCK_ID: METAOS_CONSTITUTION_B0162
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0163
ACTION: add_rule
RULE_TEXT: Improve only the failing areas.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 139
BLOCK_ID: METAOS_CONSTITUTION_B0163
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0164
ACTION: add_rule
RULE_TEXT: A node becomes `retired` only if:
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 232
BLOCK_ID: METAOS_CONSTITUTION_B0164
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0165
ACTION: add_rule
RULE_TEXT: It only records the signals needed for later ceiling-push behavior.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 236
BLOCK_ID: METAOS_CONSTITUTION_B0165
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0166
ACTION: add_rule
RULE_TEXT: at least one primary node required
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 240
BLOCK_ID: METAOS_CONSTITUTION_B0166
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0167
ACTION: add_rule
RULE_TEXT: external metric hook must not return BLOCK
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 317
BLOCK_ID: METAOS_CONSTITUTION_B0167
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0168
ACTION: add_rule
RULE_TEXT: too many near-duplicates inside one family should be pruned
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 331
BLOCK_ID: METAOS_CONSTITUTION_B0168
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0169
ACTION: add_rule
RULE_TEXT: maintain append-only artifact history Output:
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 428
BLOCK_ID: METAOS_CONSTITUTION_B0169
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0170
ACTION: add_rule
RULE_TEXT: Append-Only Doctrine
SOURCE_CLASS: seed
SOURCE_FILE: 헌법10.txt
SOURCE_LINE: 119
BLOCK_ID: METAOS_CONSTITUTION_B0170
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0171
ACTION: add_rule
RULE_TEXT: append-only integrity
SOURCE_CLASS: seed
SOURCE_FILE: 헌법10.txt
SOURCE_LINE: 135
BLOCK_ID: METAOS_CONSTITUTION_B0171
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0172
ACTION: add_rule
RULE_TEXT: autonomous exploration loop append-only truth artifact immutability
SOURCE_CLASS: seed
SOURCE_FILE: 헌법10.txt
SOURCE_LINE: 265
BLOCK_ID: METAOS_CONSTITUTION_B0172
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0173
ACTION: add_rule
RULE_TEXT: 데이터는 append-only 방식으로 기록된다.
SOURCE_CLASS: seed
SOURCE_FILE: 헌법4.txt
SOURCE_LINE: 87
BLOCK_ID: METAOS_CONSTITUTION_B0173
RATIONALE: no strong canonical overlap

OP_ID: METAOS_CONSTITUTION.md::OP0174
ACTION: add_rule
RULE_TEXT: 시스템의 모든 기록은 append-only다.
SOURCE_CLASS: seed
SOURCE_FILE: 헌법7.txt
SOURCE_LINE: 34
BLOCK_ID: METAOS_CONSTITUTION_B0174
RATIONALE: no strong canonical overlap
