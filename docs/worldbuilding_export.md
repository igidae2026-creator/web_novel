# Worldbuilding Export Pipeline

This repository now includes a separate worldbuilding export layer for game-content production.

## Pipeline

```text
story/world assets
-> structured draft generation
-> grounded extraction / normalization
-> schema validation
-> consistency validation
-> final export json files
```

The export layer does not use the novel text directly.

## Source Assets

Default sample assets live in `story_assets/`.

- `region_henesys.txt`
- `npc_henesys.txt`
- `quest_chain_01.txt`
- `item_theme.txt`
- `monster_lore.txt`
- `banned_patterns.txt`

## Output Files

- `exports/region_style.json`
- `exports/npc_sheet.json`
- `exports/quest_chain.json`
- `exports/theme_tags.json`
- `exports/banned_patterns.json`

Draft files are also written to `exports/drafts/`.

Schema files are stored in `exports/schemas/`.

## How To Run

```bash
python3 -m engine.worldbuilding_export
```

## Validation

The export pipeline performs:

- schema-oriented field validation
- stable ID normalization
- null or empty-array fallback for missing fields
- cross-file consistency checks for region, NPC, quest, and theme references
- banned pattern validation against generated IDs and tags

## Hallucination Reduction

The export pipeline reduces unsupported invention by:

- using deterministic asset parsing first
- normalizing only grounded fields
- using null or empty arrays instead of guessing
- keeping machine-friendly stable IDs
- rejecting cross-file reference errors
- avoiding unsupported lore invention in final exports
