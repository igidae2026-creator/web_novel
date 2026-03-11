from engine.quality_gate import quality_gate, quality_gate_report
from engine.pipeline import _project_episode_state
from engine.story_state import ensure_story_state


def test_quality_gate_accepts_balanced_episode_signals():
    report = quality_gate_report(
        {
            "hook_score": 0.82,
            "paywall_score": 0.78,
            "emotion_density": 0.76,
            "escalation": 0.79,
            "character_score": 0.75,
            "payoff_score": 0.77,
            "pacing_score": 0.74,
            "chemistry_score": 0.69,
            "repetition_score": 0.18,
        },
        {
            "hook_score_min": 0.7,
            "paywall_score_min": 0.7,
            "emotion_density_min": 0.65,
            "escalation_min": 0.65,
            "character_score_min": 0.66,
            "payoff_score_min": 0.68,
            "pacing_score_min": 0.66,
            "chemistry_score_min": 0.6,
            "cliffhanger_valid_required": True,
            "cliffhanger_carryover_pressure_min": 6,
            "repetition_max": 0.35,
            "predicted_retention_min": 0.62,
            "thread_pressure_min": 6,
            "curiosity_debt_min": 5,
            "threat_proximity_min": 5,
            "payoff_debt_min": 2,
            "fallout_pressure_min": 4,
            "chemistry_pressure_min": 4,
            "information_gap_min": 4,
            "retention_sustainability_min": 5,
            "ceiling_total_min": 58,
            "causal_score_min": 0.72,
            "causal_issues_max": 2,
            "payoff_integrity_min": 0.72,
            "payoff_corruption_flags_max": 0,
            "world_instability_max": 7,
            "pattern_overused_events_max": 1,
            "pattern_crowding_max": 5,
            "novelty_debt_max": 4,
            "novelty_guard_min": 4,
            "conflict_threat_pressure_min": 6,
            "conflict_consequence_level_min": 5,
            "conflict_open_threads_min": 2,
            "protagonist_decision_pressure_min": 7,
            "protagonist_momentum_min": 0.52,
            "balanced_objective_min": 0.66,
            "objective_variance_max": 0.33,
            "weakest_objective_axis_min": 0.55,
        },
        retention_state={
            "unresolved_thread_pressure": 8,
            "curiosity_debt": 7,
            "threat_proximity": 8,
            "payoff_debt": 4,
            "fallout_pressure": 6,
            "chemistry_pressure": 6,
            "information_gap": 5,
            "sustainability": 7,
        },
        predicted_retention=0.74,
        cliffhanger="배신 추적은 아직 끝나지 않았다. 신뢰가 무너지며 다음 선택의 비용이 급등한다. 이번 선택은 관계를 되돌릴 수 없게 바꾼다. 그리고 누가 먼저 칼을 빼들었고 누가 늦게 알아차릴까.",
        cliffhanger_plan={
            "target": "배신 추적",
            "open_question": "누가 먼저 칼을 빼들었고 누가 늦게 알아차릴까",
            "carryover_pressure": 8,
            "irreversible_cost": "이번 선택은 관계를 되돌릴 수 없게 바꾼다.",
        },
        content_ceiling={"ceiling_total": 67},
        causal_report={"score": 0.88, "issues": ["relationship_fallout"]},
        story_state={
            "promise_graph": {"payoff_integrity": 0.81, "payoff_corruption_flags": []},
            "world": {"instability": 5},
            "pattern_memory": {"overused_events": ["betrayal"]},
            "portfolio_memory": {"novelty_guard": 7},
            "portfolio_metrics": {"pattern_crowding": 3, "novelty_debt": 2},
            "conflict": {
                "threat_pressure": 8,
                "consequence_level": 7,
                "threads": [
                    {"id": "main", "status": "open"},
                    {"id": "fallout", "status": "pressured"},
                ],
            },
            "cast": {
                "protagonist": {"decision_pressure": 9, "progress": 2, "backlash": 1, "urgency": 8},
                "rival": {"progress": 1},
            },
        },
        objective_scores={
            "fun": 0.78,
            "coherence": 0.77,
            "character_persuasiveness": 0.76,
            "pacing": 0.74,
            "retention": 0.79,
            "emotional_immersion": 0.75,
            "information_design": 0.73,
            "emotional_payoff": 0.74,
            "long_run_sustainability": 0.72,
            "world_logic": 0.76,
            "chemistry": 0.69,
            "stability": 0.75,
        },
    )

    assert report["passed"] is True
    assert report["failed_checks"] == []


def test_quality_gate_rejects_thin_episode_even_if_basic_scores_pass():
    accepted = quality_gate(
        {
            "hook_score": 0.75,
            "paywall_score": 0.73,
            "emotion_density": 0.68,
            "escalation": 0.7,
            "character_score": 0.61,
            "payoff_score": 0.64,
            "pacing_score": 0.62,
            "chemistry_score": 0.51,
            "repetition_score": 0.2,
        },
        {
            "hook_score_min": 0.7,
            "paywall_score_min": 0.7,
            "emotion_density_min": 0.65,
            "escalation_min": 0.65,
            "character_score_min": 0.66,
            "payoff_score_min": 0.68,
            "pacing_score_min": 0.66,
            "chemistry_score_min": 0.6,
            "cliffhanger_valid_required": True,
            "cliffhanger_carryover_pressure_min": 6,
            "repetition_max": 0.35,
            "predicted_retention_min": 0.62,
            "thread_pressure_min": 6,
            "curiosity_debt_min": 5,
            "ceiling_total_min": 58,
            "causal_score_min": 0.72,
            "causal_issues_max": 2,
            "payoff_integrity_min": 0.72,
            "payoff_corruption_flags_max": 0,
            "world_instability_max": 7,
            "conflict_threat_pressure_min": 6,
            "conflict_consequence_level_min": 5,
            "conflict_open_threads_min": 2,
            "protagonist_decision_pressure_min": 7,
            "balanced_objective_min": 0.66,
            "objective_variance_max": 0.33,
            "weakest_objective_axis_min": 0.55,
        },
        retention_state={"unresolved_thread_pressure": 3, "curiosity_debt": 2},
        predicted_retention=0.55,
        cliffhanger="다음 화를 기대해주세요.",
        cliffhanger_plan={
            "target": "주 갈등",
            "open_question": "누가 대가를 치를까",
            "carryover_pressure": 3,
            "irreversible_cost": "되돌릴 수 없는 손실이 남는다.",
        },
        content_ceiling={"ceiling_total": 49},
        causal_report={"score": 0.5, "issues": ["causal_link", "world_consequence", "cliffhanger_alignment"]},
        story_state={
            "promise_graph": {"payoff_integrity": 0.44, "payoff_corruption_flags": [{"type": "overdue_payoff"}]},
            "world": {"instability": 8},
            "conflict": {
                "threat_pressure": 3,
                "consequence_level": 3,
                "threads": [{"id": "main", "status": "open"}],
            },
            "cast": {"protagonist": {"decision_pressure": 4}},
        },
        objective_scores={
            "fun": 0.59,
            "coherence": 0.44,
            "character_persuasiveness": 0.46,
            "pacing": 0.48,
            "retention": 0.43,
            "emotional_immersion": 0.47,
            "information_design": 0.39,
            "emotional_payoff": 0.36,
            "long_run_sustainability": 0.42,
            "world_logic": 0.33,
            "chemistry": 0.31,
            "stability": 0.38,
        },
    )

    assert accepted is False


