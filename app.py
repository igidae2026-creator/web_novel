import os
import time
import json
import streamlit as st
from engine.safe_io import safe_copy_bytes, safe_write_text
from engine.runtime_supervisor import load_supervisor_state

from engine.config import load_config, save_config
from engine.state import StateStore
from engine.openai_client import LLM
from engine.cost import CostTracker
from engine.external_rank import ExternalRankSignals
from engine.ceiling import top_percent_from_rank, band_from_top_percent
from engine.strategy import GENRE_SUBENGINES
from engine.pipeline import EpisodeRejectedError, build_outline, generate_episode, ensure_project_dirs
from engine.io_utils import read_text
from engine.runtime_config import (
    DEFAULT_RUNTIME_CONFIG_PATH,
    DEFAULT_SYSTEM_STATUS_PATH,
    configured_loop_steps,
    configured_track_count,
    load_runtime_config,
    load_runtime_config_into_cfg,
    save_runtime_config,
)

from metaos_business.revenue_dashboard import render as render_revenue
from metaos_business.campaign_dashboard import render as render_campaign
from metaos_business.runtime_dashboard import render as render_runtime_dashboard

st.set_page_config(page_title="METAOS FINAL", layout="wide")
st.title("METAOS FINAL — Streamlit Only")

CFG_PATH = "config.yaml"
TRACKS_ROOT = os.path.join("domains", "webnovel", "tracks")
cfg = load_config(CFG_PATH)
runtime_cfg = load_runtime_config()

if not os.getenv("OPENAI_API_KEY"):
    st.error("OPENAI_API_KEY 환경변수가 필요합니다.")
    st.stop()

