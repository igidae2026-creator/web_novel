# CHECKLIST_PATCH

PATCH_ID: WEBNOVEL-L3-0001
TARGET_LAYER: Layer3
CHANGE_TYPE: modify
SECTION: canonical runtime entry mapping
OLD: imported Layer3 assumed generic MetaOS runtime files such as `tools/loop.py`, `tools/meta_loop.py`, and `tools/system_evolver.py`
NEW: canonical runtime for this repository is `app.py` with orchestration centered in `engine/pipeline.py`, `engine/runtime_config.py`, and `engine/state.py`
REASON: the actual repository is a Streamlit-centered web-novel production system and needs repo-true canonical mapping
STATUS: accepted

PATCH_ID: WEBNOVEL-L3-0002
TARGET_LAYER: Layer3
CHANGE_TYPE: add
SECTION: quality-axis module mapping
OLD: no repo-specific mapping for hook, cliffhanger, retention, character, conflict, world logic, and repair
NEW: map those quality axes to `engine/cliffhanger_engine.py`, `engine/tension_wave.py`, `engine/predictive_retention.py`, `engine/character_arc.py`, `engine/conflict_memory.py`, `engine/world_logic.py`, `engine/scene_causality.py`, and `engine/causal_repair.py`
REASON: upper-tier web-novel quality must be auditable at the file and test level
STATUS: accepted

PATCH_ID: WEBNOVEL-L3-0003
TARGET_LAYER: Layer3
CHANGE_TYPE: add
SECTION: goal and objective file mapping
OLD: this repository had no canonical `GOAL.md`, `SYSTEM_OBJECTIVE.md`, or `METAOS_ANCHOR.md`
NEW: `GOAL.md`, `SYSTEM_OBJECTIVE.md`, and `METAOS_ANCHOR.md` are canonical repo-goal documents
REASON: Layer2 requires fixed goal and system objective ownership
STATUS: accepted
