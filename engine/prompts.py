from .strategy import PLATFORM_STRATEGY, pick_subengine, list_subengines
from .style import constraints_text, StyleVector
from .profile import profile_constraints_text


_QUALITY_FEEDBACK_DIRECTIVES = {
    "hook_score": "실패 항목이 `hook_score`면 첫 장면에서 욕망, 위기, 즉시 손실 가능성을 앞당겨 초반 후킹을 더 날카롭게 만들 것",
    "paywall_score": "실패 항목이 `paywall_score`면 유료 전환 직전급 선택 비용, 배신, 폭로 중 하나를 회차 말단에 배치해 결제 압력을 높일 것",
    "emotion_density": "실패 항목이 `emotion_density`면 사건 설명만 하지 말고 공포, 욕망, 수치, 분노 같은 감정 반응을 장면마다 더 선명히 넣을 것",
    "escalation": "실패 항목이 `escalation`면 이번 회차의 갈등이 이전보다 비싸고 되돌리기 어렵게 커지도록 손실 규모를 올릴 것",
    "repetition_score": "실패 항목이 `repetition_score`면 같은 대립 구도, 같은 감정 표현, 같은 해결 패턴의 반복을 줄이고 사건 변주를 만들 것",
    "character_score": "실패 항목이 `character_score`면 주인공 욕망/공포/약점을 더 선명하게 드러낼 것",
    "payoff_score": "실패 항목이 `payoff_score`면 이번 회차 보상 또는 손실 회수를 더 분명하게 만들 것",
    "pacing_score": "실패 항목이 `pacing_score`면 장면 전환과 압축도를 조정해 지연 구간을 줄일 것",
    "chemistry_score": "실패 항목이 `chemistry_score`면 관계 긴장 또는 감정 반작용을 더 드러낼 것",
    "cliffhanger_valid": "실패 항목이 `cliffhanger_valid`면 마지막 한 줄을 감탄사로 끝내지 말고 열린 질문, 즉시 위험, 되돌릴 수 없는 선택 비용이 함께 남게 만들 것",
    "cliffhanger_carryover_pressure": "실패 항목이 `cliffhanger_carryover_pressure`면 다음 화를 바로 보지 않으면 손해라고 느껴질 만큼 후속 대가와 미해결 압력을 높일 것",
    "predicted_retention": "실패 항목이 `predicted_retention`면 다음 화를 보게 만드는 미해결 압력과 회차 말단 후킹을 강화할 것",
    "thread_pressure": "실패 항목이 `thread_pressure`면 해결되지 않은 문제들이 서로 얽혀 다음 선택을 더 어렵게 만드는 압박을 늘릴 것",
    "curiosity_debt": "실패 항목이 `curiosity_debt`면 숨겨진 진실, 의도, 대가에 대한 궁금증을 더 구체적인 질문 형태로 남길 것",
    "threat_proximity": "실패 항목이 `threat_proximity`면 위협이 멀리 있다는 느낌을 없애고 이번 회차에서 바로 닥치는 위험으로 당겨올 것",
    "payoff_debt": "실패 항목이 `payoff_debt`면 이전에 심은 약속이나 떡밥 중 하나를 실제 보상, 정보 회수, 손실 정산으로 연결할 것",
    "fallout_pressure": "실패 항목이 `fallout_pressure`면 이번 사건이 관계, 지위, 생존에 남기는 후폭풍을 더 크게 드러낼 것",
    "chemistry_pressure": "실패 항목이 `chemistry_pressure`면 인물 사이의 끌림, 불신, 경쟁심이 다음 선택을 흔들 정도로 반응을 키울 것",
    "information_gap": "실패 항목이 `information_gap`면 독자가 꼭 알고 싶어질 정보의 빈칸을 또렷하게 남기되, 그 빈칸이 갈등과 직접 연결되게 만들 것",
    "sustainability": "실패 항목이 `sustainability`면 한 번의 자극으로 끝내지 말고 다음 회차들까지 이어질 갈등 축과 보상 런웨이를 확보할 것",
    "ceiling_total": "실패 항목이 `ceiling_total`면 훅, 갈등, 감정, 회수 중 가장 약한 축을 끌어올려 회차 체급 자체를 높일 것",
    "causal_score": "실패 항목이 `causal_score`면 사건 원인, 비용 지불, 세계/관계 후폭풍을 더 분명하게 연결할 것",
    "causal_issues": "실패 항목이 `causal_issues`면 사건 원인, 비용 지불, 세계/관계 후폭풍을 더 분명하게 연결할 것",
    "payoff_integrity": "실패 항목이 `payoff_integrity`면 앞서 약속한 보상 축을 배신하지 말고 이번 회차 성취나 손실 정산이 약속과 같은 방향으로 이어지게 만들 것",
    "payoff_corruption_flags": "실패 항목이 `payoff_corruption_flags`면 훅만 키우고 회수를 미루지 말고, 이미 꺼낸 약속의 일부라도 이번 회차 안에 회수할 것",
    "world_instability": "실패 항목이 `world_instability`면 세계 규칙을 새로 흔들기보다 기존 규칙의 결과를 따라가며 설정 충돌과 편의적 전개를 줄일 것",
    "pacing_release_debt": "실패 항목이 `pacing_release_debt`면 연속 고점만 쌓지 말고 이번 회차 안에 부분 보상, 관계 반응, 정보 회수를 넣어 독자 피로를 풀 것",
    "pacing_spike_debt": "실패 항목이 `pacing_spike_debt`면 정체 구간을 끊고 즉시 손실, 폭로, 배신, 마감 압박 중 하나를 전면화해 다음 선택을 비싸게 만들 것",
    "pattern_overused_events": "실패 항목이 `pattern_overused_events`면 최근 자주 쓴 사건 유형을 반복하지 말고 다른 방식의 압박과 전개 변주를 선택할 것",
    "pattern_crowding": "실패 항목이 `pattern_crowding`면 이미 과밀한 장치 조합을 비우고, 한두 개 핵심 패턴만 선명하게 남겨 차별성을 회복할 것",
    "novelty_debt": "실패 항목이 `novelty_debt`면 익숙한 전개에 작은 장식만 더하지 말고 판세를 비트는 새로운 정보나 선택 구조를 추가할 것",
    "novelty_guard": "실패 항목이 `novelty_guard`면 같은 갈등 축을 되풀이하지 말고 플랫폼 독자가 신선하게 느낄 새 보상이나 변수 한 가지를 전면화할 것",
    "conflict_threat_pressure": "실패 항목이 `conflict_threat_pressure`이면 갈등이 미루기 어려운 손실과 후폭풍으로 이어지게 만들고, 열린 스레드의 대가를 더 명시할 것",
    "conflict_consequence_level": "실패 항목이 `conflict_consequence_level`이면 갈등이 미루기 어려운 손실과 후폭풍으로 이어지게 만들고, 열린 스레드의 대가를 더 명시할 것",
    "conflict_open_threads": "실패 항목이 `conflict_open_threads`면 단일 소동으로 끝내지 말고 다음 화까지 이어질 갈등 축을 최소 두 개 이상 살아 있게 만들 것",
    "protagonist_decision_pressure": "실패 항목이 `protagonist_decision_pressure`면 주인공이 이번 회차에서 무엇을 잃을지와 어떤 선택을 강요받는지 더 가깝고 비싸게 만들 것",
    "protagonist_momentum": "실패 항목이 `protagonist_momentum`이면 주인공이 밀리기만 하지 않도록 대가를 치르더라도 판을 움직이는 주도적 진전이나 역습의 발판을 남길 것",
    "balanced_objective": "실패 항목이 `balanced_objective`면 특정 강점 하나에만 기대지 말고 재미, 개연성, 감정, 장기 지속성의 약한 축을 함께 끌어올릴 것",
    "objective_variance": "실패 항목이 `objective_variance`면 강한 축은 유지하되 최약점 축을 우선 보강해 품질 편차를 줄일 것",
    "weakest_objective_axis": "실패 항목이 `weakest_objective_axis`면 가장 약한 품질 축 하나를 골라 회차 안에서 눈에 띄게 보수할 것",
    "prose_readability": "실패 항목이 `prose_readability`면 긴 문장을 끊고 문단을 더 자주 분절하며, 같은 어절로 시작하는 문장을 줄여 한국 웹소설식 가독성을 회복할 것",
}