# Sidebar toggles
with st.sidebar:
    st.header("Toggles")
    cfg["project"]["name"] = st.text_input("Project", cfg["project"]["name"])
    cfg["project"]["platform"] = st.selectbox(
        "Platform",
        ["Joara","Munpia","NaverSeries","KakaoPage","Ridibooks","Novelpia"],
        index=["Joara","Munpia","NaverSeries","KakaoPage","Ridibooks","Novelpia"].index(cfg["project"]["platform"])
    )
    cfg["project"]["genre_bucket"] = st.selectbox(
        "Genre bucket",
        list("ABCDEFGHI"),
        index=list("ABCDEFGHI").index(cfg["project"]["genre_bucket"])
    )

    bucket = cfg["project"]["genre_bucket"]
    options = ["AUTO"] + [s.key for s in GENRE_SUBENGINES[bucket]]
    labels = {"AUTO":"AUTO"} | {s.key: f"{s.key} — {s.label}" for s in GENRE_SUBENGINES[bucket]}
    cur = cfg["project"].get("sub_engine","AUTO")
    if cur not in options:
        cur = "AUTO"
    picked = st.selectbox("Sub-engine", options, index=options.index(cur), format_func=lambda k: labels.get(k,k))
    cfg["project"]["sub_engine"] = picked

    cfg["model"]["mode"] = st.selectbox("Mode", ["batch","priority"], index=["batch","priority"].index(cfg["model"]["mode"]))
    cfg["phase"] = st.selectbox("Phase", ["STABILIZE","BOOST"], index=["STABILIZE","BOOST"].index(str(cfg.get("phase","STABILIZE")).upper()))

    st.divider()
    st.subheader("External")
    st.subheader("Market")
    cfg.setdefault("market", {})
    cfg["market"]["out_of_chart_policy"] = st.selectbox(
        "Out-of-chart policy",
        ["NA","HOLD_LAST","SET_101"],
        index=["NA","HOLD_LAST","SET_101"].index(str(cfg.get("market",{}).get("out_of_chart_policy","HOLD_LAST")).upper())
    )
    cfg["market"]["window_days"] = st.slider("Market window (days)", 3, 14, int(cfg.get("market",{}).get("window_days",7)), 1)
    st.divider()

    cfg["external"]["enable_external_adjustment"] = st.toggle("Use external rank signals", value=bool(cfg["external"]["enable_external_adjustment"]))
    cfg["external"]["external_weight"] = st.slider("External weight", 0.0, 1.0, float(cfg["external"].get("external_weight", 0.65)), 0.05)
    cfg["external"]["slope_window"] = st.slider("Slope window", 2, 14, int(cfg["external"].get("slope_window", 5)), 1)

    st.divider()
    st.subheader("Limits")
    cfg["limits"]["token_ceiling_total"] = st.number_input("Token ceiling", min_value=100000, max_value=20000000, value=int(cfg["limits"]["token_ceiling_total"]), step=50000)
    cfg["limits"]["sleep_seconds_between_calls"] = st.slider("Sleep between calls", 0.0, 1.0, float(cfg["limits"]["sleep_seconds_between_calls"]), 0.02)
    cfg["limits"]["max_revision_passes"] = st.slider("Revision passes", 1, 3, int(cfg["limits"].get("max_revision_passes", 2)), 1)

    st.divider()
    st.subheader("Novel")
    cfg["novel"]["total_episodes"] = st.number_input("Total episodes", min_value=1, max_value=2000, value=int(cfg["novel"]["total_episodes"]), step=10)
    cfg["novel"]["early_focus_episodes"] = st.number_input("Early focus", min_value=1, max_value=20, value=int(cfg["novel"]["early_focus_episodes"]), step=1)

    st.divider()
    
    st.divider()
    st.subheader("WebNovel Track")
    # Track id is platform+bucket (simple) unless overridden
    default_track = f"{cfg['project']['platform']}_{cfg['project']['genre_bucket']}".lower()
    cfg.setdefault("track", {})
    cfg["track"]["id"] = st.text_input("Track ID", value=str(cfg["track"].get("id", default_track)))

    st.divider()
    st.subheader("Runtime Control")
    runtime_track_count = st.number_input(
        "Track count",
        min_value=1,
        max_value=54,
        value=int(runtime_cfg.get("track_count", 6)),
        step=1,
    )
    runtime_steps_per_run = st.number_input(
        "Release cadence",
        min_value=1,
        max_value=20,
        value=int(runtime_cfg.get("release_cadence", {}).get("steps_per_run", 1)),
        step=1,
    )
    portfolio_modes = ["balanced", "focused", "explore"]
    runtime_portfolio_mode = st.selectbox(
        "Portfolio mode",
        portfolio_modes,
        index=portfolio_modes.index(str(runtime_cfg.get("portfolio", {}).get("mode", "balanced")))
        if str(runtime_cfg.get("portfolio", {}).get("mode", "balanced")) in portfolio_modes
        else 0,
    )
    runtime_generation_enabled = st.toggle(
        "Generation enabled",
        value=bool(runtime_cfg.get("generation_enabled", True)),
    )
    runtime_revision_passes = st.slider(
        "Runtime revision passes",
        1,
        3,
        int(runtime_cfg.get("evaluation", {}).get("max_revision_passes", cfg["limits"].get("max_revision_passes", 2))),
        1,
    )
    runtime_repair_budget = st.slider(
        "Runtime repair budget",
        1,
        4,
        int(runtime_cfg.get("evaluation", {}).get("causal_repair_retry_budget", runtime_revision_passes)),
        1,
    )
    runtime_viral_required = st.toggle(
        "Runtime viral required",
        value=bool(runtime_cfg.get("evaluation", {}).get("viral_required", cfg.get("quality", {}).get("viral_required", True))),
    )

    if st.button("Save config.yaml"):
        save_config(CFG_PATH, cfg)
        st.success("Saved.")
    if st.button("Save runtime_config.json"):
        save_runtime_config(
            {
                "generation_enabled": bool(runtime_generation_enabled),
                "track_count": int(runtime_track_count),
                "release_cadence": {"mode": "queue_loop", "steps_per_run": int(runtime_steps_per_run)},
                "portfolio": {"mode": runtime_portfolio_mode},
                "evaluation": {
                    "max_revision_passes": int(runtime_revision_passes),
                    "causal_repair_retry_budget": int(runtime_repair_budget),
                    "viral_required": bool(runtime_viral_required),
                },
            },
            path=DEFAULT_RUNTIME_CONFIG_PATH,
            safe_mode=bool(cfg.get("safe_mode", False)),
            project_dir_for_backup="outputs",
        )
        st.success("Saved runtime_config.json")