def test_quality_gate_rejects_weak_cliffhanger_even_if_other_quality_signals_pass():
    report = quality_gate_report(
        {
            "hook_score": 0.83,
            "paywall_score": 0.8,
            "emotion_density": 0.76,
            "escalation": 0.8,
            "character_score": 0.77,
            "payoff_score": 0.75,
            "pacing_score": 0.73,
            "chemistry_score": 0.68,
            "repetition_score": 0.17,
        },
        {
            "hook_score_min": 0.7,
            "paywall_score_min": 0.7,
            "emotion_density_min": 0.65,
            "escalation_min": 0.65,
            "character_score_min": 0.66,
            "payoff_score_min": 0.68,
            "pacing_score_min": 0.66,
            "chemistry_score_min": 0.6,
            "cliffhanger_valid_required": True,
            "cliffhanger_carryover_pressure_min": 6,
            "repetition_max": 0.35,
            "predicted_retention_min": 0.62,
            "thread_pressure_min": 6,
            "curiosity_debt_min": 5,
            "ceiling_total_min": 58,
            "causal_score_min": 0.72,
            "causal_issues_max": 2,
            "payoff_integrity_min": 0.72,
            "payoff_corruption_flags_max": 0,
            "world_instability_max": 7,
            "conflict_threat_pressure_min": 6,
            "conflict_consequence_level_min": 5,
            "conflict_open_threads_min": 2,
            "protagonist_decision_pressure_min": 7,
            "balanced_objective_min": 0.66,
            "objective_variance_max": 0.33,
            "weakest_objective_axis_min": 0.55,
        },
        cliffhanger="문이 열렸다.",
        cliffhanger_plan={
            "target": "배신 추적",
            "open_question": "누가 먼저 칼을 빼들었고 누가 늦게 알아차릴까",
            "carryover_pressure": 4,
            "irreversible_cost": "이번 선택은 관계를 되돌릴 수 없게 바꾼다.",
        },
        retention_state={"unresolved_thread_pressure": 8, "curiosity_debt": 7},
        predicted_retention=0.75,
        content_ceiling={"ceiling_total": 67},
        causal_report={"score": 0.86, "issues": ["relationship_fallout"]},
        story_state={
            "promise_graph": {"payoff_integrity": 0.8, "payoff_corruption_flags": []},
            "world": {"instability": 5},
            "conflict": {
                "threat_pressure": 8,
                "consequence_level": 7,
                "threads": [
                    {"id": "main", "status": "open"},
                    {"id": "fallout", "status": "open"},
                ],
            },
            "cast": {"protagonist": {"decision_pressure": 9}},
        },
        objective_scores={
            "fun": 0.79,
            "coherence": 0.78,
            "character_persuasiveness": 0.77,
            "pacing": 0.75,
            "retention": 0.8,
            "emotional_immersion": 0.76,
            "information_design": 0.74,
            "emotional_payoff": 0.75,
            "long_run_sustainability": 0.73,
            "world_logic": 0.77,
            "chemistry": 0.69,
            "stability": 0.76,
        },
    )

    assert report["passed"] is False
    assert "cliffhanger_valid" in report["failed_checks"]
    assert "cliffhanger_carryover_pressure" in report["failed_checks"]


def test_quality_gate_rejects_generic_cliffhanger_even_with_strong_carryover_plan():
    report = quality_gate_report(
        {
            "hook_score": 0.84,
            "paywall_score": 0.8,
            "emotion_density": 0.77,
            "escalation": 0.79,
            "character_score": 0.78,
            "payoff_score": 0.76,
            "pacing_score": 0.74,
            "chemistry_score": 0.69,
            "repetition_score": 0.16,
        },
        {
            "hook_score_min": 0.7,
            "paywall_score_min": 0.7,
            "emotion_density_min": 0.65,
            "escalation_min": 0.65,
            "character_score_min": 0.66,
            "payoff_score_min": 0.68,
            "pacing_score_min": 0.66,
            "chemistry_score_min": 0.6,
            "cliffhanger_valid_required": True,
            "cliffhanger_carryover_pressure_min": 6,
            "repetition_max": 0.35,
            "predicted_retention_min": 0.62,
            "thread_pressure_min": 6,
            "curiosity_debt_min": 5,
            "ceiling_total_min": 58,
            "causal_score_min": 0.72,
            "causal_issues_max": 2,
            "payoff_integrity_min": 0.72,
            "payoff_corruption_flags_max": 0,
            "world_instability_max": 7,
            "conflict_threat_pressure_min": 6,
            "conflict_consequence_level_min": 5,
            "conflict_open_threads_min": 2,
            "protagonist_decision_pressure_min": 7,
            "protagonist_momentum_min": 0.52,
            "balanced_objective_min": 0.66,
            "objective_variance_max": 0.33,
            "weakest_objective_axis_min": 0.55,
        },
        cliffhanger="누가 살아남을까?",
        cliffhanger_plan={
            "target": "배신 추적",
            "open_question": "누가 먼저 칼을 빼들었고 누가 늦게 알아차릴까",
            "carryover_pressure": 8,
            "withheld_consequence": "신뢰가 무너지며 다음 선택의 비용이 급등한다.",
            "irreversible_cost": "이번 선택은 관계를 되돌릴 수 없게 바꾼다.",
        },
        retention_state={"unresolved_thread_pressure": 8, "curiosity_debt": 7},
        predicted_retention=0.75,
        content_ceiling={"ceiling_total": 67},
        causal_report={"score": 0.86, "issues": ["relationship_fallout"]},
        story_state={
            "promise_graph": {"payoff_integrity": 0.8, "payoff_corruption_flags": []},
            "world": {"instability": 5},
            "conflict": {
                "threat_pressure": 8,
                "consequence_level": 7,
                "threads": [
                    {"id": "main", "status": "open"},
                    {"id": "fallout", "status": "open"},
                ],
            },
            "cast": {
                "protagonist": {"decision_pressure": 9, "progress": 2, "backlash": 1, "urgency": 8},
                "rival": {"progress": 1},
            },
        },
        objective_scores={
            "fun": 0.79,
            "coherence": 0.77,
            "character_persuasiveness": 0.76,
            "pacing": 0.74,
            "retention": 0.78,
            "emotional_immersion": 0.75,
            "information_design": 0.73,
            "emotional_payoff": 0.74,
            "long_run_sustainability": 0.72,
            "world_logic": 0.76,
            "chemistry": 0.69,
            "stability": 0.75,
        },
    )

    assert report["passed"] is False
    assert report["failed_checks"] == ["cliffhanger_valid"]


