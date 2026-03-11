from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass(frozen=True)
class SubEngine:
    key: str
    label: str
    brief: str

GENRE_SUBENGINES: Dict[str, List[SubEngine]] = {
    "A": [
        SubEngine("A_REVENGE_REGRESSION", "회귀-복수형", "복수 타깃/권력 회수/단계적 굴복"),
        SubEngine("A_SYSTEM_GROWTH", "시스템-성장형", "미션/보상/스탯/랭킹 구조"),
        SubEngine("A_POLITICS_POWER", "권력-정치형", "세력전/협상/배신/승진"),
        SubEngine("A_PARTY_EXPANSION", "파티-확장형", "동료 수집/던전 루프/확장"),
    ],
    "B": [
        SubEngine("B_CLASSIC_MURIM", "정통 무협", "문파/사제/원한/비급"),
        SubEngine("B_DEMONIC_CULT", "사파/마도", "금기/타락/유혹/대가"),
        SubEngine("B_REVENGE_DUEL", "복수-결투", "명확한 목표/결투/승급"),
        SubEngine("B_SECT_POLITICS", "문파 정치", "권력 다툼/내부 암투"),
    ],
    "C": [
        SubEngine("C_CONTRACT", "계약 관계", "계약/가짜 연애/조건-파국"),
        SubEngine("C_ISEKAI_SURVIVAL", "빙의 생존", "규칙 학습/파멸 회피/반전"),
        SubEngine("C_NOBLE_POWER", "귀족 권력", "가문/정치/결혼/상속"),
        SubEngine("C_HEALING_ROMANCE", "치유 로맨스", "상처/회복/안정"),
    ],
    "D": [
        SubEngine("D_SLOW_BURN", "슬로우번", "긴장 누적/미세 진전"),
        SubEngine("D_ENEMIES_TO_LOVERS", "혐관", "갈등-해소 루프"),
        SubEngine("D_OBSESSION", "집착", "위험한 끌림/통제"),
        SubEngine("D_POWER_COUPLE", "강강", "대등/협업/승리"),
    ],
    "E": [
        SubEngine("E_WHO_DUNNIT", "추리", "단서/오답/해답"),
        SubEngine("E_THRILLER", "스릴러", "위협/추격/역전"),
        SubEngine("E_PSYCHOLOGICAL", "심리", "불신/자아/반전"),
        SubEngine("E_CRIME_NOIR", "범죄 느와르", "도덕 회색/거래/파국"),
    ],
    "F": [
        SubEngine("F_SPACE_OPERA", "스페이스 오페라", "세력/전쟁/탐사"),
        SubEngine("F_HARD_SF", "하드 SF", "규칙/과학/정합"),
        SubEngine("F_CYBERPUNK", "사이버펑크", "기업/해킹/계급"),
        SubEngine("F_POST_APOC", "포스트아포칼립스", "생존/규칙/공동체"),
    ],
    "G": [
        SubEngine("G_NATION_BUILDING", "국가 경영", "제도/혁신/확장"),
        SubEngine("G_WAR_STRATEGY", "전쟁 전략", "전투/전략/승패"),
        SubEngine("G_REGRESSION_HISTORY", "역사 회귀", "미래지식/개입"),
        SubEngine("G_COURT_INTRIGUE", "궁중 암투", "권모술수/정적"),
    ],
    "H": [
        SubEngine("H_SLICE_OF_LIFE", "일상", "루틴/관계/성장"),
        SubEngine("H_HEALING", "힐링", "안정/회복/따뜻함"),
        SubEngine("H_COMING_OF_AGE", "성장", "관계 변화/선택"),
        SubEngine("H_WORKPLACE", "직장물", "갈등/성과/관계"),
    ],
    "I": [
        SubEngine("I_GENRE_MIX", "장르 혼합", "두 장르 규칙 결합"),
        SubEngine("I_META", "메타", "자기지시/세계 인식"),
        SubEngine("I_EXPERIMENTAL", "실험", "형식 변주"),
        SubEngine("I_PARODY", "패러디", "클리셰 비틀기"),
    ],
}