runtime_payload = {
    "generation_enabled": bool(runtime_generation_enabled),
    "track_count": int(runtime_track_count),
    "release_cadence": {"mode": "queue_loop", "steps_per_run": int(runtime_steps_per_run)},
    "portfolio": {"mode": runtime_portfolio_mode},
    "evaluation": {
        "max_revision_passes": int(runtime_revision_passes),
        "causal_repair_retry_budget": int(runtime_repair_budget),
        "viral_required": bool(runtime_viral_required),
    },
}

out_dir = ensure_project_dirs(cfg)
state_path = os.path.join(out_dir, "state.json")
state = StateStore(state_path, safe_mode=bool(cfg.get('safe_mode', False)), project_dir_for_backup=out_dir)
state.load()

llm = LLM(cfg)
cost = CostTracker(cfg, out_dir)
ext = ExternalRankSignals(cfg)

tabs = st.tabs(["Generation", "Tracks", "MaxCeiling", "Revenue", "Campaigns"])

with tabs[0]:
    st.subheader("Rank-based top% (chart-relative)")
    snap = ext.latest(cfg["project"]["platform"], cfg["project"]["genre_bucket"])
    c1, c2, c3, c4, c5 = st.columns(5)
    if snap and snap.get("chart_size") and snap.get("rank"):
        N = int(snap["chart_size"])
        r = int(snap["rank"])
        p = top_percent_from_rank(r, N)
        band = band_from_top_percent(p)
        slope = ext.slope(cfg["project"]["platform"], cfg["project"]["genre_bucket"], window=int(cfg["external"].get("slope_window", 5)))
        c1.metric("N", N); c2.metric("Rank", r); c3.metric("Top %", f"{p:.2f}%"); c4.metric("Band", band); c5.metric("Slope", f"{slope:+.3f}")
        st.caption(f"date={snap.get('date')} event={snap.get('event_flag')} notes={snap.get('notes')}")
    else:
        st.info("data/rank_signals.csv 관측치가 없으면 내부 규칙만 적용됩니다.")

    st.subheader("Upload rank_signals.csv")
    up = st.file_uploader("CSV", type=["csv"], key="rank_csv")
    if up is not None:
        os.makedirs("data", exist_ok=True)
        safe_copy_bytes(cfg["external"]["rank_signals_csv"], up.getbuffer(), safe_mode=bool(cfg.get('safe_mode', False)))
        st.success("Saved rank_signals.csv")
        ext.load()

    left, right = st.columns([1,1])
    with left:
        st.subheader("Controls")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Start Generation"):
                saved_runtime = save_runtime_config(
                    dict(runtime_payload, generation_enabled=True),
                    path=DEFAULT_RUNTIME_CONFIG_PATH,
                    safe_mode=bool(cfg.get("safe_mode", False)),
                    project_dir_for_backup=out_dir,
                )
                runtime_cfg_for_run, _ = load_runtime_config_into_cfg(cfg, DEFAULT_RUNTIME_CONFIG_PATH)
                from engine.track_loader import list_track_dirs
                from engine.track_loop import run_queue_loop
                from engine.track_queue import start_queue
                track_dirs = list_track_dirs(TRACKS_ROOT)
                limited_track_dirs = track_dirs[: configured_track_count(saved_runtime, len(track_dirs) or 1)]
                if limited_track_dirs:
                    start_queue(track_dirs=limited_track_dirs, cfg=runtime_cfg_for_run)
                    ok, msg = run_queue_loop(
                        runtime_cfg_for_run,
                        max_steps=configured_loop_steps(saved_runtime, default_steps=1),
                    )
                    if ok:
                        st.success(msg)
                    else:
                        st.warning(msg)
                else:
                    next_ep = int(state.get("next_episode", 1))
                    try:
                        generate_episode(runtime_cfg_for_run, state, llm, cost, ext, next_ep)
                    except EpisodeRejectedError as exc:
                        st.warning(exc.audit.get("message", f"Episode {next_ep} rejected."))
                    else:
                        state.save()
                        cost.write_summary()
                        st.success(f"Episode {next_ep} saved.")
        with c2:
            if st.button("Stop Generation"):
                save_runtime_config(
                    dict(runtime_payload, generation_enabled=False),
                    path=DEFAULT_RUNTIME_CONFIG_PATH,
                    safe_mode=bool(cfg.get("safe_mode", False)),
                    project_dir_for_backup=out_dir,
                )
                from engine.track_queue import pause_queue
                pause_queue()
                st.info("Generation paused.")
        if st.button("Reset state"):
            state.reset()
            st.success("Reset.")

        if st.button("Generate/Update Outline"):
            outline = build_outline(cfg, state, llm, cost, ext)
            state.save()
            safe_write_text(os.path.join(out_dir, "outline.txt"), outline, safe_mode=bool(cfg.get('safe_mode', False)), project_dir_for_backup=out_dir)
            st.success("Outline saved.")

        next_ep = int(state.get("next_episode", 1))
        st.write(f"Next episode: **{next_ep}** / {int(cfg['novel']['total_episodes'])}")

        if st.button("Generate Next Episode"):
            try:
                generate_episode(cfg, state, llm, cost, ext, next_ep)
            except EpisodeRejectedError as exc:
                st.warning(exc.audit.get("message", f"Episode {next_ep} rejected."))
            else:
                state.save()
                cost.write_summary()
                st.success(f"Episode {next_ep} saved.")

    with right:
        st.subheader("Status")
        st.json(cost.snapshot())
        st.json(state.data)
        render_runtime_dashboard(
            system_status_path=DEFAULT_SYSTEM_STATUS_PATH,
            metrics_path=os.path.join(out_dir, "metrics.jsonl"),
            tracks_root=TRACKS_ROOT,
            standalone_out_dir=out_dir,
            limit=5,
        )
        outline_path = os.path.join(out_dir, "outline.txt")
        if os.path.exists(outline_path):
            with st.expander("Outline preview", expanded=False):
                st.text(read_text(outline_path)[:6000])