def test_quality_gate_rejects_episode_with_unstable_world_and_payoff_drift_even_if_surface_metrics_pass():
    report = quality_gate_report(
        {
            "hook_score": 0.82,
            "paywall_score": 0.79,
            "emotion_density": 0.75,
            "escalation": 0.78,
            "character_score": 0.76,
            "payoff_score": 0.74,
            "pacing_score": 0.72,
            "chemistry_score": 0.67,
            "repetition_score": 0.18,
        },
        {
            "hook_score_min": 0.7,
            "paywall_score_min": 0.7,
            "emotion_density_min": 0.65,
            "escalation_min": 0.65,
            "character_score_min": 0.66,
            "payoff_score_min": 0.68,
            "pacing_score_min": 0.66,
            "chemistry_score_min": 0.6,
            "repetition_max": 0.35,
            "predicted_retention_min": 0.62,
            "thread_pressure_min": 6,
            "curiosity_debt_min": 5,
            "ceiling_total_min": 58,
            "causal_score_min": 0.72,
            "causal_issues_max": 2,
            "payoff_integrity_min": 0.72,
            "payoff_corruption_flags_max": 0,
            "world_instability_max": 7,
            "conflict_threat_pressure_min": 6,
            "conflict_consequence_level_min": 5,
            "conflict_open_threads_min": 2,
            "protagonist_decision_pressure_min": 7,
            "balanced_objective_min": 0.66,
            "objective_variance_max": 0.33,
            "weakest_objective_axis_min": 0.55,
        },
        retention_state={"unresolved_thread_pressure": 7, "curiosity_debt": 6},
        predicted_retention=0.76,
        content_ceiling={"ceiling_total": 66},
        causal_report={"score": 0.84, "issues": ["relationship_fallout"]},
        story_state={
            "promise_graph": {
                "payoff_integrity": 0.58,
                "payoff_corruption_flags": [{"type": "hook_without_payoff"}],
            },
            "world": {"instability": 9},
            "conflict": {
                "threat_pressure": 8,
                "consequence_level": 7,
                "threads": [
                    {"id": "main", "status": "open"},
                    {"id": "fallout", "status": "open"},
                ],
            },
            "cast": {"protagonist": {"decision_pressure": 8}},
        },
        objective_scores={
            "fun": 0.77,
            "coherence": 0.58,
            "character_persuasiveness": 0.74,
            "pacing": 0.72,
            "retention": 0.7,
            "emotional_immersion": 0.74,
            "information_design": 0.69,
            "emotional_payoff": 0.53,
            "long_run_sustainability": 0.51,
            "world_logic": 0.42,
            "chemistry": 0.66,
            "stability": 0.46,
        },
    )

    assert report["passed"] is False
    assert "payoff_integrity" in report["failed_checks"]
    assert "payoff_corruption_flags" in report["failed_checks"]


def test_quality_gate_rejects_surface_pass_when_pacing_debt_signals_serialization_instability():
    report = quality_gate_report(
        {
            "hook_score": 0.81,
            "paywall_score": 0.77,
            "emotion_density": 0.74,
            "escalation": 0.76,
            "character_score": 0.75,
            "payoff_score": 0.72,
            "pacing_score": 0.74,
            "chemistry_score": 0.66,
            "repetition_score": 0.19,
        },
        {
            "hook_score_min": 0.7,
            "paywall_score_min": 0.7,
            "emotion_density_min": 0.65,
            "escalation_min": 0.65,
            "character_score_min": 0.66,
            "payoff_score_min": 0.68,
            "pacing_score_min": 0.66,
            "chemistry_score_min": 0.6,
            "repetition_max": 0.35,
            "predicted_retention_min": 0.62,
            "thread_pressure_min": 6,
            "curiosity_debt_min": 5,
            "ceiling_total_min": 58,
            "causal_score_min": 0.72,
            "causal_issues_max": 2,
            "payoff_integrity_min": 0.72,
            "payoff_corruption_flags_max": 0,
            "world_instability_max": 7,
            "pacing_release_debt_max": 2,
            "pacing_spike_debt_max": 2,
            "conflict_threat_pressure_min": 6,
            "conflict_consequence_level_min": 5,
            "conflict_open_threads_min": 2,
            "protagonist_decision_pressure_min": 7,
            "balanced_objective_min": 0.66,
            "objective_variance_max": 0.33,
            "weakest_objective_axis_min": 0.55,
        },
        retention_state={"unresolved_thread_pressure": 7, "curiosity_debt": 6},
        predicted_retention=0.72,
        content_ceiling={"ceiling_total": 64},
        causal_report={"score": 0.83, "issues": ["relationship_fallout"]},
        story_state={
            "promise_graph": {"payoff_integrity": 0.79, "payoff_corruption_flags": []},
            "world": {"instability": 5},
            "pacing": {"release_debt": 4, "spike_debt": 0, "rhythm_window": ["spike", "spike", "spike", "pressure"]},
            "conflict": {
                "threat_pressure": 7,
                "consequence_level": 6,
                "threads": [
                    {"id": "main", "status": "open"},
                    {"id": "fallout", "status": "open"},
                ],
            },
            "cast": {"protagonist": {"decision_pressure": 8}},
        },
        objective_scores={
            "fun": 0.76,
            "coherence": 0.75,
            "character_persuasiveness": 0.74,
            "pacing": 0.72,
            "retention": 0.75,
            "emotional_immersion": 0.74,
            "information_design": 0.71,
            "emotional_payoff": 0.69,
            "long_run_sustainability": 0.58,
            "world_logic": 0.73,
            "chemistry": 0.65,
            "stability": 0.7,
        },
    )

    assert report["passed"] is False
    assert "pacing_release_debt" in report["failed_checks"]


