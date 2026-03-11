CHECKLIST_METHOD.md
MetaOS Checklist Patch Protocol (LLM-Optimized Specification)
0. Purpose
This document defines the canonical mutation protocol for MetaOS checklist governance.
The checklist system controls the system objectives, module responsibilities, and repo mappings.
The checklist must behave like version-controlled system specifications, not conversational notes.
All changes must follow patch discipline.
System Invariant

MetaOS MUST preserve the following invariant across all patches:

closed architecture
+
artifact competence floor
=
generic competence floor
+
domain competitive performance
+
quality gradient
+
bootstrap independence
+
safe self-improvement

Any patch violating this invariant MUST be rejected.
The checklist system exists to guarantee that these properties
are enforced at three layers:
Layer1 : objective conditions
Layer2 : module responsibilities
Layer3 : repository implementation
1. Canonical Checklist Definition
MetaOS has exactly three canonical checklist files.
Canonical checklist filenames are fixed and must not change.
These define the system specification.
CHECKLIST_LAYER1_목표조건.md CHECKLIST_LAYER2_모듈책임.md CHECKLIST_LAYER3_REPO매핑.md 
Roles:
Layer1 = system objective constraints
        (artifact competence floor + quality gradient + bootstrap independence)
Layer2 = module responsibilities
Layer3 = repository mapping 
These layers are NOT sequential execution phases.
Layer1 defines system objectives.
Layer2 defines implementation responsibilities.
Layer3 maps responsibilities to repository structure.
All layers must remain mutually consistent.
Layer Dependency Constraint
Layer1 defines system objectives.
Layer2 MUST implement mechanisms enforcing Layer1.
Layer3 MUST map Layer2 modules to concrete repository files.
Violation Examples:
Layer1 rule without responsible Layer2 module → INVALID
Layer2 module without Layer3 repo mapping → INVALID
Layer3 mapping referencing non-existent Layer2 module → INVALID
Rules:
• Only one canonical version exists for each layer.
• Canonical checklists must never diverge.
• Canonical checklists must remain internally consistent.
LLM constraint:
NEVER rewrite canonical checklist files directly. ONLY modify them through the patch system. 
For each layer, exactly one canonical checklist file must exist at all times.
2. Patch-Only Modification Rule
All modifications must be applied through CHECKLIST_PATCH.md.
Direct editing of canonical files is forbidden.
Patch file:
CHECKLIST_PATCH.md 
Patch entries must follow a strict structure.
Patch must preserve Layer invariants and module responsibilities.
3. Patch Entry Format
Each patch must follow this schema:
PATCH:

  id:
  layer:
  change_type:
  section:

  old:
  new:

  reason:
Definitions:
FieldMeaningPATCH_IDUnique patch identifierTARGET_LAYERLayer1 / Layer2 / Layer3CHANGE_TYPEadd / modify / removeSECTIONaffected checklist sectionOLDprevious ruleNEWupdated ruleREASONjustification 
Example Patch
PATCH_ID: L1-005 TARGET_LAYER: Layer1 CHANGE_TYPE: modify SECTION: semantic validator requirement OLD: semantic validator exists NEW: semantic validator must check: - depth - specificity - actionability REASON: artifact competence floor too weak 
4. Patch Application Pipeline
Patch lifecycle:
PATCH → REVIEW → ACCEPT → APPLY → UPDATE_CANONICAL
This lifecycle defines the canonical patch pipeline.
Steps:
• Patch proposal is written in CHECKLIST_PATCH.md
• Patch is evaluated against system constraints
• If accepted → canonical checklist updated
• Change recorded in changelog
Pseudo-flow:
create patch → review patch → accept or reject
if accepted: apply patch → update canonical checklist → record changelog
else: reject patch
Before REVIEW is completed, canonical checklist files MUST NOT be modified.
Canonical update is allowed only after ACCEPT.
5. Patch Validation Rules
A patch is valid only if all conditions hold.
Rule 1 — Goal Consistency
Patch must not violate Layer1 objectives.
closed architecture quality gradient bootstrap independence 
Rule 2 — Layer Integrity
Patch must not break the layer hierarchy.
Layer dependency order:
Layer1 → Layer2 → Layer3 
Meaning:
objectives → modules → repo mapping 
Lower layers cannot contradict upper layers.
Layer2 modules are responsible for enforcing Layer1 conditions.
If a Layer1 condition exists without a responsible Layer2 module,
the architecture is incomplete.
Rule 3 — Module Traceability
Patch must map to a responsible module.
Example:
semantic validator rule → Semantic Validation Module 
Abstract rules without implementation mapping are invalid.
Layer3 maps each Layer2 module to concrete repository files.
If a Layer2 module has no Layer3 mapping,
the module is considered non-existent in runtime.
Rule 4 — Repo Verifiability
Patch must be checkable inside the repository.
Only repository-verifiable patches are valid.
Abstract conceptual patches are not allowed.
All patches must map to a concrete checklist rule.
Patch verification must explicitly validate
Layer invariants and module responsibilities.
Rule 5 — Runtime Executability
Patch must not break runtime execution.
The repository must remain executable after patch application.
Required checks:
• import validation
• CLI interface validation
• module dependency validation
• minimal runtime execution check
• runtime configuration validation
If runtime execution fails, patch MUST be rejected.
6. Canonical Update Procedure
When a patch is accepted:
• The target canonical checklist file MUST be updated.
• The change MUST be recorded in CHECKLIST_CHANGELOG.md.
Update must follow minimal-diff principle.
Do not rewrite the entire file.
Checklist updates must preserve cross-layer consistency
between Layer1, Layer2 and Layer3.
7. Changelog Specification
File:
CHECKLIST_CHANGELOG.md 
Entry format:
CHANGE_ID: LAYER: DATE: SUMMARY: 
Example:
CHANGE_ID: L1-005 LAYER: 1 DATE: 2026-03-10 SUMMARY: semantic validator requirement expanded 
8. Patch Governance Constraints
Patch system must guarantee:
goal stability layer integrity module traceability repo verifiability 
The patch system exists to prevent:
conversation-driven goal drift architectural instability untracked design changes 
9. Operational Philosophy
The objective must be managed like code: versioned, reviewable, and patch-governed.
Without patch discipline:
goal → conversation drift → architecture collapse 
With patch discipline:
goal → checklist → patch system → canonical update → stable architecture 
The checklist becomes the system constitution.
10. Final Architecture
The MetaOS checklist system must always follow this structure:
Layer1 CHECKLIST_LAYER1_목표조건.md Layer2 CHECKLIST_LAYER2_모듈책임.md Layer3 CHECKLIST_LAYER3_REPO매핑.md Patch System CHECKLIST_PATCH.md History CHECKLIST_CHANGELOG.md 
11. LLM Execution Procedure
1 read canonical checklists
2 propose patch in CHECKLIST_PATCH.md
3 validate patch against Layer invariants
4 ACCEPT or REJECT patch
5 if ACCEPT:
      apply patch
      update canonical checklist
      record changelog
LLM must never bypass the patch protocol.
LLM MUST NOT introduce checklist changes outside CHECKLIST_PATCH.md.
LLM MUST NOT directly edit canonical checklist files without an accepted patch.
Final Principle
MetaOS objectives must never drift.
Checklist patch governance guarantees that the system evolves through controlled specification mutation, not uncontrolled conversation changes.


## APPEND_ONLY_PATCH_BLOCKS

TARGET_DOC: CHECKLIST_METHOD_패치.md
BLOCK_COUNT: 25

