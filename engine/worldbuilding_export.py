from __future__ import annotations

import json
import os
import re
from copy import deepcopy
from typing import Any, Dict, List, Tuple

from .safe_io import safe_write_text

EXPORT_FILE_NAMES = {
    "region_style": "region_style.json",
    "npc_sheet": "npc_sheet.json",
    "quest_chain": "quest_chain.json",
    "theme_tags": "theme_tags.json",
    "banned_patterns": "banned_patterns.json",
}

DEFAULT_BANNED_PATTERNS = {
    "naming_constraints": {
        "forbidden_words": ["cyber", "mecha", "neon"],
        "forbidden_styles": ["modern_slang", "grimdark_overkill"],
        "allowed_name_style": "fantasy_koreanized_maple_tone",
    },
    "tone_constraints": {
        "forbidden_tones": ["explicit_horror", "nihilistic_edgelord"],
        "required_tones": ["whimsical", "adventurous", "emotionally_clear"],
    },
    "content_constraints": {
        "forbidden_patterns": [
            "direct_copy_of_existing_maplestory_lore",
            "overly_complex_political_drama",
            "immersion_breaking_meta_jokes",
        ]
    },
}


def _slug(value: str | None) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "_", str(value or "").strip().lower()).strip("_")
    return text or "unknown"


def _split_list(value: str | None) -> List[str]:
    if value in (None, ""):
        return []
    parts = re.split(r"[|,]", str(value))
    return [_slug(item) if " " not in item.strip() else _slug(item) for item in parts if item.strip()]


def _split_text_list(value: str | None) -> List[str]:
    if value in (None, ""):
        return []
    parts = re.split(r"[|,]", str(value))
    return [item.strip() for item in parts if item.strip()]