def _quality_feedback_directives(quality_feedback: dict | None) -> str:
    feedback = dict(quality_feedback or {})
    failed_checks = list(feedback.get("failed_checks", []) or [])
    directives: list[str] = []
    seen: set[str] = set()

    for check_name in failed_checks:
        directive = _QUALITY_FEEDBACK_DIRECTIVES.get(str(check_name))
        if directive and directive not in seen:
            directives.append(f"- {directive}")
            seen.add(directive)

    if not directives:
        directives.append("- 실패 항목이 있으면 가장 약한 축부터 직접 보수할 것")
    return "\n".join(directives)


def _reader_pressure_directives(story_state: dict | None) -> str:
    payload = dict(story_state or {})
    reader_quality = dict(payload.get("reader_quality_debt", {}) or {})
    market_pressure = dict(payload.get("market_feedback_pressure", {}) or {})
    directives: list[str] = []

    debt = dict(reader_quality.get("reader_quality_debt", {}) or {})
    if float(debt.get("hook_debt", 0.0) or 0.0) > 0:
        directives.append("- 초반 1~3문단 안에 욕망, 위험, 즉시 손실 가능성을 함께 배치해 첫 클릭 독자를 바로 붙잡을 것")
    if float(debt.get("payoff_debt", 0.0) or 0.0) > 0:
        directives.append("- 이번 회차 안에 약속된 보상, 정보 회수, 관계 후폭풍 중 하나를 반드시 가시화해 payoff 체감을 올릴 것")
    if float(debt.get("fatigue_debt", 0.0) or 0.0) > 0:
        directives.append("- 같은 감정/대립 반복을 줄이고 장면 압축과 전개 변주를 늘려 연재 피로를 낮출 것")
    if float(debt.get("retention_debt", 0.0) or 0.0) > 0:
        directives.append("- 회차 말미에 열린 질문, 즉시 위험, 다음 선택 비용을 함께 남겨 다음 화 클릭 손실감을 만들 것")
    if float(debt.get("thinness_debt", 0.0) or 0.0) > 0:
        directives.append("- 장면이 얇게 흐르지 않도록 욕망, 대가, 위협, 관계 압박 중 최소 두 축을 같은 장면 안에서 동시에 체감시키고 밀도를 올릴 것")
    if float(debt.get("repetition_debt", 0.0) or 0.0) > 0:
        directives.append("- 최근과 같은 훅, 반전, 감정 반응, 대립 패턴을 복제하지 말고 사건 방식과 감정 결을 분명히 변주할 것")
    if float(debt.get("deja_vu_debt", 0.0) or 0.0) > 0:
        directives.append("- 기시감이 나지 않도록 익숙한 압박을 반복하지 말고 판세를 비트는 새로운 정보, 선택 구조, 관계 축을 한 번은 전면화할 것")
    if float(debt.get("fake_urgency_debt", 0.0) or 0.0) > 0:
        directives.append("- 말로만 급박하게 굴지 말고 이번 회차 안에서 실제 손실, 선택 비용, 되돌릴 수 없는 전진 중 하나를 발생시킬 것")
    if float(debt.get("compression_debt", 0.0) or 0.0) > 0:
        directives.append("- 이미 이해된 설명을 반복하지 말고 문단을 더 압축해 핵심 장면 도착 시간을 앞당길 것")

    if market_pressure:
        if float(market_pressure.get("market_pressure_response", 0.0) or 0.0) > 0:
            directives.append("- 최근 시장 반응이 약하므로 회차 체급이 보이게 갈등 비용과 후킹 강도를 평시보다 더 높일 것")
        if float(market_pressure.get("reader_exit_risk_response", 0.0) or 0.0) > 0:
            directives.append("- 이탈 위험이 높으므로 지연 설명을 줄이고 핵심 장면 도착 시간을 앞당길 것")
        if "campaign_roi_response" in market_pressure:
            directives.append("- 기존 패턴의 효율이 약하므로 익숙한 장식 반복 대신 새로운 보상 변수나 판세 전환을 한 번 전면화할 것")

    if not directives:
        return "- 상위독자가 첫 화부터 따라붙을 만큼 초반 흡입력, 회차 말미 훅, payoff 압력을 함께 유지할 것"
    return "\n".join(directives)


