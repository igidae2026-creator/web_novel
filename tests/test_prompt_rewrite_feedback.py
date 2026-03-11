from engine.prompts import PROMPTS
from engine.style import StyleVector


def _cfg() -> dict:
    return {
        "project": {
            "platform": "Munpia",
            "genre_bucket": "A",
            "sub_engine": "AUTO",
        },
        "novel": {
            "total_episodes": 300,
            "words_per_episode_min": 2500,
            "words_per_episode_max": 3500,
        },
        "quality": {},
        "quality": {
            "hook_score_min": 0.7,
            "paywall_score_min": 0.7,
            "emotion_density_min": 0.65,
            "repetition_max": 0.35,
            "escalation_min": 0.65,
        },
    }


def test_episode_rewrite_prompt_includes_targeted_guidance_for_uncovered_gate_failures():
    prompt = PROMPTS.episode_rewrite_json(
        _cfg(),
        draft_json={"episode_text": "초안", "quote_line": "한 줄", "comment_hook": "다음은?", "cliffhanger": "끝"},
        ep=12,
        knobs={"compression": 0.7},
        style=StyleVector(),
        sub_engine_key="AUTO",
        viral_required=True,
        story_state={},
        repair_plan={},
        quality_feedback={
            "failed_checks": [
                "payoff_integrity",
                "payoff_corruption_flags",
                "world_instability",
                "pattern_overused_events",
                "novelty_guard",
                "protagonist_momentum",
                "balanced_objective",
                "objective_variance",
                "weakest_objective_axis",
                "cliffhanger_valid",
                "threat_proximity",
                "payoff_debt",
            ]
        },
    )

    assert "앞서 약속한 보상 축을 배신하지 말고" in prompt
    assert "이미 꺼낸 약속의 일부라도 이번 회차 안에 회수할 것" in prompt
    assert "기존 규칙의 결과를 따라가며 설정 충돌과 편의적 전개를 줄일 것" in prompt
    assert "최근 자주 쓴 사건 유형을 반복하지 말고" in prompt
    assert "플랫폼 독자가 신선하게 느낄 새 보상이나 변수" in prompt
    assert "주도적 진전이나 역습의 발판을 남길 것" in prompt
    assert "재미, 개연성, 감정, 장기 지속성의 약한 축을 함께 끌어올릴 것" in prompt
    assert "품질 편차를 줄일 것" in prompt
    assert "가장 약한 품질 축 하나를 골라 회차 안에서 눈에 띄게 보수할 것" in prompt
    assert "열린 질문, 즉시 위험, 되돌릴 수 없는 선택 비용" in prompt
    assert "위협이 멀리 있다는 느낌을 없애고" in prompt
    assert "이전에 심은 약속이나 떡밥 중 하나를 실제 보상" in prompt


def test_master_outline_prompt_includes_design_guardrails_for_hidden_reader_risk():
    prompt = PROMPTS.master_outline(
        _cfg(),
        ext_snapshot={},
        sub_engine_key="AUTO",
        story_state={
            "portfolio": {
                "design_guardrails": [
                    "새 아크와 새 작품 기획에서 얇은 장면 연결과 말뿐인 긴장 유발 패턴을 금지한다",
                    "최근과 유사한 갈등 구조를 반복하지 말고 보상 구조 자체를 바꾼다",
                ]
            },
            "pattern_memory": {"overused_events": ["betrayal"], "exploration_bias": 8},
        },
    )

    assert "포트폴리오 설계 가드레일" in prompt
    assert "얇은 장면 연결과 말뿐인 긴장 유발 패턴을 금지한다" in prompt
    assert "패턴 메모리" in prompt
    assert "설계 금지/회피 규칙 3개" in prompt