def test_quality_gate_rejects_serialized_pattern_crowding_even_if_surface_scores_pass():
    report = quality_gate_report(
        {
            "hook_score": 0.84,
            "paywall_score": 0.8,
            "emotion_density": 0.77,
            "escalation": 0.8,
            "character_score": 0.79,
            "payoff_score": 0.76,
            "pacing_score": 0.74,
            "chemistry_score": 0.68,
            "repetition_score": 0.16,
        },
        {
            "hook_score_min": 0.7,
            "paywall_score_min": 0.7,
            "emotion_density_min": 0.65,
            "escalation_min": 0.65,
            "character_score_min": 0.66,
            "payoff_score_min": 0.68,
            "pacing_score_min": 0.66,
            "chemistry_score_min": 0.6,
            "repetition_max": 0.35,
            "predicted_retention_min": 0.62,
            "thread_pressure_min": 6,
            "curiosity_debt_min": 5,
            "ceiling_total_min": 58,
            "causal_score_min": 0.72,
            "causal_issues_max": 2,
            "payoff_integrity_min": 0.72,
            "payoff_corruption_flags_max": 0,
            "world_instability_max": 7,
            "pattern_overused_events_max": 1,
            "pattern_crowding_max": 5,
            "novelty_debt_max": 4,
            "novelty_guard_min": 4,
            "conflict_threat_pressure_min": 6,
            "conflict_consequence_level_min": 5,
            "conflict_open_threads_min": 2,
            "protagonist_decision_pressure_min": 7,
            "balanced_objective_min": 0.66,
            "objective_variance_max": 0.33,
            "weakest_objective_axis_min": 0.55,
        },
        retention_state={"unresolved_thread_pressure": 8, "curiosity_debt": 7},
        predicted_retention=0.75,
        content_ceiling={"ceiling_total": 67},
        causal_report={"score": 0.86, "issues": ["relationship_fallout"]},
        story_state={
            "promise_graph": {"payoff_integrity": 0.83, "payoff_corruption_flags": []},
            "world": {"instability": 4},
            "pattern_memory": {"overused_events": ["betrayal", "arrival", "power_shift"]},
            "portfolio_memory": {"novelty_guard": 2},
            "portfolio_metrics": {"pattern_crowding": 7, "novelty_debt": 6},
            "conflict": {
                "threat_pressure": 8,
                "consequence_level": 7,
                "threads": [
                    {"id": "main", "status": "open"},
                    {"id": "fallout", "status": "open"},
                ],
            },
            "cast": {"protagonist": {"decision_pressure": 8}},
        },
        objective_scores={
            "fun": 0.79,
            "coherence": 0.77,
            "character_persuasiveness": 0.76,
            "pacing": 0.74,
            "retention": 0.78,
            "emotional_immersion": 0.75,
            "information_design": 0.73,
            "emotional_payoff": 0.74,
            "long_run_sustainability": 0.7,
            "world_logic": 0.77,
            "chemistry": 0.68,
            "stability": 0.74,
        },
    )

    assert report["passed"] is False
    assert "pattern_overused_events" in report["failed_checks"]
    assert "pattern_crowding" in report["failed_checks"]
    assert "novelty_debt" in report["failed_checks"]
    assert "novelty_guard" in report["failed_checks"]


def test_quality_gate_rejects_surface_strong_episode_when_story_pressure_runs_cold():
    report = quality_gate_report(
        {
            "hook_score": 0.83,
            "paywall_score": 0.8,
            "emotion_density": 0.76,
            "escalation": 0.79,
            "character_score": 0.77,
            "payoff_score": 0.75,
            "pacing_score": 0.74,
            "chemistry_score": 0.68,
            "repetition_score": 0.17,
        },
        {
            "hook_score_min": 0.7,
            "paywall_score_min": 0.7,
            "emotion_density_min": 0.65,
            "escalation_min": 0.65,
            "character_score_min": 0.66,
            "payoff_score_min": 0.68,
            "pacing_score_min": 0.66,
            "chemistry_score_min": 0.6,
            "repetition_max": 0.35,
            "predicted_retention_min": 0.62,
            "thread_pressure_min": 6,
            "curiosity_debt_min": 5,
            "ceiling_total_min": 58,
            "causal_score_min": 0.72,
            "causal_issues_max": 2,
            "payoff_integrity_min": 0.72,
            "payoff_corruption_flags_max": 0,
            "world_instability_max": 7,
            "conflict_threat_pressure_min": 6,
            "conflict_consequence_level_min": 5,
            "conflict_open_threads_min": 2,
            "protagonist_decision_pressure_min": 7,
            "balanced_objective_min": 0.66,
            "objective_variance_max": 0.33,
            "weakest_objective_axis_min": 0.55,
        },
        retention_state={"unresolved_thread_pressure": 7, "curiosity_debt": 6},
        predicted_retention=0.76,
        content_ceiling={"ceiling_total": 65},
        causal_report={"score": 0.83, "issues": ["relationship_fallout"]},
        story_state={
            "promise_graph": {"payoff_integrity": 0.82, "payoff_corruption_flags": []},
            "world": {"instability": 4},
            "conflict": {
                "threat_pressure": 4,
                "consequence_level": 3,
                "threads": [{"id": "main", "status": "open"}],
            },
            "cast": {"protagonist": {"decision_pressure": 5}},
        },
        objective_scores={
            "fun": 0.76,
            "coherence": 0.74,
            "character_persuasiveness": 0.75,
            "pacing": 0.73,
            "retention": 0.69,
            "emotional_immersion": 0.74,
            "information_design": 0.71,
            "emotional_payoff": 0.7,
            "long_run_sustainability": 0.67,
            "world_logic": 0.73,
            "chemistry": 0.66,
            "stability": 0.72,
        },
    )

    assert report["passed"] is False
    assert "conflict_threat_pressure" in report["failed_checks"]
    assert "conflict_consequence_level" in report["failed_checks"]
    assert "conflict_open_threads" in report["failed_checks"]
    assert "protagonist_decision_pressure" in report["failed_checks"]