def _arc_pressure_directives(story_state: dict | None) -> str:
    payload = dict(story_state or {})
    arc_pressure = dict(payload.get("arc_pressure", {}) or {})
    debt = dict(arc_pressure.get("arc_pressure", {}) or {})
    directives: list[str] = []

    if float(debt.get("payoff_debt", 0.0) or 0.0) > 0:
        directives.append("- 장기 약속 회수가 밀렸으므로 이번 회차 안에 보상, 정산, 진실 공개 중 하나를 확실히 전진시킬 것")
    if float(debt.get("momentum_debt", 0.0) or 0.0) > 0:
        directives.append("- 주인공이 끌려가기만 하지 않도록 대가를 치르더라도 판을 움직이는 주도적 선택이나 역습의 발판을 반드시 남길 것")

    if not directives:
        return "- 장기 아크 보상과 주인공 판타지 상승감을 동시에 유지할 것"
    return "\n".join(directives)


def _platform_soak_directives(story_state: dict | None) -> str:
    payload = dict(story_state or {})
    portfolio = dict(payload.get("portfolio", {}) or {})
    platform_soak_pressure = float(portfolio.get("platform_soak_pressure", 0.0) or 0.0)
    platform_soak_summary = dict(portfolio.get("platform_soak_summary", {}) or {})
    directives: list[str] = []

    if platform_soak_pressure >= 0.22:
        directives.append("- 최근 플랫폼 soak 압력이 높은 버킷이므로 초반 5화 안의 payoff 간격을 더 촘촘히 두고, 설명보다 사건 도착 속도를 앞당길 것")
    if platform_soak_pressure >= 0.34:
        directives.append("- 플랫폼 스트레스가 강하므로 얇은 연결 장면을 줄이고 손실, 위상 변화, 관계 반작용을 한 회차 안에서 더 또렷하게 발생시킬 것")
    if str(platform_soak_summary.get("dominant_mode") or "") == "volatile":
        directives.append("- 최근 long-run 양상이 불안정했으므로 회차 말미 훅만 키우지 말고 부분 회수와 후속 대가를 함께 남겨 장기 피로를 낮출 것")

    if not directives:
        return "- 플랫폼 cadence 압력과 상위독자 체감 압력을 동시에 만족하도록 초반 payoff 간격과 사건 압축을 균형 있게 유지할 것"
    return "\n".join(directives)