with tabs[1]:
    st.subheader("Track Orchestration")
    st.caption("Generate 54 tracks (6 platforms × 9 buckets) safely. No execution, only config/state scaffolding.")
    from engine.track_generator import generate_tracks
    if st.button("Generate 54 Tracks"):
        created = generate_tracks(root_dir="domains/webnovel", project_name=cfg["project"]["name"])
        st.success(f"Created {len(created)} tracks under domains/webnovel/tracks/")
        st.json(created[:10])
    idx_path = os.path.join("domains/webnovel", "tracks", "tracks_index.json")
    if os.path.exists(idx_path):
        with st.expander("tracks_index.json", expanded=False):
            st.json(json.load(open(idx_path, "r", encoding="utf-8")))

    st.divider()
    st.subheader("Select Track")
    st.divider()
    st.subheader("Queue Controls")
    st.divider()
    st.subheader("Stress Test")
    from engine.stress_test import run_stress_test
    st_steps = st.number_input("Stress steps", min_value=10, max_value=10000, value=200, step=50)
    if st.button("Run Stress Test (dry-run)"):
        rep = run_stress_test(cfg, steps=int(st_steps))
        st.json(rep)

    from engine.track_queue import start_queue, pause_queue, resume_queue, load_queue_state
    from engine.track_runner import run_queue_step

    qs = load_queue_state()
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Start Queue"):
            qs = start_queue(cfg=cfg)
            st.success(f"Queue started: {qs.get('status')} ({len(qs.get('track_dirs', []))} tracks)")
    with c2:
        if st.button("Pause Queue"):
            qs = pause_queue()
            st.info("Queue paused")
    with c3:
        if st.button("Resume Queue"):
            qs = resume_queue(cfg=cfg)
            st.info("Queue resumed")

    st.write("Queue state:")
    st.subheader("Recent Events (selected track)")

    st.subheader("Boost History Table")

    st.subheader("Boost History Table (Expanded)")
    import pandas as pd
    rows=[]
    tracks_root=os.path.join("domains","webnovel","tracks")
    if os.path.exists(tracks_root):
        for d in os.listdir(tracks_root):
            td=os.path.join(tracks_root,d)
            bh=os.path.join(td,"outputs","boost_history.json")
            if os.path.exists(bh):
                data=json.load(open(bh,"r",encoding="utf-8"))
                rows.append({
                    "track":d,
                    "last_boost_date":data.get("last_boost_date"),
                    "boost_count":data.get("boost_count",0)
                })
    if rows:
        st.dataframe(pd.DataFrame(rows))
    else:
        st.caption("No boost history yet.")

    if cfg.get("track",{}).get("dir"):
        bh_path = os.path.join(cfg["track"]["dir"],"outputs","boost_history.json")
        if os.path.exists(bh_path):
            st.json(json.load(open(bh_path,"r",encoding="utf-8")))
        else:
            st.caption("No boost_history.json yet. Run rebalance/auto loop first.")

    from engine.event_log import read_recent
    if cfg.get("track", {}).get("dir"):
        ev = read_recent(os.path.join(cfg["track"]["dir"], "outputs"), n=50)
        if ev:
            with st.expander("events.jsonl (last 50)", expanded=False):
                st.json(ev)
        else:
            st.caption("No events yet for this track.")

    st.json(qs)

    from engine.track_queue import progress_info
    pi = progress_info(qs)
    st.write("Queue Progress:")
    st.subheader("Portfolio Summary")
    st.divider()
    st.subheader("Rebalance Portfolio (Grade-driven)")
    st.caption("Rotation-aware boost scheduling; per-track history stored in outputs/boost_history.json")
    from engine.portfolio_orchestrator import rebalance_platform
    if st.button("Rebalance Now"):
        rep = rebalance_platform(cfg, os.path.join("domains","webnovel","tracks"))
        st.json(rep)

    from engine.portfolio_report import summarize_portfolio
    ps = summarize_portfolio()
    st.json(ps)

    st.json(pi)
    from engine.track_runner import retry_current
    if st.button("Retry Current Track"):
        ok,msg = retry_current(cfg)
        if ok:
            st.success(msg)
        else:
            st.warning(msg)


    if st.button("Run One Queue Step (1 track / 1 episode)"):
        ok, msg = run_queue_step(cfg)
        if ok:
            st.success(msg)
        else:
            st.warning(msg)

    st.divider()
    st.subheader("Auto Loop (Safe)")
    from engine.track_loop import run_queue_loop
    steps = st.number_input(
        "Steps per click",
        min_value=1,
        max_value=20,
        value=configured_loop_steps(runtime_cfg, default_steps=3),
        step=1,
    )
    if st.button("Run Auto Loop (N steps)"):
        ok2, msg2 = run_queue_loop(cfg, max_steps=int(steps))
        (st.success(msg2) if ok2 else st.warning(msg2))
    hist_path = os.path.join("domains","webnovel","tracks","queue_history.json")
    if os.path.exists(hist_path):
        with st.expander("Queue History", expanded=False):
            st.json(json.load(open(hist_path, "r", encoding="utf-8")))

    from engine.track_loader import list_track_dirs
    track_dirs = list_track_dirs(TRACKS_ROOT)
    chosen = st.selectbox("Track directory", ["(none)"] + track_dirs)
    if chosen != "(none)":
        cfg.setdefault("track", {})
        cfg["track"]["dir"] = chosen
        st.success(f"Selected track: {chosen}")