def test_quality_gate_rejects_surface_pass_when_protagonist_momentum_collapses():
    report = quality_gate_report(
        {
            "hook_score": 0.83,
            "paywall_score": 0.79,
            "emotion_density": 0.76,
            "escalation": 0.78,
            "character_score": 0.77,
            "payoff_score": 0.74,
            "pacing_score": 0.73,
            "chemistry_score": 0.67,
            "repetition_score": 0.18,
        },
        {
            "hook_score_min": 0.7,
            "paywall_score_min": 0.7,
            "emotion_density_min": 0.65,
            "escalation_min": 0.65,
            "character_score_min": 0.66,
            "payoff_score_min": 0.68,
            "pacing_score_min": 0.66,
            "chemistry_score_min": 0.6,
            "repetition_max": 0.35,
            "predicted_retention_min": 0.62,
            "thread_pressure_min": 6,
            "curiosity_debt_min": 5,
            "ceiling_total_min": 58,
            "causal_score_min": 0.72,
            "causal_issues_max": 2,
            "payoff_integrity_min": 0.72,
            "payoff_corruption_flags_max": 0,
            "world_instability_max": 7,
            "conflict_threat_pressure_min": 6,
            "conflict_consequence_level_min": 5,
            "conflict_open_threads_min": 2,
            "protagonist_decision_pressure_min": 7,
            "protagonist_momentum_min": 0.52,
            "balanced_objective_min": 0.66,
            "objective_variance_max": 0.33,
            "weakest_objective_axis_min": 0.55,
        },
        retention_state={"unresolved_thread_pressure": 8, "curiosity_debt": 7},
        predicted_retention=0.75,
        content_ceiling={"ceiling_total": 66},
        causal_report={"score": 0.84, "issues": ["relationship_fallout"]},
        story_state={
            "promise_graph": {"payoff_integrity": 0.8, "payoff_corruption_flags": []},
            "world": {"instability": 4},
            "conflict": {
                "threat_pressure": 8,
                "consequence_level": 7,
                "threads": [
                    {"id": "main", "status": "open"},
                    {"id": "fallout", "status": "open"},
                ],
            },
            "cast": {
                "protagonist": {
                    "decision_pressure": 9,
                    "urgency": 9,
                    "progress": 0,
                    "backlash": 4,
                },
                "rival": {"progress": 3},
            },
        },
        objective_scores={
            "fun": 0.78,
            "coherence": 0.77,
            "character_persuasiveness": 0.76,
            "pacing": 0.74,
            "retention": 0.77,
            "emotional_immersion": 0.74,
            "information_design": 0.72,
            "emotional_payoff": 0.73,
            "long_run_sustainability": 0.71,
            "world_logic": 0.75,
            "chemistry": 0.67,
            "stability": 0.74,
        },
    )

    assert report["passed"] is False
    assert "protagonist_momentum" in report["failed_checks"]


def test_quality_gate_rejects_surface_pass_when_objective_profile_is_unbalanced():
    report = quality_gate_report(
        {
            "hook_score": 0.82,
            "paywall_score": 0.78,
            "emotion_density": 0.75,
            "escalation": 0.77,
            "character_score": 0.74,
            "payoff_score": 0.73,
            "pacing_score": 0.72,
            "chemistry_score": 0.68,
            "repetition_score": 0.19,
        },
        {
            "hook_score_min": 0.7,
            "paywall_score_min": 0.7,
            "emotion_density_min": 0.65,
            "escalation_min": 0.65,
            "character_score_min": 0.66,
            "payoff_score_min": 0.68,
            "pacing_score_min": 0.66,
            "chemistry_score_min": 0.6,
            "repetition_max": 0.35,
            "predicted_retention_min": 0.62,
            "thread_pressure_min": 6,
            "curiosity_debt_min": 5,
            "ceiling_total_min": 58,
            "causal_score_min": 0.72,
            "causal_issues_max": 2,
            "payoff_integrity_min": 0.72,
            "payoff_corruption_flags_max": 0,
            "world_instability_max": 7,
            "conflict_threat_pressure_min": 6,
            "conflict_consequence_level_min": 5,
            "conflict_open_threads_min": 2,
            "protagonist_decision_pressure_min": 7,
            "balanced_objective_min": 0.66,
            "objective_variance_max": 0.33,
            "weakest_objective_axis_min": 0.55,
        },
        retention_state={"unresolved_thread_pressure": 7, "curiosity_debt": 6},
        predicted_retention=0.75,
        content_ceiling={"ceiling_total": 67},
        causal_report={"score": 0.83, "issues": ["relationship_fallout"]},
        story_state={
            "promise_graph": {"payoff_integrity": 0.8, "payoff_corruption_flags": []},
            "world": {"instability": 4},
            "conflict": {
                "threat_pressure": 8,
                "consequence_level": 7,
                "threads": [
                    {"id": "main", "status": "open"},
                    {"id": "fallout", "status": "open"},
                ],
            },
            "cast": {"protagonist": {"decision_pressure": 8}},
        },
        objective_scores={
            "fun": 0.89,
            "coherence": 0.84,
            "character_persuasiveness": 0.83,
            "pacing": 0.81,
            "retention": 0.85,
            "emotional_immersion": 0.8,
            "information_design": 0.79,
            "emotional_payoff": 0.77,
            "long_run_sustainability": 0.54,
            "world_logic": 0.51,
            "chemistry": 0.49,
            "stability": 0.5,
        },
    )

    assert report["passed"] is False
    assert "balanced_objective" in report["failed_checks"]
    assert "weakest_objective_axis" in report["failed_checks"]