class PROMPTS:
    @staticmethod
    def master_outline(cfg: dict, ext_snapshot: dict, sub_engine_key: str, story_state: dict | None = None) -> str:
        pj = cfg["project"]
        nv = cfg["novel"]
        q = cfg["quality"]
        plat = PLATFORM_STRATEGY.get(pj["platform"], {})
        bucket = pj["genre_bucket"]
        sub = pick_subengine(bucket, sub_engine_key)
        portfolio = dict((story_state or {}).get("portfolio", {}) or {})
        pattern = dict((story_state or {}).get("pattern_memory", {}) or {})
        design_guardrails = list(portfolio.get("design_guardrails", []) or [])
        if not design_guardrails:
            design_guardrails = list(((cfg.get("project", {}) or {}).get("bootstrap_design_guardrails", []) or []))

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

포트폴리오 설계 가드레일:
{design_guardrails}

플랫폼 soak 압력 지시:
{_platform_soak_directives(story_state)}

패턴 메모리:
{pattern}

출력(한국어, 구체적으로):
1) 로그라인 1문장
2) 세계 규칙/시스템/핵심 제약
3) 주인공/적대자/조력자/라이벌(각 2~3문장)
4) 1~3화: 씬 단위 비트(각 씬: 목표/갈등/감정 변곡/훅)
5) 20~30화: 유료 전환 폭발 아크 비트(필수)
6) 50화마다 아크 리셋 지점(총 {nv['total_episodes']//50}개 이상)
7) 최종 결말과 마지막 갈등 해결
8) 최근 실패 패턴을 피하기 위한 설계 금지/회피 규칙 3개
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