with tabs[2]:
    st.subheader("MAX CEILING — Auto profiles from your materials")
    st.caption("Upload zips/txt. METAOS extracts statistics only (no raw text output) and builds profile constraints.")
    inputs_dir = "corpus_inputs"
    os.makedirs(inputs_dir, exist_ok=True)
    files = st.file_uploader("Upload materials", type=["zip","txt","md"], accept_multiple_files=True, key="mc_files")
    if files:
        for uf in files:
            safe_copy_bytes(os.path.join(inputs_dir, uf.name), uf.getbuffer(), safe_mode=bool(cfg.get("safe_mode", False)))
        st.success(f"Saved {len(files)} file(s) to {inputs_dir}/")
    from metaos_corpus.profile_builder import build_profiles
    if st.button("Build/Refresh profiles"):
        profiles = build_profiles(inputs_dir=inputs_dir, out_dir=os.path.join("data","profiles"), scratch_dir=os.path.join("data","scratch"), default_platform="GLOBAL")
        st.success(f"Built {len(profiles)} profile group(s).")
    idx = os.path.join("data","profiles","profiles_index.json")
    if os.path.exists(idx):
        st.json(json.load(open(idx, "r", encoding="utf-8")))

with tabs[3]:
    st.subheader("Revenue Inputs")
    rev_up = st.file_uploader("Upload revenue_input.csv", type=["csv"], key="rev_csv")
    rev_path = "data/revenue_input.csv"
    if rev_up is not None:
        os.makedirs("data", exist_ok=True)
        safe_copy_bytes(rev_path, rev_up.getbuffer(), safe_mode=bool(cfg.get('safe_mode', False)))
        st.success("Saved data/revenue_input.csv")
    st.caption("Template: revenue_input_template.csv")
    render_revenue(rev_path)

