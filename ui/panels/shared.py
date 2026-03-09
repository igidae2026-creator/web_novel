import streamlit as st

from engine.control_console import (
    execute_policy_action,
    load_runtime_snapshot,
    request_policy_action,
    requires_confirmation,
    restore_last_stable_config,
    save_runtime_snapshot,
)
from engine.runtime_config import DEFAULT_RUNTIME_CONFIG_PATH, save_runtime_config

LABELS = {
    "ko": {
        "title": "웹소설 자동화 운영 콘솔",
        "dashboard": "운영 대시보드",
        "project_setup": "프로젝트 설정",
        "generation": "생성 제어",
        "portfolio": "트랙 / 포트폴리오",
        "release": "릴리즈 스케줄러",
        "quality": "품질 / 신뢰성",
        "outputs": "출력 검토",
        "simple": "간단 모드",
        "advanced": "고급 모드",
        "mode": "모드",
        "project": "프로젝트",
        "loop_status": "루프 상태",
        "active_tracks": "활성 트랙 수",
        "balanced_total": "balanced_total",
        "drift": "드리프트",
        "latest_warning": "최신 경고",
        "latest_error": "최신 오류",
        "next_action": "다음 권장 액션",
        "warning_panel": "경고 / 오류 패널",
        "confirm": "실행 확인",
        "execute": "실행",
        "no_data": "표시할 데이터가 없습니다.",
        "korean_first": "기본 언어는 한국어입니다.",
        "save_config": "현재 설정 저장",
        "save_snapshot": "현재 스냅샷 저장",
        "load_snapshot": "스냅샷 불러오기",
        "restore_stable": "마지막 안정 설정 복원",
        "one_click_generate": "원클릭 생성",
        "one_click_auto_loop": "원클릭 자동 루프",
        "one_click_release_plan": "원클릭 릴리즈 계획",
        "one_click_reliability": "원클릭 신뢰성 점검",
        "one_click_pause": "원클릭 안전 일시정지",
    },
    "en": {
        "title": "Web-Novel Operator Console",
        "dashboard": "Dashboard",
        "project_setup": "Project Setup",
        "generation": "Generation Control",
        "portfolio": "Track / Portfolio",
        "release": "Release Scheduler",
        "quality": "Quality / Reliability",
        "outputs": "Outputs Review",
        "simple": "Simple",
        "advanced": "Advanced",
        "mode": "Mode",
        "project": "Project",
        "loop_status": "Loop status",
        "active_tracks": "Active tracks",
        "balanced_total": "balanced_total",
        "drift": "Drift",
        "latest_warning": "Latest warning",
        "latest_error": "Latest error",
        "next_action": "Next recommended action",
        "warning_panel": "Warnings / Errors",
        "confirm": "Confirmation",
        "execute": "Execute",
        "no_data": "No data available.",
        "korean_first": "Korean is the default language.",
        "save_config": "Save Config",
        "save_snapshot": "Save Snapshot",
        "load_snapshot": "Load Snapshot",
        "restore_stable": "Restore Stable",
        "one_click_generate": "One-click Generate",
        "one_click_auto_loop": "One-click Auto Loop",
        "one_click_release_plan": "One-click Release Plan",
        "one_click_reliability": "One-click Reliability Check",
        "one_click_pause": "One-click Safe Pause",
    },
}

PLATFORMS = ["Joara", "Munpia", "NaverSeries", "KakaoPage", "Ridibooks", "Novelpia"]


def t(key: str, lang: str) -> str:
    return LABELS.get(lang, LABELS["ko"]).get(key, key)


def parse_horizons(text: str) -> list[int]:
    return [int(item.strip()) for item in str(text or "").split(",") if item.strip().isdigit()]


def session_defaults_from_runtime(runtime_cfg: dict) -> dict:
    project_setup = dict(runtime_cfg.get("project_setup", {}) or {})
    evaluation = dict(runtime_cfg.get("evaluation", {}) or {})
    release_cadence = dict(runtime_cfg.get("release_cadence", {}) or {})
    portfolio = dict(runtime_cfg.get("portfolio", {}) or {})
    release_scheduler = dict(runtime_cfg.get("release_scheduler", {}) or {})
    reliability = dict(runtime_cfg.get("reliability", {}) or {})
    presets = dict(runtime_cfg.get("presets", {}) or {})
    console = dict(runtime_cfg.get("console", {}) or {})
    snapshots = dict((runtime_cfg.get("snapshots", {}) or {}).get("saved", {}) or {})
    return {
        "console_language": str(console.get("language", "ko")),
        "console_mode": str(console.get("mode", "simple")),
        "project_preset": str(presets.get("project", "Steady Series")),
        "platform_preset": str(presets.get("platform", "Munpia Standard")),
        "genre_preset": str(presets.get("genre", "A")),
        "project_name": str(project_setup.get("name", "METAOS_Project")),
        "platform_name": str(project_setup.get("platform", "Munpia")),
        "genre_bucket": str(project_setup.get("genre_bucket", "A")),
        "sub_engine": str(project_setup.get("sub_engine", "AUTO")),
        "target_total_episodes": int(project_setup.get("target_total_episodes", 300)),
        "early_focus_episodes": int(project_setup.get("early_focus_episodes", 3)),
        "generation_enabled": bool(runtime_cfg.get("generation_enabled", True)),
        "track_count": int(runtime_cfg.get("track_count", 6)),
        "revision_passes": int(evaluation.get("max_revision_passes", 2)),
        "repair_budget": int(evaluation.get("causal_repair_retry_budget", 2)),
        "viral_required": bool(evaluation.get("viral_required", True)),
        "portfolio_mode": str(portfolio.get("mode", "balanced")),
        "cadence_mode": str(release_cadence.get("mode", "queue_loop")),
        "steps_per_run": int(release_cadence.get("steps_per_run", 1)),
        "scheduler_strategy": str(release_scheduler.get("strategy", "adaptive")),
        "window_count": int(release_scheduler.get("window_count", 6)),
        "drift_check_enabled": bool(reliability.get("drift_check_enabled", True)),
        "horizons_text": ",".join(str(item) for item in reliability.get("simulation_horizons", [30, 60, 120])),
        "snapshot_name": "operator_snapshot",
        "selected_snapshot": "(none)" if not snapshots else sorted(snapshots.keys())[0],
        "override_track": "(none)",
        "override_note": "",
        "review_choice": "",
    }


