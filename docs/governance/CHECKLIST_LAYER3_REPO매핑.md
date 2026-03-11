MetaOS 층 3 체크리스트 정본
Repo File 1:1 Mapping Checklist

---

## WEBNOVEL_CANONICAL_OVERRIDE

This override is the canonical Layer 3 mapping for the current `web_novel` repository.

If any imported generic MetaOS mapping below conflicts with this override, this override wins for this repository.

### 1. Canonical Runtime Entry Mapping

- Artifact runtime entrypoint -> `app.py`
- Generation runtime orchestrator -> `engine/pipeline.py`
- Runtime config authority -> `engine/runtime_config.py`
- State persistence authority -> `engine/state.py`
- OpenAI model gateway -> `engine/openai_client.py`

PASS conditions:
- `app.py` is the user-facing runtime entry
- `engine/pipeline.py` is the episode generation orchestration center
- runtime and state ownership are explicit

FAIL conditions:
- another runtime entry is treated as canonical without being documented here
- generation authority is split across undocumented duplicate entrypoints

### 2. Goal / Objective Mapping

- User task goal -> `GOAL.md`
- System objective -> `SYSTEM_OBJECTIVE.md`
- Governance anchor -> `METAOS_ANCHOR.md`
- Repo alignment bridge -> `docs/governance/WEBNOVEL_ALIGNMENT_STATUS.md`

### 3. Generation / Prompt Assembly Mapping

- Outline generation -> `engine/pipeline.py`
- Episode generation -> `engine/pipeline.py`
- Prompt templates -> `engine/prompts.py`
- Platform / sub-engine strategy -> `engine/strategy.py`
- Style shaping -> `engine/style.py`

### 4. Quality Gate Mapping

- Minimum gate predicate -> `engine/quality_gate.py`
- Validation aggregation / import sanity -> `engine/integrated_validator.py`
- Score evaluation source used by pipeline -> `analytics/content_ceiling.py`
- Regression rejection -> `engine/regression_guard.py`

### 5. Hook / Cliffhanger / Tension Mapping

- Cliffhanger planning and enforcement -> `engine/cliffhanger_engine.py`
- Tension pacing state -> `engine/tension_wave.py`
- Event pressure generation -> `engine/event_generator.py`
- Retention forecast input -> `engine/predictive_retention.py`
- Tests -> `tests/test_fun_cliffhanger_engine.py`, `tests/test_fun_tension_wave.py`, `tests/test_fun_retention_engine.py`

### 6. Character / Conflict / Emotion Mapping

- Character pressure and arc state -> `engine/character_arc.py`
- Conflict escalation memory -> `engine/conflict_memory.py`
- Information / emotion balance -> `engine/information_emotion.py`
- Antagonist pressure planning -> `engine/antagonist_planner.py`
- Tests -> `tests/test_fun_character_engine.py`, `tests/test_fun_conflict_engine.py`, `tests/test_absolute_ceiling_regression.py`

### 7. World Logic / Causality / Repair Mapping

- World-state continuity -> `engine/world_logic.py`
- Scene causality checks -> `engine/scene_causality.py`
- Promise / payoff tracking -> `engine/promise_graph.py`
- Causal repair planning and audit -> `engine/causal_repair.py`, `engine/repair_diff_audit.py`
- Tests -> `tests/test_absolute_ceiling_regression.py`

### 8. Retention / Serialization / Reader Pressure Mapping

- Retention state and prediction -> `engine/predictive_retention.py`
- Reward serialization -> `engine/reward_serialization.py`
- Market serialization -> `engine/market_serialization.py`
- Pattern anti-repetition memory -> `engine/pattern_memory.py`
- Tests -> `tests/test_fun_retention_engine.py`, `tests/test_content_ceiling.py`, `tests/test_absolute_ceiling_regression.py`

### 9. Market / Portfolio / Release Mapping

- External rank ingestion -> `engine/external_rank.py`
- Market policy -> `engine/market_policy_engine.py`
- Portfolio orchestration -> `engine/portfolio_orchestrator.py`
- Cross-track release -> `engine/cross_track_release.py`
- Portfolio scheduling support -> `portfolio_layer/wave_scheduler.py`
- Market adapter layer -> `market_layer/market_api.py`, `market_layer/rank_guard.py`

### 10. Reliability / Safety / Backup Mapping

- Long-run reliability simulation -> `engine/reliability.py`
- Safe file writes -> `engine/safe_io.py`
- Backup controls -> `engine/backup_manager.py`, `engine/full_backup_manager.py`, `engine/backup_retention.py`
- Delete / mutation guardrails -> `engine/delete_guard.py`, `engine/safe_guard.py`, `engine/governance.py`

### 11. Test / Audit Mapping

- Repo-wide regression bundle -> `tests/test_absolute_ceiling_regression.py`
- Core quality slices -> `tests/test_fun_cliffhanger_engine.py`, `tests/test_fun_character_engine.py`, `tests/test_fun_conflict_engine.py`, `tests/test_fun_retention_engine.py`, `tests/test_fun_tension_wave.py`
- Revenue / KPI side modules -> `tests/test_roi.py`, `tests/test_funnel.py`, `tests/test_kpi.py`
- Imported coverage ledger -> `docs/governance/COVERAGE_AUDIT.csv`
- Conflict ledger -> `docs/governance/CONFLICT_LOG.csv`

### 12. Reference-Only Rule

