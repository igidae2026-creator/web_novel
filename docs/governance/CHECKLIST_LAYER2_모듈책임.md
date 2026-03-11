MetaOS 층 2 체크리스트 정본
Module Checklist
0. 층 2의 목적
층 2의 목적은 MetaOS의 목표 조건들을 구현 모듈 단위의 책임으로 분해하고, 각 책임이 실제 repo에서 존재하고 작동하는지를 판정 가능하게 만드는 것이다. 
즉 층 2는
추상 목표 → 구현 책임 → 체크 가능한 모듈 상태 
로 내리는 층이다.
1. Goal / Objective Module
역할
무엇을 최적화할지 고정하고, generic floor와 domain target을 분리하며, 단발 hit가 아니라 stable production 목표를 정의한다. 
체크리스트
[ ] GOAL.md가 존재한다 [ ] SYSTEM_OBJECTIVE.md 또는 동등한 상위 목적 정의가 있다 [ ] 목표가 “좋은 결과 하나”가 아니라 “지속적 생산”으로 정의되어 있다 [ ] generic competence floor와 domain target이 분리되어 있다 [ ] usable 정의가 generic floor + domain objective로 명시되어 있다 [ ] domain target percentile 또는 경쟁 기준이 명시되어 있다 [ ] production quality 목표 P(artifact ∈ target-tier)가 정의되어 있다 
FAIL 조건
[ ] 목표가 단발 artifact 생성으로만 정의된다 [ ] generic과 domain 목표가 섞여 있다 [ ] stable production 목표가 없다 
2. Artifact Generation Module
역할
artifact를 실제 생성하고, contract / node / candidate / context를 반영해 실질 내용을 만든다. 
체크리스트
[ ] codex_worker.py 또는 동등한 생성 모듈이 존재한다 [ ] artifact contract를 읽는다 [ ] node 정보를 반영한다 [ ] candidate 정보를 반영한다 [ ] upstream context / handoff를 반영한다 [ ] 기존 artifact가 있으면 patch mode로 동작한다 [ ] 단순 형식 채우기가 아니라 실질 내용 생성을 지시한다 [ ] stable production을 위한 재생성 가능성이 있다 
FAIL 조건
[ ] 템플릿 채우기 수준에 머문다 [ ] node/candidate/context를 무시한다 [ ] 항상 블라인드 rewrite만 수행한다 
3. Semantic Validation Module
역할
artifact competence floor를 시스템 속성으로 강제한다. 
체크리스트
[ ] format validator가 있다 [ ] semantic validator가 있다 [ ] semantic validator가 depth를 검사한다 [ ] semantic validator가 actionability를 검사한다 [ ] semantic validator가 specificity를 검사한다 [ ] semantic validator가 recommendation quality를 검사한다 [ ] “내용 있음”과 “쓸만함”을 구분한다 [ ] generic competence floor를 검사한다 [ ] domain objective relevance를 검사한다 
FAIL 조건
[ ] 형식만 검사한다 [ ] 길이만 검사한다 [ ] 의미/실질성을 전혀 보지 않는다 
4. Repair Policy Module
역할
실패 원인별 targeted patch를 수행해 artifact competence floor와 quality gradient를 높인다. 
체크리스트
[ ] repair_artifact.py 또는 동등한 모듈이 있다 [ ] validator failure code를 읽는다 [ ] judge critique를 읽는다 [ ] weakest axis를 읽는다 [ ] failure code별 repair strategy가 존재한다 [ ] repair가 추상적 요청이 아니라 targeted patch다 [ ] repair 후 재검증 경로가 있다 [ ] repair 후 점수 비교가 가능하다 [ ] repair가 competence floor를 실제로 올리도록 설계되어 있다 
FAIL 조건
[ ] “좋게 고쳐라” 수준의 추상 지시만 있다 [ ] failure family를 반영하지 않는다 [ ] repair 후 재평가가 없다 
5. Quality Scoring Module
역할
Q를 수치화하고, generic quality / domain performance / trend를 추적한다. 
체크리스트
[ ] judge_artifact.py가 존재한다 [ ] score_artifact.py가 존재한다 [ ] generic quality score가 존재한다 [ ] domain performance score가 존재하거나 대체 proxy가 존재한다 [ ] total Q 산식이 정의되어 있다 [ ] score history가 저장된다 [ ] weakest axis가 기록된다 [ ] variance 추적이 가능하다 [ ] production quality 추적이 가능하다 
FAIL 조건
[ ] score가 단일 감각 점수뿐이다 [ ] generic/domain 구분이 없다 [ ] history가 저장되지 않는다 
6. Acceptance Gate Module
역할
무엇이 채택되는지 완전히 닫힌 규칙으로 결정한다. 
체크리스트
[ ] validate_all PASS가 필수다 [ ] judge PASS가 필수다 [ ] rule score PASS가 필수다 [ ] external metric PASS/SKIP가 필수다 [ ] survivor selection PASS가 필수다 [ ] 하나라도 실패하면 commit 불가다 [ ] acceptance gate가 문서와 코드에서 일치한다 [ ] repair 후 다시 gate 전부를 통과해야 한다 
FAIL 조건
[ ] 일부 gate를 우회해 commit 가능하다 [ ] 문서와 runtime gate가 다르다 [ ] survivor가 validation보다 먼저 채택될 수 있다 
7. State Persistence Module
역할
이번 iteration 결과를 다음 iteration과 다음 node에 보존한다. 
체크리스트
[ ] STATE.json이 존재한다 [ ] METRICS.json이 존재한다 [ ] history가 append-only로 관리된다 [ ] accepted artifact id가 저장된다 [ ] node별 accepted artifact mapping이 존재한다 [ ] baseline lineage가 저장된다 [ ] candidate score history가 저장된다 [ ] planner가 execution state를 덮어쓰지 않는다 [ ] 개선 결과가 다음 iteration에 보존된다 
FAIL 조건
[ ] accepted 결과가 다음 실행에서 사라진다 [ ] node별 상태를 보존하지 못한다 [ ] planner가 상태를 덮어쓴다 
8. Planning / Graph Module
역할
문제를 node 구조로 분해하고, dependency-safe execution을 관리한다. 
체크리스트
[ ] planner.py가 존재한다 [ ] GOAL → GOAL_SPEC 변환이 존재한다 [ ] PLAN_GRAPH.json이 존재한다 [ ] PLAN_GRAPH_SCHEMA.md가 존재한다 [ ] graph가 dependency-safe하다 [ ] node ordering이 가능하다 [ ] plan graph와 execution state가 충돌하지 않는다 [ ] planner가 accepted node 상태를 보존하거나 존중한다 
FAIL 조건
[ ] planner가 매번 graph를 무조건 덮어쓴다 [ ] node dependency를 실제 runtime이 무시한다 [ ] graph schema가 코드와 분리되어 있다 
9. Handoff Module
역할
upstream accepted artifact를 downstream에 안정적으로 전달한다. 
체크리스트
[ ] build_node_context.py 또는 동등한 handoff 모듈이 있다 [ ] upstream accepted artifact 기준으로 handoff한다 [ ] workspace draft와 committed baseline을 구분한다 [ ] raw dump가 아니라 summary를 제공한다 [ ] reusable outputs가 포함된다 [ ] unresolved risks가 포함된다 [ ] dependency artifact id/path가 포함된다 [ ] downstream prompt가 handoff context를 실제로 사용한다 
FAIL 조건
[ ] workspace draft를 그대로 넘긴다 [ ] accepted artifact 기준이 아니다 [ ] raw text 복사 수준이다 
10. Meta Evolution Module
역할
artifact가 아니라 시스템 구조 자체를 개선한다. 
체크리스트
[ ] meta_loop.py가 존재한다 [ ] system_evolver.py가 존재한다 [ ] plateau 또는 root-cause가 trigger가 된다 [ ] repo mutation이 실제로 가능하다 [ ] system mutation이 artifact loop와 분리되어 있다 [ ] system mutation 이후 다음 iteration에 반영된다 [ ] meta improvement와 artifact improvement가 구분된다 
FAIL 조건
[ ] meta loop가 artifact loop 실패 시 그냥 종료한다 [ ] system evolution이 수동 개입 없이는 안 돈다 [ ] 구조 개선이 아닌 임시 patch만 한다 
11. Mutation Governance Module
역할
자기개선이 시스템을 망치지 않도록 mutation 권한을 제한하고 통제한다. 
체크리스트
[ ] PATCH_PROTOCOL.md가 존재한다 [ ] REPO_LOCK.json이 존재한다 [ ] mutation allowed path가 정의되어 있다 [ ] immutable dirs가 정의되어 있다 [ ] runtime이 PATCH_PROTOCOL을 실제로 읽는다 [ ] runtime이 REPO_LOCK를 실제로 읽는다 [ ] mutation allowed target만 수정 가능하다 [ ] immutable target은 실제 보호된다 
FAIL 조건
[ ] 문서만 있고 runtime enforcement가 없다 [ ] Codex가 아무 파일이나 수정할 수 있다 [ ] immutable dir가 실제로 보호되지 않는다 
12. Post-Patch Verification Module
역할
패치 후 시스템이 살아 있는지 검증하고, 실패 시 reject 또는 rollback한다. 
체크리스트
[ ] import check가 있다 [ ] CLI interface check가 있다 [ ] schema validation이 있다 [ ] dry run validation이 있다 [ ] patch 이후 end-to-end smoke test가 있다 [ ] 실패 시 patch reject가 가능하다 [ ] 실패 시 rollback 또는 restore가 가능하다 [ ] post-patch verification 없이는 patch adopt가 불가하다 
FAIL 조건
[ ] 패치만 하고 생존 확인이 없다 [ ] 실패 patch도 다음 iteration에 남는다 
13. Branch / Exploration Module
역할
local optimum escape와 explore / exploit 균형을 담당한다. 
체크리스트
[ ] branch_controller.py가 존재한다 [ ] select_survivor.py가 존재한다 [ ] candidate clustering/diversity 처리가 존재한다 [ ] exploration budget이 존재한다 [ ] max branches가 제한된다 [ ] plateau 시 exploration pressure가 증가한다 [ ] exploitation 단계가 존재한다 [ ] branch domination 패턴이 기록된다 
FAIL 조건
[ ] branch explosion 통제가 없다 [ ] explore / exploit 균형이 없다 [ ] diversity 처리가 selection에 반영되지 않는다 
14. Objective / Representation Mutation Module
역할
상한을 밀기 위해 문제 정의와 표현 자체를 바꾼다. 
체크리스트
[ ] objective mutation 경로가 존재한다 [ ] goal definition을 재해석/확장할 수 있다 [ ] objective mutation은 validator와 충돌하지 않는다 [ ] objective 변경 기록이 남는다 [ ] objective mutation 실패 시 rollback된다 [ ] representation mutation 경로가 존재한다 [ ] artifact schema / format / decomposition을 바꿀 수 있다 [ ] representation mutation 시 validator도 갱신된다 [ ] 새로운 representation이 search space를 확장한다 [ ] representation mutation 실패 시 기존 representation 유지가 가능하다 
FAIL 조건
[ ] 항상 고정된 goal만 최적화한다 [ ] 항상 고정된 artifact schema만 사용한다 
15. Module Checklist 판정 기준
PASS
[ ] 각 핵심 목표 조건이 명확한 모듈 책임으로 매핑된다 [ ] 각 모듈이 실제 repo에서 존재하고 작동한다 [ ] 모듈 간 연결이 닫혀 있다 
WEAK
[ ] 모듈은 존재하지만 역할이 불완전하다 [ ] 문서상 역할과 runtime 역할이 다르다 [ ] 일부는 model competence에 과도하게 의존한다 
FAIL
[ ] 목표 조건을 담당하는 핵심 모듈이 없다 [ ] 모듈이 있어도 실행 체인에 연결되지 않는다 [ ] self-improving closure가 모듈 레벨에서 성립하지 않는다


