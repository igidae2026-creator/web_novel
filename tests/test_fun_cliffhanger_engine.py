from engine.cliffhanger_engine import generate_cliffhanger_plan, validate_cliffhanger, enforce_cliffhanger


def test_cliffhanger_plan_tracks_withheld_consequence():
    plan = generate_cliffhanger_plan(
        {"protagonist": {"surface_goal": "복수", "urgency": 8}},
        {"threads": [{"label": "배신 추적", "consequence": "즉시 붕괴"}]},
        {"type": "betrayal", "consequence": "신뢰가 무너지며 다음 선택의 비용이 급등한다", "carryover_pressure": 8},
    )

    assert plan["mode"] == "choice_lock"
    assert "비용" in plan["withheld_consequence"] or "무너지" in plan["withheld_consequence"]
    assert plan["carryover_pressure"] >= 8


def test_cliffhanger_enforcement_replaces_weak_line():
    plan = generate_cliffhanger_plan(
        {"protagonist": {"surface_goal": "생존", "urgency": 9}},
        {"threads": [{"label": "추격전", "consequence": "더 큰 대가가 회수된다"}]},
        {"type": "loss", "consequence": "지켜야 할 것을 잃고 복구 불가 손실이 남는다", "carryover_pressure": 9},
    )
    meta = enforce_cliffhanger({"cliffhanger": "짧다"}, plan)
    valid, _ = validate_cliffhanger(meta, plan)
    assert valid
    assert meta["cliffhanger"] != "짧다"


def test_cliffhanger_validation_rejects_generic_question_without_plan_specificity():
    plan = generate_cliffhanger_plan(
        {"protagonist": {"surface_goal": "복수", "urgency": 8}},
        {"threads": [{"label": "배신 추적", "consequence": "신뢰가 무너지며 다음 선택의 비용이 급등한다"}]},
        {"type": "betrayal", "consequence": "신뢰가 무너지며 다음 선택의 비용이 급등한다", "carryover_pressure": 8},
    )

    valid, reason = validate_cliffhanger({"cliffhanger": "누가 여기서 살아남을까?"}, plan)

    assert valid is False
    assert reason == "cliffhanger not specific to planned conflict"
