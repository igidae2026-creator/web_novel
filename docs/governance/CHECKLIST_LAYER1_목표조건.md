MetaOS Layer 1 체크리스트 정본
0. Layer 1의 목적
Layer 1의 목적은 artifact가 단순히 생성되는 것이 아니라, 일반적 읽기 가능성을 넘어서 목표 도메인에서 최소 경쟁력을 갖춘 결과로 안정적으로 생산되게 만드는 것이다. 
즉 Layer 1은
좋아 보이는 artifact 1개 
가 아니라
쓸만한 artifact를 안정적으로 만들어내는 최소 바닥 
이다.
1. Layer 1 목표 정의
[ ] Layer 1의 목표는 artifact competence floor다 [ ] artifact competence floor는 system property여야 한다 [ ] artifact competence floor는 model side-effect여서는 안 된다 [ ] 목표는 단발 hit가 아니라 stable production이다 
2. “쓸만하다”의 정의
[ ] “쓸만하다”를 generic quality로만 정의하지 않았다 [ ] “쓸만하다”를 domain competitive quality까지 포함해 정의했다 [ ] usable artifact = generic competence floor + domain objective pass 로 정의했다 [ ] generic floor와 domain target을 분리했다 
기준식
usable = generic_floor_pass AND domain_objective_pass 
예시
generic_score ≥ 0.75 AND domain_score ≥ target percentile 
3. 생산 목표 정의
[ ] 목표는 좋은 artifact 하나가 아니다 [ ] 목표는 좋은 artifact를 안정적으로 생산하는 시스템이다 [ ] stable production 관점이 명시되어 있다 [ ] production quality를 추적한다 
예시
P(artifact ∈ target-tier) ≥ threshold 
예:
P(artifact ∈ top 5%) ≥ 0.3 
4. Generic Competence Floor 체크
[ ] artifact가 형식만 맞는 수준을 넘는다 [ ] artifact가 읽을 수 있다 [ ] artifact가 논리적으로 이어진다 [ ] artifact가 구조를 가진다 [ ] artifact가 최소한 coherence를 가진다 [ ] artifact가 완전히 비어 있지 않다 
Generic floor 예시 항목
[ ] grammar / readability [ ] structure / organization [ ] coherence / consistency [ ] basic reasoning continuity 
5. Domain Competence Floor 체크
[ ] artifact가 목표 도메인 경쟁 기준을 가진다 [ ] domain success criterion이 명시되어 있다 [ ] artifact가 그 기준을 향해 최적화된다 [ ] domain score가 generic score보다 상위 목표임이 명시되어 있다 
도메인 예시
[ ] 국내 웹소설 플랫폼 장르별 top 5% [ ] 단순 읽기 가능이 아니라 실제 경쟁력 있는 작품 [ ] single hit가 아니라 top-tier 수준의 지속 생산 
6. 핵심 섹션 실질성 체크
[ ] Recommended Direction이 구체적이다 [ ] Risks가 실제 리스크다 [ ] Next Actions가 실행 가능하다 [ ] 핵심 섹션이 상투적 문장으로만 채워지지 않는다 [ ] 내용이 “있다”와 “의미 있다”가 구분된다 
실패 예시
Recommended Direction: - continue research Next Actions: - improve artifact 
이런 건 Layer 1 PASS가 아니다.
7. Semantic Competence 보장 체크
[ ] semantic validator가 존재한다 [ ] semantic validator가 depth를 검사한다 [ ] semantic validator가 actionability를 검사한다 [ ] semantic validator가 specificity를 검사한다 [ ] semantic validator가 recommendation quality를 검사한다 [ ] semantic validator가 “내용 있음”과 “쓸만함”을 구분한다 
8. Repair가 실제 Layer 1을 올리는지 체크
[ ] repair는 추상적 요청이 아니다 [ ] repair는 failure code 기반 targeted patch다 [ ] repair는 weakest area를 구조적으로 보완한다 [ ] repair 후 재검증이 있다 [ ] repair 후 실제 품질 상승 여부를 측정한다 [ ] repair가 competence floor를 올리도록 설계되어 있다 
9. Layer 1의 측정 가능성 체크
[ ] generic competence score가 있다 [ ] domain performance score가 있다 [ ] 두 점수를 분리해서 기록한다 [ ] usable 판정 기준이 수치 또는 명시 규칙으로 존재한다 [ ] “쓸만하다”가 감각적 표현으로만 남아 있지 않다 
권장 수식
Q = w1 * generic_quality + w2 * domain_score w1 < w2 
10. Layer 1 PASS 조건
다음이 모두 충족되어야 한다.
[ ] artifact가 형식 이상이다 [ ] artifact가 generic competence floor를 넘는다 [ ] artifact가 domain objective를 향해 경쟁력을 가진다 [ ] 핵심 섹션이 실질적으로 채워진다 [ ] semantic validator가 이를 강제한다 [ ] repair가 실제 competence floor를 높인다 [ ] artifact quality가 model 운에만 의존하지 않는다 [ ] stable production 관점이 유지된다 
11. Layer 1 FAIL 조건
아래 중 하나라도 성립하면 Layer 1 FAIL로 본다.
[ ] artifact가 형식 채우기에 가깝다 [ ] 내용은 있으나 의미가 약하다 [ ] 핵심 섹션이 상투적이다 [ ] generic quality만 있고 domain 경쟁력이 없다 [ ] semantic validator가 없다 [ ] repair가 실제로 품질을 못 올린다 [ ] artifact competence가 system property가 아니라 model side-effect다 [ ] 좋은 결과가 단발적으로만 나온다 
12. Layer 1 최종 판정 블록
PASS
[ ] Layer 1 PASS artifact competence floor is a system property and stable production of usable artifacts is achievable 
WEAK
[ ] Layer 1 WEAK artifact competence exists only partially and remains unstable or model-dependent 
FAIL
[ ] Layer 1 FAIL artifact quality is not system-guaranteed and usable output is not reliably producible 
초압축 Layer 1 체크리스트
매번 빠르게 볼 때는 이것만 보면 된다.
[ ] artifact가 형식 채우기를 넘는가 [ ] artifact가 generic competence floor를 넘는가 [ ] artifact가 domain 경쟁력을 가지는가 [ ] semantic validator가 이를 강제하는가 [ ] repair가 실제 competence floor를 올리는가 [ ] 좋은 결과가 단발이 아니라 안정적으로 생산되는가 
Layer 1 핵심 문장
Layer 1의 목표는 좋아 보이는 artifact 하나를 얻는 것이 아니라, generic competence floor와 domain competitive performance를 동시에 만족하는 artifact를 안정적으로 생산 가능한 수준까지 system property로 만드는 것이다.