def initialize_session_state(runtime_cfg: dict):
    for key, value in session_defaults_from_runtime(runtime_cfg).items():
        st.session_state.setdefault(key, value)


def sync_session_state(runtime_cfg: dict):
    for key, value in session_defaults_from_runtime(runtime_cfg).items():
        st.session_state[key] = value


def build_runtime_payload_from_values(base_runtime_cfg: dict, values: dict) -> dict:
    payload = {
        "console": {
            "language": values["console_language"],
            "mode": values["console_mode"],
            "current_project": values["project_name"],
        },
        "presets": {
            "project": values["project_preset"],
            "platform": values["platform_preset"],
            "genre": values["genre_preset"],
        },
        "project_setup": {
            "name": values["project_name"],
            "platform": values["platform_name"],
            "genre_bucket": values["genre_bucket"],
            "sub_engine": values["sub_engine"],
            "target_total_episodes": int(values["target_total_episodes"]),
            "early_focus_episodes": int(values["early_focus_episodes"]),
        },
        "generation_enabled": bool(values["generation_enabled"]),
        "track_count": int(values["track_count"]),
        "generation_control": {"flow": "track_queue", "auto_outline": True},
        "release_cadence": {"mode": values["cadence_mode"], "steps_per_run": int(values["steps_per_run"])},
        "portfolio": {"mode": values["portfolio_mode"]},
        "release_scheduler": {"strategy": values["scheduler_strategy"], "window_count": int(values["window_count"])},
        "evaluation": {
            "max_revision_passes": int(values["revision_passes"]),
            "causal_repair_retry_budget": int(values["repair_budget"]),
            "viral_required": bool(values["viral_required"]),
        },
        "reliability": {
            "simulation_horizons": parse_horizons(values["horizons_text"]),
            "drift_check_enabled": bool(values["drift_check_enabled"]),
        },
        "projects": base_runtime_cfg.get("projects", {}),
        "snapshots": base_runtime_cfg.get("snapshots", {}),
        "review_state": base_runtime_cfg.get("review_state", {}),
        "operator_overrides": base_runtime_cfg.get("operator_overrides", {}),
    }
    return payload


def build_runtime_payload(base_runtime_cfg: dict) -> dict:
    values = {key: st.session_state.get(key) for key in session_defaults_from_runtime(base_runtime_cfg).keys()}
    return build_runtime_payload_from_values(base_runtime_cfg, values)


def persist_runtime_config(payload: dict) -> dict:
    saved = save_runtime_config(payload, path=DEFAULT_RUNTIME_CONFIG_PATH)
    st.session_state["console_runtime_saved"] = saved
    return saved


def request_or_execute_action(action: str, runtime_payload: dict, loop_active: bool, policy_action_path: str, extra_payload: dict | None = None):
    payload = dict(extra_payload or {})
    if requires_confirmation(action, loop_active=loop_active):
        st.session_state["pending_action"] = {
            "action": action,
            "runtime_payload": runtime_payload,
            "extra_payload": payload,
        }
        return None
    saved = persist_runtime_config(runtime_payload)
    request_policy_action(action, payload=payload, path=saved["paths"]["policy_action_path"])
    result = execute_policy_action(
        config_path="config.yaml",
        runtime_config_path=DEFAULT_RUNTIME_CONFIG_PATH,
        policy_action_path=saved["paths"]["policy_action_path"],
    )
    st.session_state["last_action_result"] = result
    return result


def execute_pending_action():
    pending = st.session_state.get("pending_action")
    if not pending:
        return None
    saved = persist_runtime_config(pending["runtime_payload"])
    request_policy_action(pending["action"], payload=pending["extra_payload"], path=saved["paths"]["policy_action_path"])
    result = execute_policy_action(
        config_path="config.yaml",
        runtime_config_path=DEFAULT_RUNTIME_CONFIG_PATH,
        policy_action_path=saved["paths"]["policy_action_path"],
    )
    st.session_state["last_action_result"] = result
    st.session_state.pop("pending_action", None)
    return result


def save_snapshot_from_session(base_runtime_cfg: dict):
    payload = build_runtime_payload(base_runtime_cfg)
    updated = save_runtime_snapshot(payload, st.session_state.get("snapshot_name", "operator_snapshot"))
    persist_runtime_config(updated)
    return updated


def load_snapshot_to_session(base_runtime_cfg: dict):
    updated = load_runtime_snapshot(build_runtime_payload(base_runtime_cfg), st.session_state.get("selected_snapshot", "(none)"))
    persist_runtime_config(updated)
    sync_session_state(updated)
    return updated


def restore_stable_to_session(base_runtime_cfg: dict):
    updated = restore_last_stable_config(build_runtime_payload(base_runtime_cfg))
    persist_runtime_config(updated)
    sync_session_state(updated)
    return updated
