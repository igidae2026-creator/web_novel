import json
import os

from engine.track_queue import build_track_dirs


def _write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def test_build_track_dirs_prioritizes_critical_failed_bundles(tmp_path):
    tracks_root = tmp_path / "domains" / "webnovel" / "tracks"
    track_a = tracks_root / "track_a"
    track_b = tracks_root / "track_b"
    track_c = tracks_root / "track_c"
    for track in [track_a, track_b, track_c]:
        _write_json(track / "track.json", {"project": {"platform": "Munpia", "genre_bucket": "A"}})

    _write_json(track_a / "outputs" / "final_threshold_eval.json", {"failed_bundles": []})
    _write_json(track_b / "outputs" / "final_threshold_eval.json", {"failed_bundles": ["judgment_capability"]})
    _write_json(track_c / "outputs" / "final_threshold_eval.json", {"failed_bundles": ["truth_capability"]})

    ordered = build_track_dirs(str(tracks_root))

    assert ordered[0].endswith("track_c")
    assert ordered[1].endswith("track_b")
    assert ordered[2].endswith("track_a")


def test_build_track_dirs_prioritizes_reader_quality_failed_criteria_within_same_bundle_band(tmp_path):
    tracks_root = tmp_path / "domains" / "webnovel" / "tracks"
    track_a = tracks_root / "track_a"
    track_b = tracks_root / "track_b"
    for track in [track_a, track_b]:
        _write_json(track / "track.json", {"project": {"platform": "Munpia", "genre_bucket": "A"}})

    _write_json(track_a / "outputs" / "final_threshold_eval.json", {"failed_bundles": ["generation_capability"], "failed_criteria": []})
    _write_json(
        track_b / "outputs" / "final_threshold_eval.json",
        {"failed_bundles": ["generation_capability"], "failed_criteria": ["early_hook_strength", "reader_retention_stability"]},
    )

    ordered = build_track_dirs(str(tracks_root))

    assert ordered[0].endswith("track_b")
    assert ordered[1].endswith("track_a")


def test_build_track_dirs_prioritizes_hidden_reader_risk_within_same_band(tmp_path):
    tracks_root = tmp_path / "domains" / "webnovel" / "tracks"
    track_a = tracks_root / "track_a"
    track_b = tracks_root / "track_b"
    for track in [track_a, track_b]:
        _write_json(track / "track.json", {"project": {"platform": "Munpia", "genre_bucket": "A"}})

    _write_json(
        track_a / "outputs" / "final_threshold_eval.json",
        {
            "failed_bundles": ["generation_capability"],
            "failed_criteria": ["reader_retention_stability"],
            "criteria": {
                "reader_retention_stability": {
                    "details": {
                        "reader_quality_debt": {
                            "thinness_debt": 0.08,
                            "fake_urgency_debt": 0.07,
                        }
                    }
                }
            },
        },
    )
    _write_json(
        track_b / "outputs" / "final_threshold_eval.json",
        {
            "failed_bundles": ["generation_capability"],
            "failed_criteria": ["reader_retention_stability"],
            "criteria": {
                "reader_retention_stability": {
                    "details": {
                        "reader_quality_debt": {
                            "thinness_debt": 0.22,
                            "fake_urgency_debt": 0.16,
                            "compression_debt": 0.12,
                        }
                    }
                }
            },
        },
    )

    ordered = build_track_dirs(str(tracks_root))

    assert ordered[0].endswith("track_b")
    assert ordered[1].endswith("track_a")


def test_build_track_dirs_prioritizes_hidden_reader_risk_trend_within_same_band(tmp_path):
    tracks_root = tmp_path / "domains" / "webnovel" / "tracks"
    track_a = tracks_root / "track_a"
    track_b = tracks_root / "track_b"
    for track in [track_a, track_b]:
        _write_json(track / "track.json", {"project": {"platform": "Munpia", "genre_bucket": "A"}})

    _write_json(
        track_a / "outputs" / "final_threshold_eval.json",
        {
            "failed_bundles": ["generation_capability"],
            "failed_criteria": ["autonomous_convergence_trend"],
            "criteria": {
                "autonomous_convergence_trend": {
                    "details": {
                        "hidden_reader_risk_trend": 0.18,
                    }
                }
            },
        },
    )
    _write_json(
        track_b / "outputs" / "final_threshold_eval.json",
        {
            "failed_bundles": ["generation_capability"],
            "failed_criteria": ["autonomous_convergence_trend"],
            "criteria": {
                "autonomous_convergence_trend": {
                    "details": {
                        "hidden_reader_risk_trend": 0.44,
                    }
                }
            },
        },
    )

    ordered = build_track_dirs(str(tracks_root))

    assert ordered[0].endswith("track_b")
    assert ordered[1].endswith("track_a")