def test_quality_gate_rejects_surface_pass_when_retention_topology_runs_thin():
    report = quality_gate_report(
        {
            "hook_score": 0.84,
            "paywall_score": 0.79,
            "emotion_density": 0.76,
            "escalation": 0.78,
            "character_score": 0.77,
            "payoff_score": 0.74,
            "pacing_score": 0.73,
            "chemistry_score": 0.68,
            "repetition_score": 0.17,
        },
        {
            "hook_score_min": 0.7,
            "paywall_score_min": 0.7,
            "emotion_density_min": 0.65,
            "escalation_min": 0.65,
            "character_score_min": 0.66,
            "payoff_score_min": 0.68,
            "pacing_score_min": 0.66,
            "chemistry_score_min": 0.6,
            "repetition_max": 0.35,
            "predicted_retention_min": 0.62,
            "thread_pressure_min": 6,
            "curiosity_debt_min": 5,
            "threat_proximity_min": 5,
            "payoff_debt_min": 2,
            "fallout_pressure_min": 4,
            "chemistry_pressure_min": 4,
            "information_gap_min": 4,
            "retention_sustainability_min": 5,
            "ceiling_total_min": 58,
            "causal_score_min": 0.72,
            "causal_issues_max": 2,
            "payoff_integrity_min": 0.72,
            "payoff_corruption_flags_max": 0,
            "world_instability_max": 7,
            "conflict_threat_pressure_min": 6,
            "conflict_consequence_level_min": 5,
            "conflict_open_threads_min": 2,
            "protagonist_decision_pressure_min": 7,
            "balanced_objective_min": 0.66,
            "objective_variance_max": 0.33,
            "weakest_objective_axis_min": 0.55,
        },
        retention_state={
            "unresolved_thread_pressure": 7,
            "curiosity_debt": 6,
            "threat_proximity": 4,
            "payoff_debt": 1,
            "fallout_pressure": 2,
            "chemistry_pressure": 2,
            "information_gap": 2,
            "sustainability": 4,
        },
        predicted_retention=0.74,
        content_ceiling={"ceiling_total": 66},
        causal_report={"score": 0.85, "issues": ["relationship_fallout"]},
        story_state={
            "promise_graph": {"payoff_integrity": 0.81, "payoff_corruption_flags": []},
            "world": {"instability": 4},
            "conflict": {
                "threat_pressure": 8,
                "consequence_level": 7,
                "threads": [
                    {"id": "main", "status": "open"},
                    {"id": "fallout", "status": "open"},
                ],
            },
            "cast": {"protagonist": {"decision_pressure": 8}},
        },
        objective_scores={
            "fun": 0.79,
            "coherence": 0.77,
            "character_persuasiveness": 0.76,
            "pacing": 0.74,
            "retention": 0.76,
            "emotional_immersion": 0.75,
            "information_design": 0.73,
            "emotional_payoff": 0.74,
            "long_run_sustainability": 0.72,
            "world_logic": 0.76,
            "chemistry": 0.68,
            "stability": 0.75,
        },
    )

    assert report["passed"] is False
    assert "threat_proximity" in report["failed_checks"]
    assert "payoff_debt" in report["failed_checks"]
    assert "fallout_pressure" in report["failed_checks"]
    assert "chemistry_pressure" in report["failed_checks"]
    assert "information_gap" in report["failed_checks"]
    assert "sustainability" in report["failed_checks"]


def test_quality_gate_rejects_single_thread_conflict_spike_even_if_surface_scores_pass():
    report = quality_gate_report(
        {
            "hook_score": 0.84,
            "paywall_score": 0.79,
            "emotion_density": 0.76,
            "escalation": 0.8,
            "character_score": 0.77,
            "payoff_score": 0.74,
            "pacing_score": 0.73,
            "chemistry_score": 0.67,
            "repetition_score": 0.17,
        },
        {
            "hook_score_min": 0.7,
            "paywall_score_min": 0.7,
            "emotion_density_min": 0.65,
            "escalation_min": 0.65,
            "character_score_min": 0.66,
            "payoff_score_min": 0.68,
            "pacing_score_min": 0.66,
            "chemistry_score_min": 0.6,
            "repetition_max": 0.35,
            "predicted_retention_min": 0.62,
            "thread_pressure_min": 6,
            "curiosity_debt_min": 5,
            "ceiling_total_min": 58,
            "causal_score_min": 0.72,
            "causal_issues_max": 2,
            "payoff_integrity_min": 0.72,
            "payoff_corruption_flags_max": 0,
            "world_instability_max": 7,
            "conflict_threat_pressure_min": 6,
            "conflict_consequence_level_min": 5,
            "conflict_open_threads_min": 2,
            "protagonist_decision_pressure_min": 7,
            "balanced_objective_min": 0.66,
            "objective_variance_max": 0.33,
            "weakest_objective_axis_min": 0.55,
        },
        retention_state={"unresolved_thread_pressure": 7, "curiosity_debt": 6},
        predicted_retention=0.76,
        content_ceiling={"ceiling_total": 66},
        causal_report={"score": 0.84, "issues": ["relationship_fallout"]},
        story_state={
            "promise_graph": {"payoff_integrity": 0.8, "payoff_corruption_flags": []},
            "world": {"instability": 4},
            "conflict": {
                "threat_pressure": 8,
                "consequence_level": 7,
                "threads": [
                    {"id": "main", "status": "open"},
                    {"id": "paid_off", "status": "resolved"},
                ],
            },
            "cast": {"protagonist": {"decision_pressure": 8}},
        },
        objective_scores={
            "fun": 0.79,
            "coherence": 0.77,
            "character_persuasiveness": 0.75,
            "pacing": 0.74,
            "retention": 0.77,
            "emotional_immersion": 0.75,
            "information_design": 0.72,
            "emotional_payoff": 0.74,
            "long_run_sustainability": 0.7,
            "world_logic": 0.76,
            "chemistry": 0.67,
            "stability": 0.74,
        },
    )

    assert report["passed"] is False
    assert report["failed_checks"] == ["conflict_open_threads"]


def test_projected_episode_state_updates_payoff_pressure_without_mutating_baseline():
    state = {}
    cfg = {
        "project": {"platform": "KakaoPage", "genre_bucket": "A"},
        "novel": {"paywall_window": [20, 30], "early_focus_episodes": 5},
    }
    ensure_story_state(state, cfg=cfg, outline="배신당한 황자가 제국을 되찾는다")

    before_story = state["story_state_v2"]
    projected = _project_episode_state(
        state,
        cfg=cfg,
        episode=1,
        event_plan={"type": "betrayal"},
        cliffhanger_plan={"mode": "choice_lock", "open_question": "누가 먼저 무너질까"},
        score_obj={"hook_score": 0.76, "escalation": 0.78, "emotion_density": 0.72, "payoff_score": 0.42},
    )

    assert before_story["promise_graph"]["unresolved_count"] == 0
    assert state["story_state_v2"]["promise_graph"]["unresolved_count"] == 0
    assert projected["story_state_v2"]["promise_graph"]["unresolved_count"] >= 1
    assert projected["story_state_v2"]["market"]["market_signals"]
    assert not state["story_state_v2"]["market"]["market_signals"]


