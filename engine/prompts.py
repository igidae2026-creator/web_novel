from .strategy import PLATFORM_STRATEGY, pick_subengine, list_subengines
from .style import constraints_text, StyleVector
from .profile import profile_constraints_text

class PROMPTS:
    @staticmethod
    def master_outline(cfg: dict, ext_snapshot: dict, sub_engine_key: str) -> str:
        pj = cfg["project"]
        nv = cfg["novel"]
        q = cfg["quality"]
        plat = PLATFORM_STRATEGY.get(pj["platform"], {})
        bucket = pj["genre_bucket"]
        sub = pick_subengine(bucket, sub_engine_key)

        return f"""한국 웹소설 장편(연재) 아웃라인을 작성하라.

플랫폼: {pj['platform']}
장르 버킷: {bucket}
세부 엔진: {sub.label} ({sub.key}) — {sub.brief}
총 회차: {nv['total_episodes']}

플랫폼 전략 규칙:
- 페이싱: {plat.get('pacing','balanced')}
- 후킹 규칙: {plat.get('hook_rule','')}
- 유료 구간 규칙: {plat.get('paywall_rule','')}

품질 목표(0~1):
- hook_score >= {q['hook_score_min']}
- paywall_score >= {q['paywall_score_min']}
- emotion_density >= {q['emotion_density_min']}
- repetition_score <= {q['repetition_max']}
- escalation >= {q['escalation_min']}

외부 랭킹 관측치(있으면 반영):
{ext_snapshot}

출력(한국어, 구체적으로):
1) 로그라인 1문장
2) 세계 규칙/시스템/핵심 제약
3) 주인공/적대자/조력자/라이벌(각 2~3문장)
4) 1~3화: 씬 단위 비트(각 씬: 목표/갈등/감정 변곡/훅)
5) 20~30화: 유료 전환 폭발 아크 비트(필수)
6) 50화마다 아크 리셋 지점(총 {nv['total_episodes']//50}개 이상)
7) 최종 결말과 마지막 갈등 해결
불필요한 설명 금지. 사건/갈등/보상을 명확히.
"""

    @staticmethod
    def episode_plan(cfg: dict, outline: str, ep: int, knobs: dict, ext_snapshot: dict, fatigue_directive: str, sub_engine_key: str, story_state: dict | None = None) -> str:
        pj = cfg["project"]
        nv = cfg["novel"]
        plat = PLATFORM_STRATEGY.get(pj["platform"], {})
        bucket = pj["genre_bucket"]
        sub = pick_subengine(bucket, sub_engine_key)
        return f"""에피소드 {ep}/{nv['total_episodes']}의 씬 플랜을 작성하라.

플랫폼: {pj['platform']} (페이싱 {plat.get('pacing','balanced')})
장르: {bucket} / 세부 엔진: {sub.label} ({sub.key})

현재 노브(knobs):
{knobs}

캐릭터 상태:
{(story_state or {}).get('character', {})}

갈등 상태:
{(story_state or {}).get('conflict', {})}

이벤트 계획:
{(story_state or {}).get('event', {})}

클리프행어 계획:
{(story_state or {}).get('cliffhanger', {})}

텐션 파형:
{(story_state or {}).get('tension', {})}

리텐션 압력:
{(story_state or {}).get('retention', {})}

적대자 장기 계획:
{(story_state or {}).get('antagonist', {})}

패턴 메모리:
{(story_state or {}).get('pattern_memory', {})}

시장/연재 상태:
{(story_state or {}).get('market', {})}

외부 랭킹 관측치:
{ext_snapshot}

피로도 지시:
{fatigue_directive}

아웃라인:
{outline}

출력(한국어):
- 씬 5~12개
- 각 씬: 목표/갈등/감정 변곡/전개/마무리 훅
- 회차 전체 감정 변곡 3회 이상
- 이전 회차 대비 갈등 단계 상승
- 주인공의 욕망/공포/약점이 선택과 손실에 직접 반영되어야 함
- 적대자의 다음 수와 장기 의도가 씬 전개에 드러나야 함
- 최근 과사용 패턴을 반복하지 말고 변주를 만들 것
- 플랫폼 페이싱, 유료구간 압력, 독자 신뢰를 해치지 않도록 연재형 보상 구조를 유지할 것
"""

    @staticmethod
    def episode_draft_json(cfg: dict, plan: str, ep: int, knobs: dict, style: StyleVector, sub_engine_key: str, story_state: dict | None = None) -> str:
        pj = cfg["project"]
        nv = cfg["novel"]
        plat = PLATFORM_STRATEGY.get(pj["platform"], {})
        bucket = pj["genre_bucket"]
        sub = pick_subengine(bucket, sub_engine_key)
        return f"""한국 웹소설 본문을 작성하라.

에피소드: {ep}
플랫폼: {pj['platform']} / 장르: {bucket} / 세부 엔진: {sub.label} ({sub.key})
페이싱: {plat.get('pacing','balanced')}

노브(knobs):
{knobs}

스토리 상태:
{story_state or {}}

문체/리듬 제약:
{constraints_text(style)}\n자료 기반 제약(있으면 반영):\n{profile_constraints_text(knobs.get('profile'))}

플랜:
{plan}

규칙:
- 군더더기 금지, 압축(pacing/compression 반영)
- 감정 변곡 3회 이상
- 반복 최소화
- 마지막은 강한 클리프행어
- 주인공은 욕망 때문에 움직이고 공포 때문에 망설이며 약점 때문에 비용을 치러야 한다
- 본문 길이는 대략 {nv['words_per_episode_min']}~{nv['words_per_episode_max']}자 수준의 한국어 분량을 목표로 한다(토큰 언급 금지)

출력 형식: STRICT JSON ONLY
{{
  "episode_text": "...",
  "quote_line": "...",        # 회차에서 인용/바이럴 가능한 한 줄
  "comment_hook": "...",      # 댓글 유도 질문/문장(8자 이상)
  "cliffhanger": "..."        # 마지막 훅 한 줄(8자 이상)
}}
"""

    @staticmethod
    def episode_rewrite_json(cfg: dict, draft_json: dict, ep: int, knobs: dict, style: StyleVector, sub_engine_key: str, viral_required: bool, story_state: dict | None = None) -> str:
        pj = cfg["project"]
        nv = cfg["novel"]
        plat = PLATFORM_STRATEGY.get(pj["platform"], {})
        bucket = pj["genre_bucket"]
        sub = pick_subengine(bucket, sub_engine_key)
        return f"""다음 JSON을 같은 스키마로 리라이트하라.

목표:
- 군더더기 제거
- 반복 제거
- 갈등 단계 상승 강화
- 대사 선명화
- 감정 흐름 선명화
- 주인공의 약점이 실제 위험과 손실 비용으로 드러나야 함
- 문체/리듬 제약 준수
- 클리프행어 강화
- 바이럴 요소(quote_line/comment_hook/cliffhanger) 유지 또는 강화

플랫폼: {pj['platform']} / 장르: {bucket} / 엔진: {sub.label}
페이싱: {plat.get('pacing','balanced')}
노브(knobs):
{knobs}

스토리 상태:
{story_state or {}}

문체/리듬 제약:
{constraints_text(style)}\n자료 기반 제약(있으면 반영):\n{profile_constraints_text(knobs.get('profile'))}

바이럴 필수: {viral_required}

입력 JSON:
{draft_json}

출력: STRICT JSON ONLY (동일 필드 유지)
"""

    @staticmethod
    def scoring_json(cfg: dict, episode_text: str, ep: int) -> str:
        q = cfg["quality"]
        return f"""다음 에피소드를 0~1로 평가하고 STRICT JSON ONLY로 출력하라.

필드:
hook_score
paywall_score
emotion_density
repetition_score
escalation

목표:
hook_score >= {q['hook_score_min']}
paywall_score >= {q['paywall_score_min']}
emotion_density >= {q['emotion_density_min']}
repetition_score <= {q['repetition_max']}
escalation >= {q['escalation_min']}

에피소드: {ep}

텍스트:
{episode_text}

출력: STRICT JSON ONLY
"""