## APPEND_ONLY_PATCH_BLOCKS

TARGET_DOC: CHECKLIST_LAYER1_목표조건.md
BLOCK_COUNT: 2

BLOCK_ID: CHECKLIST_LAYER1_목표조건_B0001
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 12
RULE_TEXT: Human provides only the goal and optional constraints.
RATIONALE: no strong canonical overlap

BLOCK_ID: CHECKLIST_LAYER1_목표조건_B0002
ACTION: add_rule
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 131
RULE_TEXT: objective should be explicit and direct
RATIONALE: no strong canonical overlap


## APPLY_QUEUE_OPERATIONS

TARGET_DOC: CHECKLIST_LAYER1_목표조건.md
TOTAL_OPS: 2

OP_ID: CHECKLIST_LAYER1_목표조건.md::OP0001
ACTION: add_rule
RULE_TEXT: Human provides only the goal and optional constraints.
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 12
BLOCK_ID: CHECKLIST_LAYER1_목표조건_B0001
RATIONALE: no strong canonical overlap

OP_ID: CHECKLIST_LAYER1_목표조건.md::OP0002
ACTION: add_rule
RULE_TEXT: objective should be explicit and direct
SOURCE_CLASS: reference
SOURCE_FILE: 참고자료.md
SOURCE_LINE: 131
BLOCK_ID: CHECKLIST_LAYER1_목표조건_B0002
RATIONALE: no strong canonical overlap
