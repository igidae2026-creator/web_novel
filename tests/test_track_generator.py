import json
import os

from engine.track_generator import generate_tracks


def _write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def test_generate_tracks_bootstraps_subengine_from_hidden_reader_risk_profile(tmp_path):
    tracks_root = tmp_path / "tracks"
    existing_dir = tracks_root / "legacy_munpia_a"
    _write_json(
        existing_dir / "track.json",
        {"project": {"name": "existing", "platform": "Munpia", "genre_bucket": "A", "sub_engine": "A_REVENGE_REGRESSION"}},
    )
    _write_json(
        existing_dir / "outputs" / "final_threshold_eval.json",
        {
            "criteria": {
                "reader_retention_stability": {
                    "details": {
                        "reader_quality_debt": {
                            "thinness_debt": 0.18,
                            "fake_urgency_debt": 0.14,
                        }
                    }
                },
                "serialization_fatigue_control": {
                    "details": {
                        "reader_quality_debt": {
                            "repetition_debt": 0.12,
                            "deja_vu_debt": 0.1,
                        }
                    }
                },
                "autonomous_convergence_trend": {
                    "details": {
                        "hidden_reader_risk_trend": 0.21,
                        "heavy_reader_signal_trend": 0.57,
                    }
                },
            }
        },
    )

    created = generate_tracks(str(tmp_path), "bootstrap-project", platforms=["Munpia"], buckets=["A"])

    assert created[0]["hidden_reader_risk"] >= 0.7
    track_json = json.load(open(tracks_root / "munpia_a" / "track.json", "r", encoding="utf-8"))
    assert track_json["project"]["sub_engine"] != "AUTO"
    assert track_json["project"]["sub_engine"] == created[0]["sub_engine"]
    assert track_json["project"]["bootstrap_design_guardrails"]
    assert track_json["bootstrap_strategy"]["hidden_reader_risk"] >= 0.7
    assert track_json["project"]["bootstrap_heavy_reader_signal_trend"] == 0.57
    assert created[0]["heavy_reader_signal_trend"] == 0.57