## APPEND_ONLY_PATCH_BLOCKS

TARGET_DOC: CHECKLIST_LAYER2_모듈책임.md
BLOCK_COUNT: 27

BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0001
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 67
RULE_TEXT: All internal execution must be governed by METAOS runtime rules.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0002
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 71
RULE_TEXT: Unsafe system mutations that compromise autonomy, persistence, or invariants must be rejected.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0003
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 6
RULE_TEXT: The runtime must operate continuously without requiring human intervention.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0004
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 7
RULE_TEXT: All runtime operations must preserve the constitutional invariants defined in Layer 1.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0005
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 12
RULE_TEXT: The runtime loop must never terminate while the system is active.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0006
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 72
RULE_TEXT: Mutation must maintain exploration diversity.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0007
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 73
RULE_TEXT: Mutation must not violate system invariants.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0008
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 84
RULE_TEXT: METAOS runtime state must be derived from event history.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0009
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 126
RULE_TEXT: The runtime must maintain stability while exploring.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0010
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 132
RULE_TEXT: Safety checks must prevent runtime collapse.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0011
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 134
RULE_TEXT: METAOS must persist runtime knowledge.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0012
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 144
RULE_TEXT: METAOS must support runtime restart.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0013
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 150
RULE_TEXT: Runtime pauses may occur, but the evolutionary process must remain resumable.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0014
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 155
RULE_TEXT: Runtime processes must obey constitutional invariants.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0015
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 156
RULE_TEXT: Runtime components must not modify artifact history, violate append-only truth, or bypass evaluation mechanisms.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0016
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 14
RULE_TEXT: External systems may interact with METAOS but cannot override METAOS constitutional principles or runtime rules.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0017
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 24
RULE_TEXT: The kernel cannot be bypassed by runtime components.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0018
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 34
RULE_TEXT: All runtime operations must pass governance authorization.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0019
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 50
RULE_TEXT: System mutation must be governed.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0020
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 56
RULE_TEXT: All mutations must pass validation before execution.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0021
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 57
RULE_TEXT: Unsafe mutations must be rejected.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0022
ACTION: add_rule
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 101
RULE_TEXT: External systems must not gain direct control over METAOS runtime.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0023
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 18
RULE_TEXT: Must produce a validator-ready artifact
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0024
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 135
RULE_TEXT: critique must be concrete and repair-oriented
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0025
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 331
RULE_TEXT: survivor selection should prefer the strongest family representative when collapse occurs
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0026
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 407
RULE_TEXT: validator authority must remain intact
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0027
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 649
RULE_TEXT: External-metric results are only written to global metrics history; there is no candidate-scoped persisted external-metric record for survivor selection or commit gating.
RATIONALE: no strong canonical overlap


