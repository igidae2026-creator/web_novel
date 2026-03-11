import json
import os

from engine.certification import save_report


def test_save_report_refreshes_final_threshold_bundle(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    out_dir = tmp_path / "outputs"
    out_dir.mkdir(parents=True)
    track_dir = tmp_path
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True)
    (data_dir / "revenue_input.csv").write_text("revenue\n1200\n800\n", encoding="utf-8")
    (data_dir / "campaign_input.csv").write_text("campaign,spend,revenue\nlaunch,100,180\nretarget,50,70\n", encoding="utf-8")

    with open(track_dir / "state.json", "w", encoding="utf-8") as handle:
        json.dump(
            {
                "story_state_v2": {"control": {}},
                "last_quality_gate": {
                    "passed": True,
                    "checks": {
                        "hook_score": True,
                        "cliffhanger_valid": True,
                        "world_instability": True,
                    },
                    "predicted_retention": 0.86,
                    "content_ceiling_total": 73,
                    "causal_score": 0.9,
                },
                "quality_lift_if_human_intervenes": 0.0,
            },
            handle,
            ensure_ascii=False,
            indent=2,
        )

    with open(out_dir / "events.jsonl", "w", encoding="utf-8") as handle:
        handle.write(json.dumps({"ts": "2026-03-11 00:00:00", "type": "queue_step", "payload": {}}) + "\n")
    with open(out_dir / "metrics.jsonl", "w", encoding="utf-8") as handle:
        handle.write(
            json.dumps(
                {
                    "episode": 3,
                    "scores": {"hook_score": 0.9},
                    "episode_attribution": {"lineage_parent": "outline:v2"},
                    "retention": {"predicted_next_episode": 0.86},
                    "content_ceiling": {"ceiling_total": 73},
                    "meta": {
                        "scene_causality": {"score": 0.9},
                        "episode_attribution": {"lineage_parent": "outline:v2"},
                    },
                },
                ensure_ascii=False,
            )
            + "\n"
        )

    cfg = {
        "project": {"platform": "Munpia", "genre_bucket": "A"},
        "quality": {"predicted_retention_min": 0.8, "causal_score_min": 0.72, "ceiling_total_min": 65},
        "safe_mode": False,
    }
    report = {
        "market": {
            "available": True,
            "ok": True,
            "stats": {"available": True, "latest_top_percent": 2.5},
        },
        "failure_reason": None,
    }

    path = save_report(cfg, str(out_dir), report)

    assert path.endswith("certification_report.json")
    certification_report = json.load(open(path, "r", encoding="utf-8"))
    assert certification_report["business_feedback"]["available"] is True
    assert certification_report["business_feedback"]["revenue_rows"] == 2
    assert certification_report["business_feedback"]["campaign_rows"] == 2
    final_threshold_path = out_dir / "final_threshold_eval.json"
    assert final_threshold_path.exists()
    final_threshold = json.load(open(final_threshold_path, "r", encoding="utf-8"))
    assert "final_threshold_ready" in final_threshold
    assert final_threshold["criteria"]["market_feedback_autoloop"]["details"]["business_feedback_present"] is True