with tabs[4]:
    st.subheader("Campaign Inputs")
    camp_up = st.file_uploader("Upload campaign_input.csv", type=["csv"], key="camp_csv")
    camp_path = "data/campaign_input.csv"
    if camp_up is not None:
        os.makedirs("data", exist_ok=True)
        safe_copy_bytes(camp_path, camp_up.getbuffer(), safe_mode=bool(cfg.get('safe_mode', False)))
        st.success("Saved data/campaign_input.csv")
    st.caption("Template: campaign_input_template.csv")
    render_campaign(camp_path)


    st.subheader("Certification Report")

    st.subheader("Grade State")
    gs_path = os.path.join(out_dir, "grade_state.json")
    if os.path.exists(gs_path):
        with st.expander("grade_state.json", expanded=False):
            st.json(json.load(open(gs_path, "r", encoding="utf-8")))
    else:
        st.caption("No grade_state.json yet. Generate certification to create it.")


    st.subheader("Certification Trend (Last 5)")

    st.subheader("Certification Charts (Last 20)")
    from engine.cert_viz import load_cert_series, stability_score
    series = load_cert_series(os.path.join(out_dir, "metrics.jsonl"), last_n=20)
    if series.get("available"):
        st.line_chart(series["latest_top_percent"])
        st.line_chart(series["std_top_percent"])
        ss = stability_score(series)
        if ss.get("available"):
            st.metric("Stability Score", f"{ss['score']:.3f}")
            st.caption(f"ok_rate={ss['ok_rate']:.2f}  std_mean={ss['std_mean']:.2f}  band_last={ss['band_last']}")
            if ss.get("stable_window"):
                st.success("STABLE WINDOW: last 5 certs >=4 OK and std_mean<=1.2")
    else:
        st.info("No certification series yet.")

    from engine.certification import summarize_cert_trend
    trend = summarize_cert_trend(out_dir, last_n=5)
    if trend.get("available"):
        st.json(trend)
    else:
        st.info("No certification history available.")

    from engine.certification import certify, save_report
    if st.button("Generate Certification Report"):
        rep = certify(cfg, out_dir)
        save_report(cfg, out_dir, rep)
        st.success("Saved certification_report.json")
    cert_path = os.path.join(out_dir, "certification_report.json")
    if os.path.exists(cert_path):
        with st.expander("Latest certification_report.json", expanded=False):
            st.json(json.load(open(cert_path, "r", encoding="utf-8")))
    final_threshold_path = os.path.join(out_dir, "final_threshold_eval.json")
    if os.path.exists(final_threshold_path):
        with st.expander("Latest final_threshold_eval.json", expanded=False):
            st.json(json.load(open(final_threshold_path, "r", encoding="utf-8")))
    supervisor_path = os.path.join("domains", "webnovel", "runtime", "supervisor_state.json")
    if os.path.exists(supervisor_path):
        supervisor_state = load_supervisor_state(supervisor_path)
        st.subheader("Supervisor Risk")
        c1, c2, c3 = st.columns(3)
        c1.metric("Supervisor status", str(supervisor_state.get("status") or "idle"))
        c2.metric("Hidden risk trend", f"{float(supervisor_state.get('hidden_reader_risk_trend', 0.0) or 0.0):.2f}")
        c3.metric("Trend priority", str(supervisor_state.get("reader_risk_trend_priority") or "none"))
        with st.expander("Latest supervisor_state.json", expanded=False):
            st.json(supervisor_state)

    st.subheader("Phase Health")
    from engine.phase_health import check as phase_check
    st.json(phase_check())


    st.subheader("Integrated Validation")
    from engine.integrated_validator import run_all
    if st.button("Run Validation Suite"):
        rep = run_all(".")
        st.json(rep)