The imported generic Layer 3 body below is retained as source reference, not as direct runtime truth, except where it matches the mappings above.

---
0. 층 3의 목적
층 3의 목적은 층 2에서 정의한 각 모듈 책임을 실제 repo 파일, 디렉터리, 상태 파일, 문서 파일에 1:1 또는 명시적 N:1로 매핑하여, 무엇이 정본인지 무엇이 중복인지 무엇이 누락인지 무엇이 runtime authority인지 판정 가능하게 만드는 것이다. 
즉 층 3은
모듈 책임 → 실제 파일 → canonical file → PASS / FAIL 판정 
으로 내리는 층이다.
1. Canonical Runtime Entry Mapping
역할
실제로 무엇을 실행하면 되는지, 어떤 파일이 runtime authority인지 고정한다. 
체크리스트
[ ] canonical runtime entrypoint가 하나로 고정되어 있다 [ ] 실제 운영 entrypoint 파일이 명시되어 있다 [ ] meta runtime entrypoint와 artifact runtime entrypoint가 구분된다 [ ] loop.py의 역할과 meta_loop.py의 역할이 문서와 일치한다 [ ] system_evolver.py의 역할이 문서와 일치한다 [ ] 중복 버전 파일이 정리되었거나 canonical winner가 명시되어 있다 
권장 canonical file 매핑
Artifact runtime entrypoint → tools/loop.py Meta runtime entrypoint → tools/meta_loop.py System evolution entrypoint → tools/system_evolver.py 
FAIL 조건
[ ] meta_loop.py가 여러 버전으로 공존하고 canonical이 없다 [ ] system_evolver.py가 여러 버전으로 공존하고 canonical이 없다 [ ] 문서에 적힌 실행 파일과 실제 runtime 파일이 다르다 
2. Goal / Objective Module File Mapping
역할
무엇을 최적화하는지, 어떤 도메인을 목표로 하는지, generic floor와 domain target을 어디에 적는지 고정한다. 
체크리스트
[ ] GOAL.md가 canonical user-goal file이다 [ ] SYSTEM_OBJECTIVE.md 또는 동등 canonical 상위 목적 파일이 존재한다 [ ] METAOS_ANCHOR.md 또는 동등 anchor file이 존재한다 [ ] GOAL.md는 task/domain goal을 담고 SYSTEM_OBJECTIVE.md는 system-level objective를 담는다 [ ] generic floor / domain target / production target이 canonical file에 기록된다 
권장 canonical file 매핑
User task goal → GOAL.md System objective → SYSTEM_OBJECTIVE.md Invariant anchor / constitution → METAOS_ANCHOR.md 
FAIL 조건
[ ] goal 정의가 여러 파일에 흩어져 있다 [ ] system objective가 채팅 문맥에만 있고 repo 파일에 없다 [ ] anchor가 문서로 존재하지 않는다 
3. Planning / Graph Module File Mapping
역할
goal을 execution graph로 바꾸고, node dependency와 runtime graph를 관리하는 파일을 고정한다. 
체크리스트
[ ] planner.py가 canonical planner implementation이다 [ ] GOAL_SPEC.md가 canonical compiled goal spec file이다 [ ] PLAN_GRAPH.json이 canonical runtime graph file이다 [ ] PLAN_GRAPH_SCHEMA.md가 canonical graph schema file이다 [ ] planner.py는 PLAN_GRAPH.json과 충돌 없이 동작한다 [ ] execution state는 PLAN_GRAPH.json과 분리 저장되거나 안전하게 병합된다 
권장 canonical file 매핑
Planner implementation → tools/planner.py Compiled goal spec → GOAL_SPEC.md Runtime plan graph → PLAN_GRAPH.json Plan graph schema → PLAN_GRAPH_SCHEMA.md 
FAIL 조건
[ ] planner.py가 accepted node 상태를 매번 덮어쓴다 [ ] PLAN_GRAPH.json이 schema와 다르다 [ ] graph status와 runtime state가 한 파일 안에서 충돌한다 
4. Artifact Generation Module File Mapping
역할
artifact를 생성/수정하는 canonical worker file과 draft artifact location을 고정한다. 
체크리스트
[ ] codex_worker.py가 canonical artifact generation worker다 [ ] ARTIFACT_CONTRACT.md가 canonical artifact schema file이다 [ ] workspace/artifact.md가 canonical current workspace artifact다 [ ] multi-candidate 사용 시 workspace/candidates/... 구조가 canonical이다 [ ] generation target path가 문서와 runtime에서 일치한다 
권장 canonical file 매핑
Generation worker → tools/codex_worker.py Artifact schema / contract → ARTIFACT_CONTRACT.md Primary workspace artifact → workspace/artifact.md Candidate workspace → workspace/candidates/<node_id>/<candidate_id>.md 
FAIL 조건
[ ] artifact target file이 문서와 코드에서 다르다 [ ] artifact contract가 runtime에서 실제로 참조되지 않는다 [ ] workspace artifact와 committed artifact 구분이 없다 
5. Semantic Validation Module File Mapping
역할
artifact competence floor를 검사하는 validator 파일들을 고정한다. 
체크리스트
[ ] validate_format.py가 canonical format validator다 [ ] validate_goal_alignment.py가 canonical goal validator다 [ ] validate_acceptance.py가 canonical acceptance validator다 [ ] semantic validator가 별도 파일로 존재하거나 acceptance validator에 통합되어 있다 [ ] validate_all.py가 validator orchestration의 canonical entry다 [ ] VALIDATION_GATE.md가 validator ordering과 authority를 설명한다 
권장 canonical file 매핑
Format validator → tools/validate_format.py Goal alignment validator → tools/validate_goal_alignment.py Acceptance / semantic validator → tools/validate_acceptance.py 또는 tools/validate_semantic.py (권장 추가 가능) Validation orchestrator → tools/validate_all.py Validator contract → VALIDATION_GATE.md 
FAIL 조건
[ ] semantic validator가 파일로 존재하지 않는다 [ ] validate_all.py와 개별 validator CLI 계약이 다르다 [ ] 문서상 validator authority와 runtime order가 다르다 
6. Repair Policy Module File Mapping
역할
실패 원인을 읽고 targeted patch를 수행하는 파일을 고정한다. 
체크리스트
[ ] repair_artifact.py가 canonical repair engine이다 [ ] FAILURE_ACTION_MAP.md가 canonical failure-to-repair mapping file이다 [ ] repair_artifact.py가 FAILURE_ACTION_MAP.md를 실제로 읽는다 [ ] repair_artifact.py가 validator / judge output path를 실제로 읽는다 
권장 canonical file 매핑
Repair engine → tools/repair_artifact.py Failure policy map → FAILURE_ACTION_MAP.md 
FAIL 조건
[ ] repair_artifact.py가 failure code를 실제로 반영하지 않는다 [ ] FAILURE_ACTION_MAP.md가 문서로만 존재한다 [ ] repair 이후 재검증 연결이 없다 
7. Quality Scoring Module File Mapping
역할
artifact quality를 점수화하고 기록하는 파일을 고정한다. 
체크리스트
[ ] judge_artifact.py가 canonical judge scoring file이다 [ ] score_artifact.py가 canonical rule scoring file이다 [ ] external_metrics.py가 canonical external metric file이다 [ ] judge summary output path가 canonical으로 고정된다 [ ] rule score summary output path가 canonical으로 고정된다 [ ] metric history 저장 위치가 canonical으로 고정된다 
권장 canonical file 매핑
Judge scorer → tools/judge_artifact.py Rule scorer → tools/score_artifact.py External metric hook → tools/external_metrics.py Judge summary → workspace/judge_summary.json 또는 workspace/candidates/<node>/<candidate>.judge.json Rule summary → workspace/candidates/<node>/<candidate>.score.json 
FAIL 조건
[ ] judge summary path가 문서/manifest/code에서 다르다 [ ] score_artifact.py가 runtime에서 실제로 호출되지 않는다 [ ] external metric 결과가 저장되지 않는다 
8. Acceptance Gate Module File Mapping
역할
무엇이 최종 채택되는지 결정하는 gate 관련 파일과 실행 순서를 고정한다. 
체크리스트
[ ] ACCEPTANCE_CRITERIA.md가 canonical acceptance contract다 [ ] select_survivor.py가 canonical survivor selector다 [ ] commit_artifact.py가 canonical artifact adoption file이다 [ ] commit_state.py가 canonical state adoption file이다 [ ] validate_all → judge → rule score → external → survivor → commit 순서가 코드에 반영된다 [ ] REJECT 경로와 ACCEPT 경로가 명확히 분리된다 
권장 canonical file 매핑
Acceptance contract → ACCEPTANCE_CRITERIA.md Survivor selection → tools/select_survivor.py Artifact commit → tools/commit_artifact.py State commit → tools/commit_state.py 
FAIL 조건
[ ] commit_artifact.py가 일부 gate 실패 상태에서도 실행 가능하다 [ ] select_survivor.py가 hard validation을 무시할 수 있다 [ ] ACCEPTANCE_CRITERIA.md와 runtime gate sequence가 다르다 
9. State Persistence Module File Mapping
역할
state, metrics, history, lineage, accepted mapping을 저장하는 파일들을 고정한다. 
체크리스트
[ ] STATE.json이 canonical runtime state file이다 [ ] METRICS.json이 canonical metrics file이다 [ ] BASELINE_REGISTRY.json이 canonical baseline registry file이다 [ ] history/ 디렉터리가 canonical append-only history directory다 [ ] node별 accepted artifact mapping file이 존재한다 [ ] lineage parent 정보가 artifact commit에 반영된다 
권장 canonical file 매핑
Runtime state → STATE.json Metrics → METRICS.json Baseline registry → BASELINE_REGISTRY.json History → history/*.json Node accepted mapping → STATE.json 내부 accepted_nodes / node_artifacts 또는 별도 NODE_ARTIFACT_MAP.json (권장 가능) 
FAIL 조건
[ ] accepted artifact mapping이 node별로 없다 [ ] baseline lineage가 commit 결과에 반영되지 않는다 [ ] history가 append-only가 아니다 
10. Handoff Module File Mapping
역할
upstream accepted artifact를 downstream에 전달하는 파일과 context output path를 고정한다. 
체크리스트
[ ] build_node_context.py가 canonical handoff builder다 [ ] HANDOFF_POLICY.md가 canonical handoff contract다 [ ] workspace/node_context/<node>.md가 canonical handoff output path다 [ ] handoff input source가 accepted artifact 기준으로 고정된다 [ ] dependency artifact id/path를 기록할 canonical field가 있다 
권장 canonical file 매핑
Handoff builder → tools/build_node_context.py Handoff contract → HANDOFF_POLICY.md Node handoff context output → workspace/node_context/<node_id>.md 
FAIL 조건
[ ] build_node_context.py가 workspace draft를 읽는다 [ ] HANDOFF_POLICY.md와 실제 handoff 내용이 다르다 [ ] reusable outputs / risks / summary가 실제 파일에 없다 
11. Meta Evolution Module File Mapping
역할
artifact가 아니라 repo/system 구조를 개선하는 파일들을 고정한다. 
체크리스트
[ ] meta_loop.py가 canonical meta iteration controller다 [ ] system_evolver.py가 canonical system mutation engine이다 [ ] ITERATION_LEDGER.md 또는 동등 ledger가 canonical evolution log다 [ ] meta loop trigger source가 STATE/METRICS 기반으로 고정된다 [ ] system mutation output이 repo 파일 변경으로 반영된다 
권장 canonical file 매핑
Meta loop controller → tools/meta_loop.py System evolver → tools/system_evolver.py Evolution ledger → ITERATION_LEDGER.md 또는 history/system_evolution.json 
FAIL 조건
[ ] system_evolver.py가 여러 버전으로 공존한다 [ ] meta_loop.py가 실패 시 그냥 종료만 한다 [ ] evolution log가 남지 않는다 
12. Mutation Governance Module File Mapping
역할
mutation allowed/forbidden target을 문서와 runtime에서 고정한다. 
체크리스트
[ ] PATCH_PROTOCOL.md가 canonical mutation protocol file이다 [ ] REPO_LOCK.json이 canonical mutation lock file이다 [ ] system_evolver.py가 두 파일을 실제로 읽는다 [ ] mutation allowed target과 immutable target이 코드에서 enforce된다 
권장 canonical file 매핑
Patch protocol → PATCH_PROTOCOL.md Repo mutation lock → REPO_LOCK.json 
FAIL 조건
[ ] protocol/lock 문서만 존재한다 [ ] runtime에서 enforcement가 없다 
13. Post-Patch Verification Module File Mapping
역할
patch 이후 생존 검증을 담당하는 파일/스크립트를 고정한다. 
체크리스트
[ ] post-patch verification entry가 존재한다 [ ] import/CLI/schema/smoke test를 담당하는 canonical file이 있다 [ ] system_evolver.py가 patch 이후 해당 verification을 호출한다 [ ] verification 실패 시 reject/rollback 경로가 존재한다 
권장 canonical file 매핑
Post-patch verification orchestrator → tools/post_patch_verify.py 또는 tools/system_self_check.py (권장 추가 가능) Smoke validation → tools/validate_all.py + 추가 self-check runner 
FAIL 조건
[ ] patch 이후 verification 전용 파일이 없다 [ ] system_evolver.py가 verification을 호출하지 않는다 
14. Branch / Exploration Module File Mapping
역할
branching, candidate diversity, clustering, exploration budget을 담당하는 파일을 고정한다. 
체크리스트
[ ] branch_controller.py가 canonical branch policy runtime이다 [ ] BRANCH_POLICY.md가 canonical branch policy file이다 [ ] select_survivor.py가 canonical survivor file이다 [ ] cluster_candidates.py가 canonical clustering file이다 [ ] candidate family sidecar output path가 canonical이다 [ ] exploration budget source가 canonical state/metrics field에 존재한다 
권장 canonical file 매핑
Branch controller → tools/branch_controller.py Branch policy → BRANCH_POLICY.md Survivor selector → tools/select_survivor.py Candidate clustering → tools/cluster_candidates.py Candidate family sidecar → workspace/candidates/<node>/<candidate>.family.json 
FAIL 조건
[ ] branching은 있지만 canonical policy file과 연결되지 않는다 [ ] clustering 결과가 selection에 전혀 반영되지 않는다 [ ] exploration budget 필드가 state/metrics에 없다 
15. Objective / Representation Mutation Module File Mapping
역할
goal definition과 artifact schema/representation을 바꾸는 실험적 상위 mutation 경로를 고정한다. 
체크리스트
[ ] objective mutation을 담당하는 canonical file이 존재한다 [ ] representation mutation을 담당하는 canonical file이 존재한다 [ ] validator/schema update file이 연결된다 [ ] mutation 기록 파일이 존재한다 [ ] rollback 대상 파일이 명시된다 
권장 canonical file 매핑
Objective mutation controller → tools/objective_mutator.py (권장 추가 가능) Representation mutation controller → tools/representation_mutator.py (권장 추가 가능) Schema update target → ARTIFACT_CONTRACT.md / PLAN_GRAPH_SCHEMA.md / validators Mutation history → history/objective_mutations.json → history/representation_mutations.json 
FAIL 조건
[ ] objective/representation mutation 책임 파일이 없다 [ ] 문서상만 있고 runtime 경로가 없다 
16. Repo Manifest / Documentation Mapping
역할
repo 문서, manifest, runtime code가 같은 시스템을 설명하게 고정한다. 
체크리스트
[ ] REPO_MANIFEST.json이 현재 canonical files를 반영한다 [ ] AGENTS.md가 현재 runtime 구조를 반영한다 [ ] EXECUTION_COMMANDS.md가 실제 CLI 계약과 일치한다 [ ] ACCEPTANCE_CRITERIA.md / VALIDATION_GATE.md / BRANCH_POLICY.md가 현재 코드와 일치한다 [ ] obsolete 문서가 정리되었거나 deprecated로 표시된다 
권장 canonical file 매핑
Repo manifest → REPO_MANIFEST.json Runtime instruction doc → AGENTS.md Execution commands doc → EXECUTION_COMMANDS.md 
FAIL 조건
[ ] 문서와 코드가 다른 시스템을 설명한다 [ ] obsolete iteration 문서가 canonical처럼 남아 있다 [ ] CLI 사용법이 실제 코드와 다르다 
17. Repo File Mapping 판정 기준
PASS
[ ] 각 모듈 책임이 canonical file에 명확히 매핑된다 [ ] 중복 파일 중 canonical winner가 정해져 있다 [ ] 문서 / manifest / runtime / state 저장 위치가 서로 일치한다 [ ] file-level ambiguity가 없다 
WEAK
[ ] 대부분 매핑되지만 일부 canonical ambiguity가 남아 있다 [ ] 문서와 runtime 사이 불일치가 일부 있다 [ ] state / handoff / verification 파일이 불완전하다 
FAIL
[ ] 어떤 파일이 정본인지 결정되지 않았다 [ ] 동일 책임을 여러 파일이 충돌하며 가진다 [ ] runtime / docs / manifest / state path가 서로 다르다 
초압축 층 3 체크리스트
매번 빠르게 볼 때는 이것만 보면 된다.
[ ] runtime entrypoint 정본이 하나인가 [ ] GOAL / SYSTEM_OBJECTIVE / ANCHOR 파일이 분리되어 있는가 [ ] planner / graph / state가 충돌하지 않는가 [ ] artifact generation / validation / repair / scoring / commit 파일이 canonical로 정리됐는가 [ ] accepted artifact / node state / lineage / history 저장 위치가 고정됐는가 [ ] handoff가 accepted artifact 기준 파일을 읽는가 [ ] meta_loop / system_evolver / mutation governance / post-patch verification 파일이 정리됐는가 [ ] branch / exploration / clustering 파일이 canonical로 연결됐는가 [ ] objective / representation mutation 파일 책임이 정의됐는가 [ ] manifest / docs / runtime이 같은 시스템을 설명하는가 
층 3 핵심 문장
층 3의 목표는 MetaOS의 각 모듈 책임을 실제 repo 파일과 경로에 canonical하게 고정하여, 무엇이 정본이고 무엇이 중복이며 무엇이 누락인지 파일 수준에서 판정 가능하게 만드는 것이다. 
층 1~3 최종 구조
층 1 무엇을 원하는가 층 2 그걸 어떤 모듈이 책임지는가 층 3 그 모듈 책임이 실제 어떤 파일에 매핑되는가


## APPEND_ONLY_PATCH_BLOCKS

TARGET_DOC: CHECKLIST_LAYER3_REPO매핑.md
BLOCK_COUNT: 51

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0001
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 37
RULE_TEXT: Secrets must never be stored in plaintext within public repositories.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0002
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 103
RULE_TEXT: System files must follow defined management rules.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0003
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 109
RULE_TEXT: Artifact files must remain immutable.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0004
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 110
RULE_TEXT: Runtime files may be updated but must maintain version history.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0005
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 18
RULE_TEXT: Must comply with GOAL_POLICY.md
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0006
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 240
RULE_TEXT: each node must have node_id, status, dependencies, workspace_path
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0007
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 407
RULE_TEXT: repository must remain runnable
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0008
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 500
RULE_TEXT: Expected chain cannot start: no project-local planner component exists.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0009
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 517
RULE_TEXT: REPO_MANIFEST.json is missing, so manifest-to-filesystem consistency cannot hold.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0010
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 551
RULE_TEXT: The only matching filenames discovered were unrelated installed-package files (moviepy/spacy loop.py, torch planner.py), not repository components.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0011
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 555
RULE_TEXT: No Python dependency manifest/lockfile (requirements.txt, pyproject.toml, or equivalent) pinning the required openai package.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0012
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 556
RULE_TEXT: No Node dependency manifest/lockfile (package.json, package-lock.json, or equivalent) pinning the required @openai/codex CLI/runtime.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0013
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 562
RULE_TEXT: tools/meta_loop.py stops when tools/loop.py returns blocked/non-zero, so the meta-loop never performs system evolution on the primary failure path it is supposed to recover.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0014
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 565
RULE_TEXT: tools/select_survivor.py: uses p(...) but never imports p from tools/common.py.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0015
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 572
RULE_TEXT: PLAN_GRAPH_SCHEMA.md defines validator_set, but tools/validate_all.py never reads node schema and hardcodes validators.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0016
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 573
RULE_TEXT: tools/planner.py does not validate generated plan graphs against PLAN_GRAPH_SCHEMA.md; it only checks that nodes is non-empty.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0017
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 576
RULE_TEXT: EXTERNAL_METRICS.md says default behavior without hook config is SKIP; tools/external_metrics.py implements no SKIP/disable path and always runs a built-in metric.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0018
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 584
RULE_TEXT: STATE.json.current_node_id is declared but never written by tools/loop.py or tools/commit_state.py.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0019
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 588
RULE_TEXT: ARTIFACT_CONTRACT.md requires exact section order and no freeform preamble, but tools/validate_format.py checks only token presence, a few empties, and length.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0020
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 589
RULE_TEXT: ARTIFACT_CONTRACT.md marks many metadata fields as required, but validators do not enforce non-empty ARTIFACT_CLASS, GOAL_REF, PLAN_NODE_REF, STATE_REF, and related metadata; tools/commit_artifact.py only fills a subset.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0021
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 598
RULE_TEXT: tools/meta_loop.py evolves only after a successful artifact loop; when tools/loop.py returns blocked/non-zero, meta-loop exits instead of invoking system evolution.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0022
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 608
RULE_TEXT: tools/build_node_context.py truncates upstream artifacts to 3000 chars and emits a raw dump instead of the structured dependency summary required by HANDOFF_POLICY.md.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0023
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 613
RULE_TEXT: tools/retire_candidates.py cannot execute, so the normal post-survivor retirement path is broken.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0024
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 614
RULE_TEXT: tools/cluster_candidates.py only logs clusters; cluster/family outputs are not consumed by survivor selection or pruning.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0025
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 617
RULE_TEXT: Candidate files are never cleared between runs; stale candidates and stale judge/score/family sidecars remain eligible for later selection.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0026
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 623
RULE_TEXT: tools/branch_controller.py uses only global plateau_counter >= 2; it does not implement the full branch-trigger conditions documented in BRANCH_POLICY.md.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0027
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 642
RULE_TEXT: VALIDATION_GATE.md says every check object must contain name, status, code, and details, but all validator PASS checks omit code.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0028
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 650
RULE_TEXT: STATE.json.current_node_id is never maintained by runtime code, despite multi-node execution and node-context generation.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0029
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 652
RULE_TEXT: tools/validate_format.py does not check non-empty values for several required contract fields:
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0030
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 664
RULE_TEXT: tools/build_node_context.py does not emit dependency artifact IDs, reusable outputs, or unresolved downstream-relevant risks as required by HANDOFF_POLICY.md.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0031
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 669
RULE_TEXT: tools/cluster_candidates.py and family summaries are history-only; pruning and survivor selection do not consume cluster/family data despite BRANCH_POLICY.md and CANDIDATE_FAMILIES.md.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0032
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 673
RULE_TEXT: EXTERNAL_METRICS.md says “no hook config => SKIP” and allows missing external metrics only when explicitly disabled, but no hook-config or disable mechanism exists and tools/external_metrics.py never emits SKIP.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0033
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 690
RULE_TEXT: Add-on package instructions introduce python tools/meta_loop.py as a top-level runner, but the canonical command docs were never updated to include it.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0034
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 701
RULE_TEXT: STATE.json.last_failure_code is never updated anywhere, so failure-family triggers in FAILURE_ACTION_MAP.md / BRANCH_POLICY.md have no persisted source of truth.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0035
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 702
RULE_TEXT: STATE.json.current_node_id is never updated during node execution.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0036
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 708
RULE_TEXT: tools/validate_all.py ignores node validator_set and always runs a hardcoded validator trio.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0037
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 709
RULE_TEXT: tools/validate_format.py does not enforce the exact ARTIFACT_CONTRACT.md structure: it ignores section order, boundary --- markers, the no-extra-sections rule, and emptiness of most required metadata fields.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0038
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 714
RULE_TEXT: In all provided meta_loop.py variants, plateau handling occurs only after a successful tools/loop.py run; if tools/loop.py exits blocked/nonzero, the meta-loop breaks before evolution can run.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0039
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 729
RULE_TEXT: tools/branch_controller.py ignores node-specific max_branches, plateau-escalation caps, repair-count triggers, and failure-family triggers; it keys only off a shared plateau_counter.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0040
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 730
RULE_TEXT: tools/cluster_candidates.py and family summaries are recorded but never enforced in selection/pruning; near-duplicate pruning and family-aware survivor choice are absent.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0041
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 736
RULE_TEXT: The repo claims multi-node execution, candidate families, retirement policy, external hooks, and meta-loop control, but several of those systems are only documented or partially recorded, not fully enforced in code.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0042
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 750
RULE_TEXT: tools/select_survivor.py calls p(...) inside the diversity check but never imports p from common.py; when more than one survivor exists, this raises NameError.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0043
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 762
RULE_TEXT: EXTERNAL_METRICS.md defines a SKIP path when no hook config exists, but tools/external_metrics.py has no hook-config/disable mechanism and never implements that documented default.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0044
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 767
RULE_TEXT: STATE.current_node_id exists but is never maintained by tools/loop.py, so node-state tracking is incomplete.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0045
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 770
RULE_TEXT: ARTIFACT_CONTRACT.md requires exact section order, no extra sections, no preamble outside schema, and no empty required fields; tools/validate_format.py does not enforce order, boundary markers, extra sections, or emptiness of most metadata fields.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0046
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 774
RULE_TEXT: tools/score_artifact.py --has-downstream can fail on handoff_not_ready, but the artifact contract has no required handoff field or token set.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0047
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 779
RULE_TEXT: In all provided meta-loop variants, plateau-based system evolution is checked only after tools/loop.py returns success; if tools/loop.py exits non-zero on blockage/plateau, meta-loop breaks before any system evolution occurs.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0048
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 782
RULE_TEXT: REPO_LOCK.json protects only a subset of the actual runtime core; final runtime-critical files such as tools/score_artifact.py, tools/external_metrics.py, tools/build_node_context.py, tools/select_survivor.py, tools/retire_candidates.py, and tools/commit_state.py are outside runtime_core.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0049
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 788
RULE_TEXT: BASELINE_REGISTRY.json is global rather than per-node, so it cannot serve as a reliable handoff source for multi-node graphs.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0050
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 792
RULE_TEXT: tools/cluster_candidates.py and candidate family summaries are write-only; tools/select_survivor.py and tools/branch_controller.py do not consume their outputs.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0051
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 793
RULE_TEXT: tools/branch_controller.py never reads BRANCH_POLICY.md or node-level branch_policy; documented caps (max alive candidates, max plateau escalations, max_branches) are not enforced.
RATIONALE: no strong canonical overlap


## APPLY_QUEUE_OPERATIONS

TARGET_DOC: CHECKLIST_LAYER3_REPO매핑.md
TOTAL_OPS: 51

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0001
ACTION: add_rule
RULE_TEXT: Secrets must never be stored in plaintext within public repositories.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 37
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0001
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0002
ACTION: add_rule
RULE_TEXT: System files must follow defined management rules.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 103
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0002
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0003
ACTION: add_rule
RULE_TEXT: Artifact files must remain immutable.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 109
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0003
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0004
ACTION: add_rule
RULE_TEXT: Runtime files may be updated but must maintain version history.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 110
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0004
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0005
ACTION: add_rule
RULE_TEXT: Must comply with GOAL_POLICY.md
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 18
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0005
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0006
ACTION: add_rule
RULE_TEXT: each node must have node_id, status, dependencies, workspace_path
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 240
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0006
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0007
ACTION: add_rule
RULE_TEXT: repository must remain runnable
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 407
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0007
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0008
ACTION: add_rule
RULE_TEXT: Expected chain cannot start: no project-local planner component exists.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 500
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0008
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0009
ACTION: add_rule
RULE_TEXT: REPO_MANIFEST.json is missing, so manifest-to-filesystem consistency cannot hold.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 517
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0009
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0010
ACTION: add_rule
RULE_TEXT: The only matching filenames discovered were unrelated installed-package files (moviepy/spacy loop.py, torch planner.py), not repository components.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 551
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0010
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0011
ACTION: add_rule
RULE_TEXT: No Python dependency manifest/lockfile (requirements.txt, pyproject.toml, or equivalent) pinning the required openai package.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 555
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0011
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0012
ACTION: add_rule
RULE_TEXT: No Node dependency manifest/lockfile (package.json, package-lock.json, or equivalent) pinning the required @openai/codex CLI/runtime.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 556
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0012
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0013
ACTION: add_rule
RULE_TEXT: tools/meta_loop.py stops when tools/loop.py returns blocked/non-zero, so the meta-loop never performs system evolution on the primary failure path it is supposed to recover.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 562
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0013
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0014
ACTION: add_rule
RULE_TEXT: tools/select_survivor.py: uses p(...) but never imports p from tools/common.py.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 565
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0014
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0015
ACTION: add_rule
RULE_TEXT: PLAN_GRAPH_SCHEMA.md defines validator_set, but tools/validate_all.py never reads node schema and hardcodes validators.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 572
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0015
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0016
ACTION: add_rule
RULE_TEXT: tools/planner.py does not validate generated plan graphs against PLAN_GRAPH_SCHEMA.md; it only checks that nodes is non-empty.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 573
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0016
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0017
ACTION: add_rule
RULE_TEXT: EXTERNAL_METRICS.md says default behavior without hook config is SKIP; tools/external_metrics.py implements no SKIP/disable path and always runs a built-in metric.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 576
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0017
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0018
ACTION: add_rule
RULE_TEXT: STATE.json.current_node_id is declared but never written by tools/loop.py or tools/commit_state.py.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 584
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0018
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0019
ACTION: add_rule
RULE_TEXT: ARTIFACT_CONTRACT.md requires exact section order and no freeform preamble, but tools/validate_format.py checks only token presence, a few empties, and length.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 588
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0019
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0020
ACTION: add_rule
RULE_TEXT: ARTIFACT_CONTRACT.md marks many metadata fields as required, but validators do not enforce non-empty ARTIFACT_CLASS, GOAL_REF, PLAN_NODE_REF, STATE_REF, and related metadata; tools/commit_artifact.py only fills a subset.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 589
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0020
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0021
ACTION: add_rule
RULE_TEXT: tools/meta_loop.py evolves only after a successful artifact loop; when tools/loop.py returns blocked/non-zero, meta-loop exits instead of invoking system evolution.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 598
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0021
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0022
ACTION: add_rule
RULE_TEXT: tools/build_node_context.py truncates upstream artifacts to 3000 chars and emits a raw dump instead of the structured dependency summary required by HANDOFF_POLICY.md.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 608
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0022
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0023
ACTION: add_rule
RULE_TEXT: tools/retire_candidates.py cannot execute, so the normal post-survivor retirement path is broken.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 613
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0023
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0024
ACTION: add_rule
RULE_TEXT: tools/cluster_candidates.py only logs clusters; cluster/family outputs are not consumed by survivor selection or pruning.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 614
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0024
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0025
ACTION: add_rule
RULE_TEXT: Candidate files are never cleared between runs; stale candidates and stale judge/score/family sidecars remain eligible for later selection.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 617
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0025
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0026
ACTION: add_rule
RULE_TEXT: tools/branch_controller.py uses only global plateau_counter >= 2; it does not implement the full branch-trigger conditions documented in BRANCH_POLICY.md.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 623
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0026
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0027
ACTION: add_rule
RULE_TEXT: VALIDATION_GATE.md says every check object must contain name, status, code, and details, but all validator PASS checks omit code.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 642
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0027
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0028
ACTION: add_rule
RULE_TEXT: STATE.json.current_node_id is never maintained by runtime code, despite multi-node execution and node-context generation.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 650
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0028
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0029
ACTION: add_rule
RULE_TEXT: tools/validate_format.py does not check non-empty values for several required contract fields:
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 652
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0029
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0030
ACTION: add_rule
RULE_TEXT: tools/build_node_context.py does not emit dependency artifact IDs, reusable outputs, or unresolved downstream-relevant risks as required by HANDOFF_POLICY.md.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 664
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0030
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0031
ACTION: add_rule
RULE_TEXT: tools/cluster_candidates.py and family summaries are history-only; pruning and survivor selection do not consume cluster/family data despite BRANCH_POLICY.md and CANDIDATE_FAMILIES.md.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 669
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0031
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0032
ACTION: add_rule
RULE_TEXT: EXTERNAL_METRICS.md says “no hook config => SKIP” and allows missing external metrics only when explicitly disabled, but no hook-config or disable mechanism exists and tools/external_metrics.py never emits SKIP.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 673
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0032
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0033
ACTION: add_rule
RULE_TEXT: Add-on package instructions introduce python tools/meta_loop.py as a top-level runner, but the canonical command docs were never updated to include it.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 690
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0033
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0034
ACTION: add_rule
RULE_TEXT: STATE.json.last_failure_code is never updated anywhere, so failure-family triggers in FAILURE_ACTION_MAP.md / BRANCH_POLICY.md have no persisted source of truth.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 701
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0034
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0035
ACTION: add_rule
RULE_TEXT: STATE.json.current_node_id is never updated during node execution.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 702
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0035
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0036
ACTION: add_rule
RULE_TEXT: tools/validate_all.py ignores node validator_set and always runs a hardcoded validator trio.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 708
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0036
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0037
ACTION: add_rule
RULE_TEXT: tools/validate_format.py does not enforce the exact ARTIFACT_CONTRACT.md structure: it ignores section order, boundary --- markers, the no-extra-sections rule, and emptiness of most required metadata fields.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 709
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0037
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0038
ACTION: add_rule
RULE_TEXT: In all provided meta_loop.py variants, plateau handling occurs only after a successful tools/loop.py run; if tools/loop.py exits blocked/nonzero, the meta-loop breaks before evolution can run.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 714
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0038
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0039
ACTION: add_rule
RULE_TEXT: tools/branch_controller.py ignores node-specific max_branches, plateau-escalation caps, repair-count triggers, and failure-family triggers; it keys only off a shared plateau_counter.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 729
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0039
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0040
ACTION: add_rule
RULE_TEXT: tools/cluster_candidates.py and family summaries are recorded but never enforced in selection/pruning; near-duplicate pruning and family-aware survivor choice are absent.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 730
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0040
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0041
ACTION: add_rule
RULE_TEXT: The repo claims multi-node execution, candidate families, retirement policy, external hooks, and meta-loop control, but several of those systems are only documented or partially recorded, not fully enforced in code.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 736
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0041
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0042
ACTION: add_rule
RULE_TEXT: tools/select_survivor.py calls p(...) inside the diversity check but never imports p from common.py; when more than one survivor exists, this raises NameError.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 750
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0042
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0043
ACTION: add_rule
RULE_TEXT: EXTERNAL_METRICS.md defines a SKIP path when no hook config exists, but tools/external_metrics.py has no hook-config/disable mechanism and never implements that documented default.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 762
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0043
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0044
ACTION: add_rule
RULE_TEXT: STATE.current_node_id exists but is never maintained by tools/loop.py, so node-state tracking is incomplete.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 767
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0044
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0045
ACTION: add_rule
RULE_TEXT: ARTIFACT_CONTRACT.md requires exact section order, no extra sections, no preamble outside schema, and no empty required fields; tools/validate_format.py does not enforce order, boundary markers, extra sections, or emptiness of most metadata fields.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 770
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0045
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0046
ACTION: add_rule
RULE_TEXT: tools/score_artifact.py --has-downstream can fail on handoff_not_ready, but the artifact contract has no required handoff field or token set.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 774
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0046
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0047
ACTION: add_rule
RULE_TEXT: In all provided meta-loop variants, plateau-based system evolution is checked only after tools/loop.py returns success; if tools/loop.py exits non-zero on blockage/plateau, meta-loop breaks before any system evolution occurs.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 779
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0047
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0048
ACTION: add_rule
RULE_TEXT: REPO_LOCK.json protects only a subset of the actual runtime core; final runtime-critical files such as tools/score_artifact.py, tools/external_metrics.py, tools/build_node_context.py, tools/select_survivor.py, tools/retire_candidates.py, and tools/commit_state.py are outside runtime_core.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 782
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0048
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0049
ACTION: add_rule
RULE_TEXT: BASELINE_REGISTRY.json is global rather than per-node, so it cannot serve as a reliable handoff source for multi-node graphs.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 788
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0049
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0050
ACTION: add_rule
RULE_TEXT: tools/cluster_candidates.py and candidate family summaries are write-only; tools/select_survivor.py and tools/branch_controller.py do not consume their outputs.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 792
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0050
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER3_REPO매핑.md::OP0051
ACTION: add_rule
RULE_TEXT: tools/branch_controller.py never reads BRANCH_POLICY.md or node-level branch_policy; documented caps (max alive candidates, max plateau escalations, max_branches) are not enforced.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 793
BLOCK_ID: CHECKLIST_LAYER3_REPO매핑_B0051
RATIONALE: no strong canonical overlap