PLATFORM_STRATEGY = {
    "Munpia": {
        "pacing": "aggressive",
        "hook_rule": "1화에서 즉시 갈등 발생. 정보 덤프 금지.",
        "paywall_rule": "20~30화에 위상 급변/대형 보상/대형 배신 중 하나를 반드시 배치.",
        "dialogue_bias": 0.45,
        "cliff_bias": 0.85,
    },
    "NaverSeries": {
        "pacing": "balanced",
        "hook_rule": "초반 후킹은 강하게, 다만 이해 가능한 정보량 유지.",
        "paywall_rule": "유료 구간에 감정 보상 + 사건 보상을 균형 있게 배치.",
        "dialogue_bias": 0.40,
        "cliff_bias": 0.75,
    },
    "KakaoPage": {
        "pacing": "aggressive",
        "hook_rule": "클리프행어 강도 높게. 문장 길이 압축.",
        "paywall_rule": "유료 전환 구간에서 감정 최고점 + 관계/위상 변화 반드시 발생.",
        "dialogue_bias": 0.50,
        "cliff_bias": 0.90,
    },
    "Ridibooks": {
        "pacing": "character",
        "hook_rule": "캐릭터 음성/관계 긴장 우선. 미세 감정 표현 강화.",
        "paywall_rule": "관계 전환의 분기점(고백/배신/선택)을 유료 구간에 배치.",
        "dialogue_bias": 0.58,
        "cliff_bias": 0.70,
    },
    "Novelpia": {
        "pacing": "spiky",
        "hook_rule": "초반 후킹을 과감하게. 실험/변주 허용.",
        "paywall_rule": "유료 구간(또는 전환 구간)에 강한 자극/반전 배치.",
        "dialogue_bias": 0.48,
        "cliff_bias": 0.88,
    },
}

def list_subengines(bucket: str):
    return GENRE_SUBENGINES.get(bucket, [])

def pick_subengine(bucket: str, requested_key: str) -> SubEngine:
    subs = GENRE_SUBENGINES.get(bucket, [])
    if not subs:
        return SubEngine("GENERIC", "기본", "기본")
    if requested_key and requested_key != "AUTO":
        for s in subs:
            if s.key == requested_key:
                return s
    # AUTO: pick first by default; caller can override with more advanced logic
    return subs[0]


def pick_bootstrap_subengine(
    bucket: str,
    hidden_reader_risk: float = 0.0,
    heavy_reader_signal_trend: float = 1.0,
    platform_soak_pressure: float = 0.0,
) -> SubEngine:
    subs = GENRE_SUBENGINES.get(bucket, [])
    if not subs:
        return SubEngine("GENERIC", "기본", "기본")
    pressure = hidden_reader_risk + max(0.0, 0.72 - heavy_reader_signal_trend) + platform_soak_pressure * 0.85
    if pressure >= 0.9 and len(subs) >= 4:
        return subs[3]
    if pressure >= 0.55 and len(subs) >= 3:
        return subs[2]
    if pressure >= 0.35 and len(subs) >= 2:
        return subs[1]
    return subs[0]


def bootstrap_design_guardrails(
    hidden_reader_risk: float = 0.0,
    heavy_reader_signal_trend: float = 1.0,
    platform_soak_pressure: float = 0.0,
    platform: str | None = None,
) -> List[str]:
    guardrails: List[str] = []
    pressure = hidden_reader_risk + max(0.0, 0.72 - heavy_reader_signal_trend) + platform_soak_pressure * 0.85
    if pressure >= 0.35:
        guardrails.append("초기 기획에서 얇은 장면 연결과 말뿐인 긴장 유발 패턴을 금지한다")
        guardrails.append("초반 3화 안에 실제 손실, 선택 비용, 보상 회수 중 최소 하나를 확정한다")
    if pressure >= 0.5:
        guardrails.append("최근과 유사한 갈등 구조와 클리프행어 어법을 반복하지 말고 보상 구조 자체를 바꾼다")
    if platform_soak_pressure >= 0.22:
        guardrails.append("플랫폼 cadence 압력이 높은 버킷이므로 초반 5화 안에 payoff 회수 간격을 더 촘촘하게 둔다")
    if 0.0 < heavy_reader_signal_trend < 0.62:
        guardrails.append("상위독자 체감 압력이 약했던 패턴을 피하고 주인공 주도 선택과 회차 말미 손실감을 강화한다")
    if platform:
        pacing = str((PLATFORM_STRATEGY.get(platform, {}) or {}).get("pacing") or "balanced")
        if pacing == "aggressive":
            guardrails.append("공격적 플랫폼이므로 정보 설명보다 즉시 갈등과 위상 변화를 우선 배치한다")
        elif pacing == "character":
            guardrails.append("캐릭터 중심 플랫폼이므로 관계 긴장과 감정 전환을 사건과 같은 비중으로 배치한다")
    if not guardrails:
        guardrails.append("초기 기획에서 강한 후킹과 장기 payoff를 함께 설계한다")
    return guardrails[:4]


# Joara strategy
PLATFORM_STRATEGY["Joara"] = {
    "pacing": "balanced",
    "hook_rule": "초반 후킹은 강하게. 다만 과도한 자극 반복은 금지.",
    "paywall_rule": "전환 구간(유료/후원/선호 유도)에서 관계/위상/보상 중 최소 1개를 확정.",
    "dialogue_bias": 0.52,
    "cliff_bias": 0.78,
}