def test_projected_episode_state_rebuilds_retention_from_projected_pressure():
    state = {}
    cfg = {
        "project": {"platform": "KakaoPage", "genre_bucket": "A"},
        "novel": {"paywall_window": [20, 30], "early_focus_episodes": 5},
    }
    ensure_story_state(state, cfg=cfg, outline="배신당한 황자가 제국을 되찾는다")
    state["retention_engine"] = {"unresolved_thread_pressure": 0, "curiosity_debt": 0, "fallout_pressure": 0}

    projected = _project_episode_state(
        state,
        cfg=cfg,
        episode=2,
        event_plan={
            "type": "betrayal",
            "carryover_pressure": 9,
            "consequence": "핵심 관계가 적으로 돌아선다",
        },
        cliffhanger_plan={
            "mode": "choice_lock",
            "open_question": "누가 먼저 무너질까",
            "carryover_pressure": 8,
        },
        score_obj={"hook_score": 0.79, "escalation": 0.82, "emotion_density": 0.74, "payoff_score": 0.45},
    )

    assert state["retention_engine"] == {"unresolved_thread_pressure": 0, "curiosity_debt": 0, "fallout_pressure": 0}
    assert projected["retention_engine"]["unresolved_thread_pressure"] >= 7
    assert projected["retention_engine"]["curiosity_debt"] >= 9
    assert projected["retention_engine"]["fallout_pressure"] >= 5


def test_quality_gate_accepts_surface_strong_episode_with_readable_prose():
    readable_text = (
        "황자는 무너진 회랑에서 멈춰 섰다. 인장을 깨면 스승을 살릴 수 있었지만, 왕가의 권위는 되돌릴 수 없게 흔들린다. "
        "그는 망설인 끝에 인장을 부쉈고, 감춰졌던 진실이 피처럼 번졌다.\n\n"
        "동맹은 그 대가를 본 순간 칼끝을 거두지 못했다. 황자는 복수를 밀어붙일지, 무너지는 질서를 먼저 붙들지 선택해야 했다. "
        "하지만 마지막 문이 열리기 직전 불빛이 꺼졌고, 배신자의 이름은 아직 누구의 입에서도 나오지 않았다."
    )

    report = quality_gate_report(
        {
            "hook_score": 0.84,
            "paywall_score": 0.79,
            "emotion_density": 0.77,
            "escalation": 0.8,
            "character_score": 0.78,
            "payoff_score": 0.75,
            "pacing_score": 0.74,
            "chemistry_score": 0.69,
            "repetition_score": 0.16,
        },
        {
            "hook_score_min": 0.7,
            "paywall_score_min": 0.7,
            "emotion_density_min": 0.65,
            "escalation_min": 0.65,
            "character_score_min": 0.66,
            "payoff_score_min": 0.68,
            "pacing_score_min": 0.66,
            "chemistry_score_min": 0.6,
            "repetition_max": 0.35,
            "prose_readability_min": 0.62,
            "predicted_retention_min": 0.62,
            "thread_pressure_min": 6,
            "curiosity_debt_min": 5,
            "ceiling_total_min": 58,
            "causal_score_min": 0.72,
            "causal_issues_max": 2,
            "payoff_integrity_min": 0.72,
            "payoff_corruption_flags_max": 0,
            "world_instability_max": 7,
            "conflict_threat_pressure_min": 6,
            "conflict_consequence_level_min": 5,
            "conflict_open_threads_min": 2,
            "protagonist_decision_pressure_min": 7,
            "balanced_objective_min": 0.66,
            "objective_variance_max": 0.33,
            "weakest_objective_axis_min": 0.55,
        },
        episode_text=readable_text,
        retention_state={"unresolved_thread_pressure": 8, "curiosity_debt": 7},
        predicted_retention=0.78,
        content_ceiling={"ceiling_total": 67},
        causal_report={"score": 0.86, "issues": ["relationship_fallout"]},
        story_state={
            "promise_graph": {"payoff_integrity": 0.81, "payoff_corruption_flags": []},
            "world": {"instability": 4},
            "conflict": {
                "threat_pressure": 8,
                "consequence_level": 7,
                "threads": [
                    {"id": "main", "status": "open"},
                    {"id": "betrayal", "status": "open"},
                ],
            },
            "cast": {"protagonist": {"decision_pressure": 8}},
        },
        objective_scores={
            "fun": 0.8,
            "coherence": 0.78,
            "character_persuasiveness": 0.77,
            "pacing": 0.75,
            "retention": 0.79,
            "emotional_immersion": 0.76,
            "information_design": 0.74,
            "emotional_payoff": 0.75,
            "long_run_sustainability": 0.73,
            "world_logic": 0.76,
            "chemistry": 0.69,
            "stability": 0.75,
        },
    )

    assert report["passed"] is True
    assert report["checks"]["prose_readability"] is True
    assert report["prose_report"]["score"] >= 0.62