def _parse_key_value_blocks(path: str) -> List[Dict[str, str]]:
    if not os.path.exists(path):
        return []
    blocks: List[Dict[str, str]] = []
    current: Dict[str, str] = {}
    with open(path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                if current:
                    blocks.append(current)
                    current = {}
                continue
            if line == "---":
                if current:
                    blocks.append(current)
                    current = {}
                continue
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            current[_slug(key)] = value.strip()
    if current:
        blocks.append(current)
    return blocks


def _build_region_drafts(story_assets_dir: str) -> List[Dict[str, Any]]:
    regions: List[Dict[str, Any]] = []
    for name in sorted(os.listdir(story_assets_dir)):
        if not name.startswith("region_") or not name.endswith(".txt"):
            continue
        blocks = _parse_key_value_blocks(os.path.join(story_assets_dir, name))
        if not blocks:
            continue
        block = blocks[0]
        region_id = _slug(block.get("region_id") or name.replace("region_", "").replace(".txt", ""))
        regions.append(
            {
                "region_id": region_id,
                "name": block.get("name"),
                "tone": _slug(block.get("tone")) if block.get("tone") else None,
                "visual_style": {
                    "palette": _split_list(block.get("palette")),
                    "architecture": _split_list(block.get("architecture")),
                    "landmarks": _split_list(block.get("landmarks")),
                },
                "factions": _split_list(block.get("factions")),
                "hazards": _split_list(block.get("hazards")),
                "keywords": _split_list(block.get("keywords")),
                "_evidence": {"source_file": name, "fields": sorted(block.keys())},
            }
        )
    return regions


def _build_npc_drafts(story_assets_dir: str) -> List[Dict[str, Any]]:
    npcs: List[Dict[str, Any]] = []
    for name in sorted(os.listdir(story_assets_dir)):
        if not name.startswith("npc_") or not name.endswith(".txt"):
            continue
        for block in _parse_key_value_blocks(os.path.join(story_assets_dir, name)):
            relationships = []
            for rel in _split_text_list(block.get("relationships")):
                if ">" in rel:
                    target, rel_type = rel.split(">", 1)
                elif "|" in rel:
                    target, rel_type = rel.split("|", 1)
                else:
                    target, rel_type = rel, ""
                relationships.append({"target_npc_id": _slug(target), "type": _slug(rel_type) if rel_type else None})
            npcs.append(
                {
                    "npc_id": _slug(block.get("npc_id") or block.get("name")),
                    "name": block.get("name"),
                    "region_id": _slug(block.get("region_id")) if block.get("region_id") else None,
                    "role": _slug(block.get("role")) if block.get("role") else None,
                    "personality": _split_list(block.get("personality")),
                    "speech_style": _slug(block.get("speech_style")) if block.get("speech_style") else None,
                    "services": _split_list(block.get("services")),
                    "related_quests": _split_list(block.get("related_quests")),
                    "relationships": relationships,
                    "_evidence": {"source_file": name, "fields": sorted(block.keys())},
                }
            )
    return npcs


def _build_quest_chain_drafts(story_assets_dir: str) -> List[Dict[str, Any]]:
    chains: List[Dict[str, Any]] = []
    for name in sorted(os.listdir(story_assets_dir)):
        if not name.startswith("quest_chain_") or not name.endswith(".txt"):
            continue
        blocks = _parse_key_value_blocks(os.path.join(story_assets_dir, name))
        if not blocks:
            continue
        header = blocks[0]
        quests = []
        for block in blocks[1:]:
            reward_items = _split_list(block.get("reward_items"))
            reward_exp = block.get("reward_exp")
            quests.append(
                {
                    "quest_id": _slug(block.get("quest_id") or block.get("name")),
                    "start_npc_id": _slug(block.get("start_npc_id")) if block.get("start_npc_id") else None,
                    "region_id": _slug(block.get("region_id")) if block.get("region_id") else None,
                    "objective": _slug(block.get("objective")) if block.get("objective") else None,
                    "steps": _split_list(block.get("steps")),
                    "rewards": {
                        "items": reward_items,
                        "exp": int(reward_exp) if str(reward_exp or "").isdigit() else None,
                    },
                    "next_quest_id": _slug(block.get("next_quest_id")) if block.get("next_quest_id") else None,
                }
            )
        chains.append(
            {
                "chain_id": _slug(header.get("chain_id") or name.replace(".txt", "")),
                "theme": _slug(header.get("theme")) if header.get("theme") else None,
                "quests": quests,
                "_evidence": {"source_file": name, "fields": sorted(header.keys())},
            }
        )
    return chains


def _build_theme_drafts(story_assets_dir: str) -> Dict[str, Any]:
    def _theme_blocks(filename: str, key: str) -> List[Dict[str, Any]]:
        path = os.path.join(story_assets_dir, filename)
        items = []
        for block in _parse_key_value_blocks(path):
            items.append(
                {
                    "theme_id": _slug(block.get("theme_id") or block.get("name") or filename.replace(".txt", "")),
                    "tags": _split_list(block.get("tags")),
                    "region_ids": _split_list(block.get("region_ids")),
                    "_evidence": {"source_file": filename, "fields": sorted(block.keys())},
                }
            )
        return items

    return {
        "monster_themes": _theme_blocks("monster_lore.txt", "monster_themes"),
        "item_themes": _theme_blocks("item_theme.txt", "item_themes"),
    }


def _build_banned_patterns_draft(story_assets_dir: str) -> Dict[str, Any]:
    path = os.path.join(story_assets_dir, "banned_patterns.txt")
    blocks = _parse_key_value_blocks(path)
    if not blocks:
        return deepcopy(DEFAULT_BANNED_PATTERNS)
    block = blocks[0]
    return {
        "naming_constraints": {
            "forbidden_words": _split_list(block.get("forbidden_words")) or deepcopy(DEFAULT_BANNED_PATTERNS["naming_constraints"]["forbidden_words"]),
            "forbidden_styles": _split_list(block.get("forbidden_styles")) or deepcopy(DEFAULT_BANNED_PATTERNS["naming_constraints"]["forbidden_styles"]),
            "allowed_name_style": _slug(block.get("allowed_name_style")) if block.get("allowed_name_style") else DEFAULT_BANNED_PATTERNS["naming_constraints"]["allowed_name_style"],
        },
        "tone_constraints": {
            "forbidden_tones": _split_list(block.get("forbidden_tones")) or deepcopy(DEFAULT_BANNED_PATTERNS["tone_constraints"]["forbidden_tones"]),
            "required_tones": _split_list(block.get("required_tones")) or deepcopy(DEFAULT_BANNED_PATTERNS["tone_constraints"]["required_tones"]),
        },
        "content_constraints": {
            "forbidden_patterns": _split_list(block.get("forbidden_patterns")) or deepcopy(DEFAULT_BANNED_PATTERNS["content_constraints"]["forbidden_patterns"])
        },
    }


def generate_structured_drafts(story_assets_dir: str) -> Dict[str, Any]:
    return {
        "region_style": {"regions": _build_region_drafts(story_assets_dir)},
        "npc_sheet": {"npcs": _build_npc_drafts(story_assets_dir)},
        "quest_chain": {"quest_chains": _build_quest_chain_drafts(story_assets_dir)},
        "theme_tags": _build_theme_drafts(story_assets_dir),
        "banned_patterns": _build_banned_patterns_draft(story_assets_dir),
    }


def _drop_evidence(payload: Any) -> Any:
    if isinstance(payload, list):
        return [_drop_evidence(item) for item in payload]
    if isinstance(payload, dict):
        return {key: _drop_evidence(value) for key, value in payload.items() if not key.startswith("_")}
    return payload


def grounded_normalize_drafts(drafts: Dict[str, Any]) -> Dict[str, Any]:
    normalized = _drop_evidence(deepcopy(drafts))
    for region in normalized.get("region_style", {}).get("regions", []):
        region["region_id"] = _slug(region.get("region_id"))
        if region.get("tone"):
            region["tone"] = _slug(region["tone"])
        for key in ("palette", "architecture", "landmarks"):
            region.setdefault("visual_style", {}).setdefault(key, [])
            region["visual_style"][key] = [_slug(item) for item in list(region["visual_style"].get(key, []) or [])]
    for npc in normalized.get("npc_sheet", {}).get("npcs", []):
        npc["npc_id"] = _slug(npc.get("npc_id"))
        npc["region_id"] = _slug(npc.get("region_id")) if npc.get("region_id") else None
        npc["role"] = _slug(npc.get("role")) if npc.get("role") else None
        npc["speech_style"] = _slug(npc.get("speech_style")) if npc.get("speech_style") else None
        npc["services"] = [_slug(item) for item in list(npc.get("services", []) or [])]
        npc["personality"] = [_slug(item) for item in list(npc.get("personality", []) or [])]
        npc["related_quests"] = [_slug(item) for item in list(npc.get("related_quests", []) or [])]
        for rel in npc.get("relationships", []) or []:
            rel["target_npc_id"] = _slug(rel.get("target_npc_id")) if rel.get("target_npc_id") else None
            rel["type"] = _slug(rel.get("type")) if rel.get("type") else None
    for chain in normalized.get("quest_chain", {}).get("quest_chains", []):
        chain["chain_id"] = _slug(chain.get("chain_id"))
        chain["theme"] = _slug(chain.get("theme")) if chain.get("theme") else None
        for quest in chain.get("quests", []) or []:
            quest["quest_id"] = _slug(quest.get("quest_id"))
            quest["start_npc_id"] = _slug(quest.get("start_npc_id")) if quest.get("start_npc_id") else None
            quest["region_id"] = _slug(quest.get("region_id")) if quest.get("region_id") else None
            quest["objective"] = _slug(quest.get("objective")) if quest.get("objective") else None
            quest["steps"] = [_slug(item) for item in list(quest.get("steps", []) or [])]
            quest["next_quest_id"] = _slug(quest.get("next_quest_id")) if quest.get("next_quest_id") else None
            rewards = dict(quest.get("rewards", {}) or {})
            rewards["items"] = [_slug(item) for item in list(rewards.get("items", []) or [])]
            rewards["exp"] = int(rewards["exp"]) if isinstance(rewards.get("exp"), int) else None
            quest["rewards"] = rewards
    for key in ("monster_themes", "item_themes"):
        for item in normalized.get("theme_tags", {}).get(key, []) or []:
            item["theme_id"] = _slug(item.get("theme_id"))
            item["tags"] = [_slug(tag) for tag in list(item.get("tags", []) or [])]
            item["region_ids"] = [_slug(region_id) for region_id in list(item.get("region_ids", []) or [])]
    for group_key, fields in normalized.get("banned_patterns", {}).items():
        if isinstance(fields, dict):
            for field_name, value in list(fields.items()):
                if isinstance(value, list):
                    fields[field_name] = [_slug(item) for item in value]
                elif isinstance(value, str):
                    fields[field_name] = _slug(value)
    return normalized


def _validate_list_strings(items: Any, field: str) -> List[str]:
    errors = []
    if not isinstance(items, list):
        return [f"{field} must be a list"]
    for index, item in enumerate(items):
        if not isinstance(item, str):
            errors.append(f"{field}[{index}] must be a string")
    return errors


def validate_export_schemas(payloads: Dict[str, Any]) -> Dict[str, Any]:
    errors: List[str] = []
    for region in payloads.get("region_style", {}).get("regions", []):
        if not isinstance(region.get("region_id"), str):
            errors.append("region_style.regions.region_id must be string")
        errors.extend(_validate_list_strings(region.get("factions", []), "region_style.regions.factions"))
        errors.extend(_validate_list_strings(region.get("hazards", []), "region_style.regions.hazards"))
        errors.extend(_validate_list_strings(region.get("keywords", []), "region_style.regions.keywords"))
    for npc in payloads.get("npc_sheet", {}).get("npcs", []):
        if not isinstance(npc.get("npc_id"), str):
            errors.append("npc_sheet.npcs.npc_id must be string")
        errors.extend(_validate_list_strings(npc.get("services", []), "npc_sheet.npcs.services"))
        errors.extend(_validate_list_strings(npc.get("related_quests", []), "npc_sheet.npcs.related_quests"))
    for chain in payloads.get("quest_chain", {}).get("quest_chains", []):
        if not isinstance(chain.get("chain_id"), str):
            errors.append("quest_chain.quest_chains.chain_id must be string")
        for quest in chain.get("quests", []):
            if not isinstance(quest.get("quest_id"), str):
                errors.append("quest_chain.quest_chains.quests.quest_id must be string")
            errors.extend(_validate_list_strings(quest.get("steps", []), "quest_chain.quest_chains.quests.steps"))
            rewards = quest.get("rewards", {})
            errors.extend(_validate_list_strings(rewards.get("items", []), "quest_chain.quest_chains.quests.rewards.items"))
            if rewards.get("exp") is not None and not isinstance(rewards.get("exp"), int):
                errors.append("quest_chain.quest_chains.quests.rewards.exp must be int or null")
    for section in ("monster_themes", "item_themes"):
        for item in payloads.get("theme_tags", {}).get(section, []):
            if not isinstance(item.get("theme_id"), str):
                errors.append(f"theme_tags.{section}.theme_id must be string")
            errors.extend(_validate_list_strings(item.get("tags", []), f"theme_tags.{section}.tags"))
            errors.extend(_validate_list_strings(item.get("region_ids", []), f"theme_tags.{section}.region_ids"))
    banned = payloads.get("banned_patterns", {})
    if not isinstance(((banned.get("naming_constraints", {}) or {}).get("allowed_name_style")), str):
        errors.append("banned_patterns.naming_constraints.allowed_name_style must be string")
    for group, field in (("naming_constraints", "forbidden_words"), ("naming_constraints", "forbidden_styles"), ("tone_constraints", "forbidden_tones"), ("tone_constraints", "required_tones"), ("content_constraints", "forbidden_patterns")):
        errors.extend(_validate_list_strings((banned.get(group, {}) or {}).get(field, []), f"banned_patterns.{group}.{field}"))
    return {"valid": not errors, "errors": errors}


def validate_export_consistency(payloads: Dict[str, Any]) -> Dict[str, Any]:
    errors: List[str] = []
    region_ids = {region["region_id"] for region in payloads.get("region_style", {}).get("regions", []) if region.get("region_id")}
    npc_ids = {npc["npc_id"] for npc in payloads.get("npc_sheet", {}).get("npcs", []) if npc.get("npc_id")}
    quest_ids = {
        quest["quest_id"]
        for chain in payloads.get("quest_chain", {}).get("quest_chains", [])
        for quest in chain.get("quests", [])
        if quest.get("quest_id")
    }
    forbidden_words = set((payloads.get("banned_patterns", {}).get("naming_constraints", {}) or {}).get("forbidden_words", []))
    forbidden_styles = set((payloads.get("banned_patterns", {}).get("naming_constraints", {}) or {}).get("forbidden_styles", []))
    forbidden_tones = set((payloads.get("banned_patterns", {}).get("tone_constraints", {}) or {}).get("forbidden_tones", []))

    for npc in payloads.get("npc_sheet", {}).get("npcs", []):
        if npc.get("region_id") and npc["region_id"] not in region_ids:
            errors.append(f"NPC {npc['npc_id']} references unknown region_id {npc['region_id']}")
        for rel in npc.get("relationships", []) or []:
            target = rel.get("target_npc_id")
            if target and target not in npc_ids:
                errors.append(f"NPC {npc['npc_id']} references unknown target_npc_id {target}")
        if any(word in npc.get("npc_id", "") for word in forbidden_words):
            errors.append(f"NPC {npc['npc_id']} violates forbidden naming words")
        if npc.get("speech_style") in forbidden_styles:
            errors.append(f"NPC {npc['npc_id']} uses forbidden style {npc.get('speech_style')}")

    for chain in payloads.get("quest_chain", {}).get("quest_chains", []):
        local_ids = {quest["quest_id"] for quest in chain.get("quests", []) if quest.get("quest_id")}
        for quest in chain.get("quests", []):
            if quest.get("start_npc_id") and quest["start_npc_id"] not in npc_ids:
                errors.append(f"Quest {quest['quest_id']} references unknown start_npc_id {quest['start_npc_id']}")
            if quest.get("region_id") and quest["region_id"] not in region_ids:
                errors.append(f"Quest {quest['quest_id']} references unknown region_id {quest['region_id']}")
            if quest.get("next_quest_id") and quest["next_quest_id"] not in local_ids:
                errors.append(f"Quest {quest['quest_id']} references missing next_quest_id {quest['next_quest_id']}")
            for reward_item in (quest.get("rewards", {}) or {}).get("items", []):
                if any(word in reward_item for word in forbidden_words):
                    errors.append(f"Quest reward {reward_item} violates forbidden naming words")

    for section in ("monster_themes", "item_themes"):
        for item in payloads.get("theme_tags", {}).get(section, []):
            for region_id in item.get("region_ids", []) or []:
                if region_id not in region_ids:
                    errors.append(f"Theme {item['theme_id']} references unknown region_id {region_id}")
            if any(tag in forbidden_styles for tag in item.get("tags", []) or []):
                errors.append(f"Theme {item['theme_id']} uses forbidden style tag")
            if any(word in item.get("theme_id", "") for word in forbidden_words):
                errors.append(f"Theme {item['theme_id']} violates forbidden naming words")

    for region in payloads.get("region_style", {}).get("regions", []):
        if region.get("tone") in forbidden_tones:
            errors.append(f"Region {region['region_id']} uses forbidden tone {region.get('tone')}")

    return {"valid": not errors, "errors": errors}


def _write_json(path: str, payload: Dict[str, Any], safe_mode: bool = False) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    safe_write_text(path, json.dumps(payload, ensure_ascii=False, indent=2), safe_mode=safe_mode, project_dir_for_backup=os.path.dirname(path))


def export_worldbuilding_assets(
    story_assets_dir: str = "story_assets",
    exports_dir: str = "exports",
    safe_mode: bool = False,
) -> Dict[str, Any]:
    drafts_dir = os.path.join(exports_dir, "drafts")
    if not os.path.isdir(story_assets_dir):
        raise FileNotFoundError(f"story assets directory not found: {story_assets_dir}")

    drafts = generate_structured_drafts(story_assets_dir)
    for key, payload in drafts.items():
        _write_json(os.path.join(drafts_dir, EXPORT_FILE_NAMES[key]), payload, safe_mode=safe_mode)

    normalized = grounded_normalize_drafts(drafts)
    schema_report = validate_export_schemas(normalized)
    if not schema_report["valid"]:
        raise ValueError(f"schema validation failed: {schema_report['errors']}")
    consistency_report = validate_export_consistency(normalized)
    if not consistency_report["valid"]:
        raise ValueError(f"consistency validation failed: {consistency_report['errors']}")

    for key, payload in normalized.items():
        _write_json(os.path.join(exports_dir, EXPORT_FILE_NAMES[key]), payload, safe_mode=safe_mode)
    return {
        "drafts_dir": drafts_dir,
        "exports_dir": exports_dir,
        "files": {key: os.path.join(exports_dir, filename) for key, filename in EXPORT_FILE_NAMES.items()},
        "schema_validation": schema_report,
        "consistency_validation": consistency_report,
    }


if __name__ == "__main__":
    report = export_worldbuilding_assets()
    print(json.dumps(report, ensure_ascii=False, indent=2))