## APPLY_QUEUE_OPERATIONS

TARGET_DOC: CHECKLIST_LAYER2_모듈책임.md
TOTAL_OPS: 27

OP_ID: CHECKLIST_LAYER2_모듈책임.md::OP0001
ACTION: add_rule
RULE_TEXT: All internal execution must be governed by METAOS runtime rules.
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 67
BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0001
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER2_모듈책임.md::OP0002
ACTION: add_rule
RULE_TEXT: Unsafe system mutations that compromise autonomy, persistence, or invariants must be rejected.
SOURCE_CLASS: seed
SOURCE_FILE: Layer1.txt
SOURCE_LINE: 71
BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0002
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER2_모듈책임.md::OP0003
ACTION: add_rule
RULE_TEXT: The runtime must operate continuously without requiring human intervention.
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 6
BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0003
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER2_모듈책임.md::OP0004
ACTION: add_rule
RULE_TEXT: All runtime operations must preserve the constitutional invariants defined in Layer 1.
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 7
BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0004
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER2_모듈책임.md::OP0005
ACTION: add_rule
RULE_TEXT: The runtime loop must never terminate while the system is active.
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 12
BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0005
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER2_모듈책임.md::OP0006
ACTION: add_rule
RULE_TEXT: Mutation must maintain exploration diversity.
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 72
BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0006
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER2_모듈책임.md::OP0007
ACTION: add_rule
RULE_TEXT: Mutation must not violate system invariants.
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 73
BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0007
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER2_모듈책임.md::OP0008
ACTION: add_rule
RULE_TEXT: METAOS runtime state must be derived from event history.
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 84
BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0008
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER2_모듈책임.md::OP0009
ACTION: add_rule
RULE_TEXT: The runtime must maintain stability while exploring.
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 126
BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0009
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER2_모듈책임.md::OP0010
ACTION: add_rule
RULE_TEXT: Safety checks must prevent runtime collapse.
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 132
BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0010
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER2_모듈책임.md::OP0011
ACTION: add_rule
RULE_TEXT: METAOS must persist runtime knowledge.
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 134
BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0011
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER2_모듈책임.md::OP0012
ACTION: add_rule
RULE_TEXT: METAOS must support runtime restart.
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 144
BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0012
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER2_모듈책임.md::OP0013
ACTION: add_rule
RULE_TEXT: Runtime pauses may occur, but the evolutionary process must remain resumable.
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 150
BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0013
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER2_모듈책임.md::OP0014
ACTION: add_rule
RULE_TEXT: Runtime processes must obey constitutional invariants.
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 155
BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0014
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER2_모듈책임.md::OP0015
ACTION: add_rule
RULE_TEXT: Runtime components must not modify artifact history, violate append-only truth, or bypass evaluation mechanisms.
SOURCE_CLASS: seed
SOURCE_FILE: Layer2.txt
SOURCE_LINE: 156
BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0015
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER2_모듈책임.md::OP0016
ACTION: add_rule
RULE_TEXT: External systems may interact with METAOS but cannot override METAOS constitutional principles or runtime rules.
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 14
BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0016
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER2_모듈책임.md::OP0017
ACTION: add_rule
RULE_TEXT: The kernel cannot be bypassed by runtime components.
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 24
BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0017
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER2_모듈책임.md::OP0018
ACTION: add_rule
RULE_TEXT: All runtime operations must pass governance authorization.
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 34
BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0018
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER2_모듈책임.md::OP0019
ACTION: add_rule
RULE_TEXT: System mutation must be governed.
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 50
BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0019
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER2_모듈책임.md::OP0020
ACTION: add_rule
RULE_TEXT: All mutations must pass validation before execution.
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 56
BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0020
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER2_모듈책임.md::OP0021
ACTION: add_rule
RULE_TEXT: Unsafe mutations must be rejected.
SOURCE_CLASS: seed
SOURCE_FILE: Layer3.txt
SOURCE_LINE: 57
BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0021
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER2_모듈책임.md::OP0022
ACTION: add_rule
RULE_TEXT: External systems must not gain direct control over METAOS runtime.
SOURCE_CLASS: seed
SOURCE_FILE: Layer5.txt
SOURCE_LINE: 101
BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0022
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER2_모듈책임.md::OP0023
ACTION: add_rule
RULE_TEXT: Must produce a validator-ready artifact
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 18
BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0023
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER2_모듈책임.md::OP0024
ACTION: add_rule
RULE_TEXT: critique must be concrete and repair-oriented
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 135
BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0024
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER2_모듈책임.md::OP0025
ACTION: add_rule
RULE_TEXT: survivor selection should prefer the strongest family representative when collapse occurs
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 331
BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0025
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER2_모듈책임.md::OP0026
ACTION: add_rule
RULE_TEXT: validator authority must remain intact
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 407
BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0026
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER2_모듈책임.md::OP0027
ACTION: add_rule
RULE_TEXT: External-metric results are only written to global metrics history; there is no candidate-scoped persisted external-metric record for survivor selection or commit gating.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 649
BLOCK_ID: CHECKLIST_LAYER2_모듈책임_B0027
RATIONALE: no strong canonical overlap