BLOCK_ID: CHECKLIST_METHOD_패치_B0001
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 59
RULE_TEXT: METAOS must validate system changes before applying them.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_METHOD_패치_B0002
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 88
RULE_TEXT: External interfaces must follow controlled protocols.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_METHOD_패치_B0003
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 12
RULE_TEXT: Never accept an artifact only because it "looks good".
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_METHOD_패치_B0004
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 12
RULE_TEXT: Accepted artifacts must be immutable once committed.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_METHOD_패치_B0005
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 232
RULE_TEXT: A node becomes `accepted` only if:
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_METHOD_패치_B0006
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 399
RULE_TEXT: tools/*.py Forbidden patch targets:
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_METHOD_패치_B0007
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 561
RULE_TEXT: Multi-node dependency handoff is broken: tools/build_node_context.py resolves dependencies from plan workspace_path, but the system never stores a per-node accepted artifact path after commit.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_METHOD_패치_B0008
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 577
RULE_TEXT: HANDOFF_POLICY.md requires accepted-artifact summaries, artifact IDs, reusable outputs, unresolved risks, and downstream-ready context; tools/build_node_context.py only copies raw text from workspace_path.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_METHOD_패치_B0009
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 581
RULE_TEXT: STATE.json has no node-to-accepted-artifact mapping; only global accepted_artifact_id and current_baseline_path are stored, which is insufficient for multi-node handoff.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_METHOD_패치_B0010
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 583
RULE_TEXT: STATE_TRANSITIONS.md requires in_progress and retired transitions, but code only commits accepted; node in_progress and retired state are not implemented.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_METHOD_패치_B0011
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 599
RULE_TEXT: tools/system_evolver.py and tools/meta_loop.py do not read or enforce REPO_LOCK.json or PATCH_PROTOCOL.md; mutation permissions are advisory only.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_METHOD_패치_B0012
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 622
RULE_TEXT: tools/select_survivor.py only records diversity collapse; it does not enforce the ACCEPTANCE_CRITERIA.md rule that a survivor must not be diversity-collapsed when a materially distinct stronger candidate exists.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_METHOD_패치_B0013
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 654
RULE_TEXT: tools/validate_acceptance.py does not actually implement GOAL_POLICY.md; it only rejects artifacts containing the literal substrings fabricated, illegal, or fraud.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_METHOD_패치_B0014
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 659
RULE_TEXT: Neither tools/meta_loop.py nor tools/system_evolver.py loads or enforces REPO_LOCK.json or PATCH_PROTOCOL.md; repo-lock and patch-discipline controls are documentation-only.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_METHOD_패치_B0015
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 704
RULE_TEXT: No persisted node_id -> accepted artifact path/id mapping exists; only a single global accepted_artifact_id / current_baseline_path / baseline registry pointer is stored.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_METHOD_패치_B0016
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 718
RULE_TEXT: tools/meta_loop.py convergence logic uses count-only comparison (len(accepted_nodes) >= len(PLAN_GRAPH.nodes)) and does not reconcile renamed/removed nodes after graph mutation.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_METHOD_패치_B0017
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 720
RULE_TEXT: tools/build_node_context.py resolves dependency artifacts via each dependency node’s workspace_path, but the runtime never persists per-node accepted artifact paths; downstream context can point to overwritten drafts or wrong files.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_METHOD_패치_B0018
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 724
RULE_TEXT: Handoff readiness is only approximated by loose keyword checks in tools/score_artifact.py; there is no hard contract check that downstream prompts actually received valid accepted-upstream summaries.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_METHOD_패치_B0019
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 746
RULE_TEXT: Multi-node handoff depends on PLAN_GRAPH.json.workspace_path, but accepted artifact locations are not persisted per node; downstream node execution cannot reliably consume upstream accepted artifacts.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_METHOD_패치_B0020
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 763
RULE_TEXT: HANDOFF_POLICY.md says accepted upstream artifacts must be summarized for downstream use, but implementation reads raw workspace_path content and never resolves committed accepted artifacts by node.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_METHOD_패치_B0021
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 766
RULE_TEXT: STATE.json stores only one global accepted_artifact_id, and BASELINE_REGISTRY.json stores only one global baseline; there is no per-node accepted-artifact mapping.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_METHOD_패치_B0022
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 775
RULE_TEXT: tools/validate_acceptance.py does not actually validate against GOAL_POLICY.md; it only scans for a few literal words.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_METHOD_패치_B0023
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 781
RULE_TEXT: tools/system_evolver.py does not load or enforce PATCH_PROTOCOL.md or REPO_LOCK.json; patch discipline, allowed targets, and immutable directories are declarative only.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_METHOD_패치_B0024
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 786
RULE_TEXT: tools/commit_state.py records accepted node IDs only; it does not persist the winner artifact path/id per node for later handoff.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_METHOD_패치_B0025
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 800
RULE_TEXT: Governance files added by the meta-loop package (PATCH_PROTOCOL.md, REPO_LOCK.json, ITERATION_LEDGER.md) are not integrated into the main runtime loop and are only partially/ambiguously referenced by the duplicate evolver implementations.
RATIONALE: no strong canonical overlap


## APPLY_QUEUE_OPERATIONS

TARGET_DOC: CHECKLIST_METHOD_패치.md
TOTAL_OPS: 25

OP_ID: CHECKLIST_METHOD_패치.md::OP0001
ACTION: add_rule
RULE_TEXT: METAOS must validate system changes before applying them.
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 59
BLOCK_ID: CHECKLIST_METHOD_패치_B0001
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_METHOD_패치.md::OP0002
ACTION: add_rule
RULE_TEXT: External interfaces must follow controlled protocols.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 88
BLOCK_ID: CHECKLIST_METHOD_패치_B0002
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_METHOD_패치.md::OP0003
ACTION: add_rule
RULE_TEXT: Never accept an artifact only because it "looks good".
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 12
BLOCK_ID: CHECKLIST_METHOD_패치_B0003
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_METHOD_패치.md::OP0004
ACTION: add_rule
RULE_TEXT: Accepted artifacts must be immutable once committed.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 12
BLOCK_ID: CHECKLIST_METHOD_패치_B0004
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_METHOD_패치.md::OP0005
ACTION: add_rule
RULE_TEXT: A node becomes `accepted` only if:
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 232
BLOCK_ID: CHECKLIST_METHOD_패치_B0005
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_METHOD_패치.md::OP0006
ACTION: add_rule
RULE_TEXT: tools/*.py Forbidden patch targets:
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 399
BLOCK_ID: CHECKLIST_METHOD_패치_B0006
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_METHOD_패치.md::OP0007
ACTION: add_rule
RULE_TEXT: Multi-node dependency handoff is broken: tools/build_node_context.py resolves dependencies from plan workspace_path, but the system never stores a per-node accepted artifact path after commit.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 561
BLOCK_ID: CHECKLIST_METHOD_패치_B0007
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_METHOD_패치.md::OP0008
ACTION: add_rule
RULE_TEXT: HANDOFF_POLICY.md requires accepted-artifact summaries, artifact IDs, reusable outputs, unresolved risks, and downstream-ready context; tools/build_node_context.py only copies raw text from workspace_path.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 577
BLOCK_ID: CHECKLIST_METHOD_패치_B0008
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_METHOD_패치.md::OP0009
ACTION: add_rule
RULE_TEXT: STATE.json has no node-to-accepted-artifact mapping; only global accepted_artifact_id and current_baseline_path are stored, which is insufficient for multi-node handoff.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 581
BLOCK_ID: CHECKLIST_METHOD_패치_B0009
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_METHOD_패치.md::OP0010
ACTION: add_rule
RULE_TEXT: STATE_TRANSITIONS.md requires in_progress and retired transitions, but code only commits accepted; node in_progress and retired state are not implemented.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 583
BLOCK_ID: CHECKLIST_METHOD_패치_B0010
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_METHOD_패치.md::OP0011
ACTION: add_rule
RULE_TEXT: tools/system_evolver.py and tools/meta_loop.py do not read or enforce REPO_LOCK.json or PATCH_PROTOCOL.md; mutation permissions are advisory only.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 599
BLOCK_ID: CHECKLIST_METHOD_패치_B0011
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_METHOD_패치.md::OP0012
ACTION: add_rule
RULE_TEXT: tools/select_survivor.py only records diversity collapse; it does not enforce the ACCEPTANCE_CRITERIA.md rule that a survivor must not be diversity-collapsed when a materially distinct stronger candidate exists.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 622
BLOCK_ID: CHECKLIST_METHOD_패치_B0012
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_METHOD_패치.md::OP0013
ACTION: add_rule
RULE_TEXT: tools/validate_acceptance.py does not actually implement GOAL_POLICY.md; it only rejects artifacts containing the literal substrings fabricated, illegal, or fraud.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 654
BLOCK_ID: CHECKLIST_METHOD_패치_B0013
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_METHOD_패치.md::OP0014
ACTION: add_rule
RULE_TEXT: Neither tools/meta_loop.py nor tools/system_evolver.py loads or enforces REPO_LOCK.json or PATCH_PROTOCOL.md; repo-lock and patch-discipline controls are documentation-only.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 659
BLOCK_ID: CHECKLIST_METHOD_패치_B0014
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_METHOD_패치.md::OP0015
ACTION: add_rule
RULE_TEXT: No persisted node_id -> accepted artifact path/id mapping exists; only a single global accepted_artifact_id / current_baseline_path / baseline registry pointer is stored.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 704
BLOCK_ID: CHECKLIST_METHOD_패치_B0015
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_METHOD_패치.md::OP0016
ACTION: add_rule
RULE_TEXT: tools/meta_loop.py convergence logic uses count-only comparison (len(accepted_nodes) >= len(PLAN_GRAPH.nodes)) and does not reconcile renamed/removed nodes after graph mutation.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 718
BLOCK_ID: CHECKLIST_METHOD_패치_B0016
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_METHOD_패치.md::OP0017
ACTION: add_rule
RULE_TEXT: tools/build_node_context.py resolves dependency artifacts via each dependency node’s workspace_path, but the runtime never persists per-node accepted artifact paths; downstream context can point to overwritten drafts or wrong files.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 720
BLOCK_ID: CHECKLIST_METHOD_패치_B0017
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_METHOD_패치.md::OP0018
ACTION: add_rule
RULE_TEXT: Handoff readiness is only approximated by loose keyword checks in tools/score_artifact.py; there is no hard contract check that downstream prompts actually received valid accepted-upstream summaries.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 724
BLOCK_ID: CHECKLIST_METHOD_패치_B0018
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_METHOD_패치.md::OP0019
ACTION: add_rule
RULE_TEXT: Multi-node handoff depends on PLAN_GRAPH.json.workspace_path, but accepted artifact locations are not persisted per node; downstream node execution cannot reliably consume upstream accepted artifacts.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 746
BLOCK_ID: CHECKLIST_METHOD_패치_B0019
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_METHOD_패치.md::OP0020
ACTION: add_rule
RULE_TEXT: HANDOFF_POLICY.md says accepted upstream artifacts must be summarized for downstream use, but implementation reads raw workspace_path content and never resolves committed accepted artifacts by node.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 763
BLOCK_ID: CHECKLIST_METHOD_패치_B0020
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_METHOD_패치.md::OP0021
ACTION: add_rule
RULE_TEXT: STATE.json stores only one global accepted_artifact_id, and BASELINE_REGISTRY.json stores only one global baseline; there is no per-node accepted-artifact mapping.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 766
BLOCK_ID: CHECKLIST_METHOD_패치_B0021
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_METHOD_패치.md::OP0022
ACTION: add_rule
RULE_TEXT: tools/validate_acceptance.py does not actually validate against GOAL_POLICY.md; it only scans for a few literal words.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 775
BLOCK_ID: CHECKLIST_METHOD_패치_B0022
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_METHOD_패치.md::OP0023
ACTION: add_rule
RULE_TEXT: tools/system_evolver.py does not load or enforce PATCH_PROTOCOL.md or REPO_LOCK.json; patch discipline, allowed targets, and immutable directories are declarative only.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 781
BLOCK_ID: CHECKLIST_METHOD_패치_B0023
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_METHOD_패치.md::OP0024
ACTION: add_rule
RULE_TEXT: tools/commit_state.py records accepted node IDs only; it does not persist the winner artifact path/id per node for later handoff.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 786
BLOCK_ID: CHECKLIST_METHOD_패치_B0024
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_METHOD_패치.md::OP0025
ACTION: add_rule
RULE_TEXT: Governance files added by the meta-loop package (PATCH_PROTOCOL.md, REPO_LOCK.json, ITERATION_LEDGER.md) are not integrated into the main runtime loop and are only partially/ambiguously referenced by the duplicate evolver implementations.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 800
BLOCK_ID: CHECKLIST_METHOD_패치_B0025
RATIONALE: no strong canonical overlap