def test_quality_gate_rejects_surface_pass_when_prose_turns_into_wall_of_text():
    dense_text = (
        "황자는 무너진 회랑에서 숨을 참은 채로 자신이 왜 지금 여기까지 밀려왔는지와 인장을 깨뜨리는 순간 제국의 권위와 스승의 생명과 동맹의 신뢰와 남겨진 사람들의 미래가 동시에 흔들릴 수 있다는 사실을 한 문장으로 되새기며 결정을 늦췄고 "
        "황자는 무너진 회랑에서 숨을 참은 채로 자신이 왜 지금 여기까지 밀려왔는지와 인장을 깨뜨리는 순간 제국의 권위와 스승의 생명과 동맹의 신뢰와 남겨진 사람들의 미래가 동시에 흔들릴 수 있다는 사실을 한 문장으로 되새기며 결정을 늦췄고 "
        "황자는 무너진 회랑에서 숨을 참은 채로 자신이 왜 지금 여기까지 밀려왔는지와 인장을 깨뜨리는 순간 제국의 권위와 스승의 생명과 동맹의 신뢰와 남겨진 사람들의 미래가 동시에 흔들릴 수 있다는 사실을 한 문장으로 되새기며 결정을 늦췄고 "
        "황자는 무너진 회랑에서 숨을 참은 채로 자신이 왜 지금 여기까지 밀려왔는지와 인장을 깨뜨리는 순간 제국의 권위와 스승의 생명과 동맹의 신뢰와 남겨진 사람들의 미래가 동시에 흔들릴 수 있다는 사실을 한 문장으로 되새기며 결정을 늦췄다."
    )

    report = quality_gate_report(
        {
            "hook_score": 0.84,
            "paywall_score": 0.79,
            "emotion_density": 0.76,
            "escalation": 0.79,
            "character_score": 0.77,
            "payoff_score": 0.74,
            "pacing_score": 0.73,
            "chemistry_score": 0.68,
            "repetition_score": 0.17,
        },
        {
            "hook_score_min": 0.7,
            "paywall_score_min": 0.7,
            "emotion_density_min": 0.65,
            "escalation_min": 0.65,
            "character_score_min": 0.66,
            "payoff_score_min": 0.68,
            "pacing_score_min": 0.66,
            "chemistry_score_min": 0.6,
            "repetition_max": 0.35,
            "prose_readability_min": 0.62,
            "predicted_retention_min": 0.62,
            "thread_pressure_min": 6,
            "curiosity_debt_min": 5,
            "ceiling_total_min": 58,
            "causal_score_min": 0.72,
            "causal_issues_max": 2,
            "payoff_integrity_min": 0.72,
            "payoff_corruption_flags_max": 0,
            "world_instability_max": 7,
            "conflict_threat_pressure_min": 6,
            "conflict_consequence_level_min": 5,
            "conflict_open_threads_min": 2,
            "protagonist_decision_pressure_min": 7,
            "balanced_objective_min": 0.66,
            "objective_variance_max": 0.33,
            "weakest_objective_axis_min": 0.55,
        },
        episode_text=dense_text,
        retention_state={"unresolved_thread_pressure": 8, "curiosity_debt": 7},
        predicted_retention=0.77,
        content_ceiling={"ceiling_total": 66},
        causal_report={"score": 0.86, "issues": ["relationship_fallout"]},
        story_state={
            "promise_graph": {"payoff_integrity": 0.8, "payoff_corruption_flags": []},
            "world": {"instability": 4},
            "conflict": {
                "threat_pressure": 8,
                "consequence_level": 7,
                "threads": [
                    {"id": "main", "status": "open"},
                    {"id": "betrayal", "status": "open"},
                ],
            },
            "cast": {"protagonist": {"decision_pressure": 8}},
        },
        objective_scores={
            "fun": 0.79,
            "coherence": 0.78,
            "character_persuasiveness": 0.76,
            "pacing": 0.74,
            "retention": 0.78,
            "emotional_immersion": 0.75,
            "information_design": 0.73,
            "emotional_payoff": 0.74,
            "long_run_sustainability": 0.72,
            "world_logic": 0.76,
            "chemistry": 0.68,
            "stability": 0.75,
        },
    )

    assert report["passed"] is False
    assert report["failed_checks"] == ["prose_readability"]
    assert report["prose_report"]["score"] < 0.62
    assert "wall_of_text" in report["prose_report"]["issues"]


def test_quality_gate_rejects_crowded_single_paragraph_even_when_sentences_are_not_long():
    crowded_text = (
        "황자는 부서진 홀에 들어섰다. 제단 밑에서 스승의 피가 아직 식지 않았다. "
        "동맹은 인장을 깨라고 재촉했지만 그 대가를 끝까지 설명하지 않았다. "
        "황자는 사람들을 살리려면 왕가의 권위를 버려야 한다는 사실을 받아들여야 했다. "
        "그 순간 복도를 막고 있던 기사단이 무릎을 꿇으며 누구 편에 설지 답하라고 압박했다. "
        "뒤늦게 도착한 이복동생은 황자의 선택이 곧 반역의 증거가 될 수 있다고 속삭였다. "
        "황자는 칼을 뽑지 못한 채 인장을 쥔 손에 힘만 더 주었다."
    )

    report = quality_gate_report(
        {
            "hook_score": 0.83,
            "paywall_score": 0.79,
            "emotion_density": 0.76,
            "escalation": 0.79,
            "character_score": 0.77,
            "payoff_score": 0.74,
            "pacing_score": 0.73,
            "chemistry_score": 0.67,
            "repetition_score": 0.18,
        },
        {
            "hook_score_min": 0.7,
            "paywall_score_min": 0.7,
            "emotion_density_min": 0.65,
            "escalation_min": 0.65,
            "character_score_min": 0.66,
            "payoff_score_min": 0.68,
            "pacing_score_min": 0.66,
            "chemistry_score_min": 0.6,
            "repetition_max": 0.35,
            "prose_readability_min": 0.62,
            "predicted_retention_min": 0.62,
            "thread_pressure_min": 6,
            "curiosity_debt_min": 5,
            "ceiling_total_min": 58,
            "causal_score_min": 0.72,
            "causal_issues_max": 2,
            "payoff_integrity_min": 0.72,
            "payoff_corruption_flags_max": 0,
            "world_instability_max": 7,
            "conflict_threat_pressure_min": 6,
            "conflict_consequence_level_min": 5,
            "conflict_open_threads_min": 2,
            "protagonist_decision_pressure_min": 7,
            "balanced_objective_min": 0.66,
            "objective_variance_max": 0.33,
            "weakest_objective_axis_min": 0.55,
        },
        episode_text=crowded_text,
        retention_state={"unresolved_thread_pressure": 8, "curiosity_debt": 7},
        predicted_retention=0.76,
        content_ceiling={"ceiling_total": 66},
        causal_report={"score": 0.84, "issues": ["relationship_fallout"]},
        story_state={
            "promise_graph": {"payoff_integrity": 0.8, "payoff_corruption_flags": []},
            "world": {"instability": 4},
            "conflict": {
                "threat_pressure": 8,
                "consequence_level": 7,
                "threads": [
                    {"id": "main", "status": "open"},
                    {"id": "betrayal", "status": "open"},
                ],
            },
            "cast": {"protagonist": {"decision_pressure": 8}},
        },
        objective_scores={
            "fun": 0.79,
            "coherence": 0.78,
            "character_persuasiveness": 0.76,
            "pacing": 0.74,
            "retention": 0.77,
            "emotional_immersion": 0.75,
            "information_design": 0.73,
            "emotional_payoff": 0.74,
            "long_run_sustainability": 0.72,
            "world_logic": 0.76,
            "chemistry": 0.68,
            "stability": 0.75,
        },
    )

    assert report["passed"] is False
    assert report["failed_checks"] == ["prose_readability"]
    assert report["prose_report"]["score"] < 0.62
    assert "crowded_paragraphs" in report["prose_report"]["issues"]