포트폴리오 메모리:
{(story_state or {}).get('portfolio', {})}

교차 트랙 지표:
{((story_state or {}).get('portfolio', {}) or {}).get('portfolio_metrics', {})}

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
- 다른 트랙에서 이미 과밀한 패턴은 피하고, 포트폴리오 차원의 차별화를 유지할 것
- 포트폴리오 정책 지시가 있으면 우선 반영하고, 교차 트랙 간 위험 분산과 출시 간섭 완화를 함께 고려할 것
- 추가 상위독자 압력 지시:
{_reader_pressure_directives(story_state)}
- 장기 아크 압력 지시:
{_arc_pressure_directives(story_state)}
- 플랫폼 soak 압력 지시:
{_platform_soak_directives(story_state)}
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
- 상위독자 압력 지시:
{_reader_pressure_directives(story_state)}
- 장기 아크 압력 지시:
{_arc_pressure_directives(story_state)}
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
    def episode_rewrite_json(
        cfg: dict,
        draft_json: dict,
        ep: int,
        knobs: dict,
        style: StyleVector,
        sub_engine_key: str,
        viral_required: bool,
        story_state: dict | None = None,
        repair_plan: dict | None = None,
        quality_feedback: dict | None = None,
    ) -> str:
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
- 인과 보수 지시가 있으면 우선 반영

플랫폼: {pj['platform']} / 장르: {bucket} / 엔진: {sub.label}
페이싱: {plat.get('pacing','balanced')}
노브(knobs):
{knobs}

스토리 상태:
{story_state or {}}

인과 보수 지시:
{repair_plan or {}}

품질 게이트 피드백:
{quality_feedback or {}}

문체/리듬 제약:
{constraints_text(style)}\n자료 기반 제약(있으면 반영):\n{profile_constraints_text(knobs.get('profile'))}

바이럴 필수: {viral_required}

입력 JSON:
{draft_json}

추가 규칙:
- `quality_feedback.failed_checks`에 적힌 항목은 직접 보수할 것
{_quality_feedback_directives(quality_feedback)}
- 상위독자 압력 지시:
{_reader_pressure_directives(story_state)}
- 장기 아크 압력 지시:
{_arc_pressure_directives(story_state)}

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
character_score
payoff_score
pacing_score
chemistry_score

목표:
hook_score >= {q['hook_score_min']}
paywall_score >= {q['paywall_score_min']}
emotion_density >= {q['emotion_density_min']}
repetition_score <= {q['repetition_max']}
escalation >= {q['escalation_min']}
character_score >= {q.get('character_score_min', 0.65)}
payoff_score >= {q.get('payoff_score_min', 0.68)}
pacing_score >= {q.get('pacing_score_min', 0.66)}
chemistry_score >= {q.get('chemistry_score_min', 0.60)}

에피소드: {ep}

텍스트:
{episode_text}

출력: STRICT JSON ONLY
"""
