import json
import os
import tempfile

from engine.worldbuilding_export import (
    export_worldbuilding_assets,
    generate_structured_drafts,
    grounded_normalize_drafts,
    validate_export_consistency,
    validate_export_schemas,
)


def _write(path: str, text: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def _sample_assets(root: str):
    _write(
        os.path.join(root, "region_henesys.txt"),
        "region_id: henesys\nname: Henesys\ntone: warm_peaceful_frontier\npalette: green, light_brown\narchitecture: wooden_houses\nlandmarks: village_square\nfactions: villagers\nhazards: forest_monsters\nkeywords: pastoral\n",
    )
    _write(
        os.path.join(root, "npc_henesys.txt"),
        "npc_id: henesys_maya\nname: Maya\nregion_id: henesys\nrole: healer\npersonality: kind, hopeful\nspeech_style: gentle_formal\nservices: healing\nrelated_quests: maya_medicine_01\nrelationships: henesys_teo>trust\n\n---\n\nnpc_id: henesys_teo\nname: Teo\nregion_id: henesys\nrole: scout\npersonality: alert\nspeech_style: brisk_friendly\nservices: warning\nrelated_quests: forest_warning_02\n",
    )
    _write(
        os.path.join(root, "quest_chain_01.txt"),
        "chain_id: henesys_beginner_arc\ntheme: growth_and_trust\n\n---\n\nquest_id: maya_medicine_01\nstart_npc_id: henesys_maya\nregion_id: henesys\nobjective: collect_herbs\nsteps: talk_to_maya, collect_5_green_herbs\nreward_items: basic_potion\nreward_exp: 100\nnext_quest_id: forest_warning_02\n\n---\n\nquest_id: forest_warning_02\nstart_npc_id: henesys_teo\nregion_id: henesys\nobjective: scout_forest_edge\nsteps: talk_to_teo, inspect_forest_edge\nreward_items: beginner_arrow_bundle\nreward_exp: 120\n",
    )
    _write(os.path.join(root, "item_theme.txt"), "theme_id: woodland_beginner_gear\ntags: wood, starter\nregion_ids: henesys\n")
    _write(os.path.join(root, "monster_lore.txt"), "theme_id: forest_mushroom\ntags: cute, forest\nregion_ids: henesys\n")
    _write(
        os.path.join(root, "banned_patterns.txt"),
        "forbidden_words: cyber, mecha, neon\nforbidden_styles: modern_slang, grimdark_overkill\nallowed_name_style: fantasy_koreanized_maple_tone\nforbidden_tones: explicit_horror\nrequired_tones: whimsical, adventurous\nforbidden_patterns: direct_copy_of_existing_maplestory_lore\n",
    )


def test_worldbuilding_export_generates_valid_schema_output():
    with tempfile.TemporaryDirectory() as tmpdir:
        assets_dir = os.path.join(tmpdir, "story_assets")
        exports_dir = os.path.join(tmpdir, "exports")
        _sample_assets(assets_dir)

        report = export_worldbuilding_assets(assets_dir, exports_dir)

        assert report["schema_validation"]["valid"]
        assert report["consistency_validation"]["valid"]
        assert os.path.exists(os.path.join(exports_dir, "region_style.json"))
        assert os.path.exists(os.path.join(exports_dir, "npc_sheet.json"))
        assert os.path.exists(os.path.join(exports_dir, "quest_chain.json"))
        assert os.path.exists(os.path.join(exports_dir, "theme_tags.json"))
        assert os.path.exists(os.path.join(exports_dir, "banned_patterns.json"))


def test_worldbuilding_export_uses_null_or_empty_for_missing_fields():
    with tempfile.TemporaryDirectory() as tmpdir:
        assets_dir = os.path.join(tmpdir, "story_assets")
        os.makedirs(assets_dir, exist_ok=True)
        _write(os.path.join(assets_dir, "region_henesys.txt"), "region_id: henesys\nname: Henesys\n")

        drafts = generate_structured_drafts(assets_dir)
        normalized = grounded_normalize_drafts(drafts)

        region = normalized["region_style"]["regions"][0]
        assert region["tone"] is None
        assert region["factions"] == []
        assert region["visual_style"]["palette"] == []


def test_grounded_extraction_does_not_invent_unsupported_relationships():
    with tempfile.TemporaryDirectory() as tmpdir:
        assets_dir = os.path.join(tmpdir, "story_assets")
        os.makedirs(assets_dir, exist_ok=True)
        _write(
            os.path.join(assets_dir, "npc_henesys.txt"),
            "npc_id: henesys_maya\nname: Maya\nregion_id: henesys\nrole: healer\nservices: healing\n",
        )

        drafts = generate_structured_drafts(assets_dir)
        normalized = grounded_normalize_drafts(drafts)

        npc = normalized["npc_sheet"]["npcs"][0]
        assert npc["relationships"] == []
        assert npc["related_quests"] == []


def test_cross_file_consistency_detects_missing_region_reference():
    payloads = {
        "region_style": {"regions": [{"region_id": "henesys", "name": "Henesys", "tone": None, "visual_style": {"palette": [], "architecture": [], "landmarks": []}, "factions": [], "hazards": [], "keywords": []}]},
        "npc_sheet": {"npcs": [{"npc_id": "maya", "name": "Maya", "region_id": "ellinia", "role": None, "personality": [], "speech_style": None, "services": [], "related_quests": [], "relationships": []}]},
        "quest_chain": {"quest_chains": []},
        "theme_tags": {"monster_themes": [], "item_themes": []},
        "banned_patterns": {"naming_constraints": {"forbidden_words": [], "forbidden_styles": [], "allowed_name_style": "fantasy"}, "tone_constraints": {"forbidden_tones": [], "required_tones": []}, "content_constraints": {"forbidden_patterns": []}},
    }

    report = validate_export_consistency(payloads)

    assert not report["valid"]
    assert "unknown region_id" in report["errors"][0]


def test_banned_pattern_validation_rejects_forbidden_theme_names():
    payloads = {
        "region_style": {"regions": [{"region_id": "henesys", "name": "Henesys", "tone": None, "visual_style": {"palette": [], "architecture": [], "landmarks": []}, "factions": [], "hazards": [], "keywords": []}]},
        "npc_sheet": {"npcs": []},
        "quest_chain": {"quest_chains": []},
        "theme_tags": {"monster_themes": [{"theme_id": "neon_forest", "tags": ["forest"], "region_ids": ["henesys"]}], "item_themes": []},
        "banned_patterns": {"naming_constraints": {"forbidden_words": ["neon"], "forbidden_styles": [], "allowed_name_style": "fantasy"}, "tone_constraints": {"forbidden_tones": [], "required_tones": []}, "content_constraints": {"forbidden_patterns": []}},
    }

    report = validate_export_consistency(payloads)

    assert not report["valid"]
    assert "violates forbidden naming words" in report["errors"][0]


def test_stable_export_generation_from_sample_assets():
    with tempfile.TemporaryDirectory() as tmpdir:
        assets_dir = os.path.join(tmpdir, "story_assets")
        exports_dir = os.path.join(tmpdir, "exports")
        _sample_assets(assets_dir)
        export_worldbuilding_assets(assets_dir, exports_dir)
        first = json.load(open(os.path.join(exports_dir, "npc_sheet.json"), "r", encoding="utf-8"))
        export_worldbuilding_assets(assets_dir, exports_dir)
        second = json.load(open(os.path.join(exports_dir, "npc_sheet.json"), "r", encoding="utf-8"))

        assert first == second


def test_schema_validation_catches_invalid_reward_exp_type():
    payloads = {
        "region_style": {"regions": []},
        "npc_sheet": {"npcs": []},
        "quest_chain": {"quest_chains": [{"chain_id": "chain", "theme": None, "quests": [{"quest_id": "q1", "start_npc_id": None, "region_id": None, "objective": None, "steps": [], "rewards": {"items": [], "exp": "100"}, "next_quest_id": None}]}]},
        "theme_tags": {"monster_themes": [], "item_themes": []},
        "banned_patterns": {"naming_constraints": {"forbidden_words": [], "forbidden_styles": [], "allowed_name_style": "fantasy"}, "tone_constraints": {"forbidden_tones": [], "required_tones": []}, "content_constraints": {"forbidden_patterns": []}},
    }

    report = validate_export_schemas(payloads)

    assert not report["valid"]
    assert "rewards.exp must be int or null" in report["errors"][0]
