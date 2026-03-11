## Anchor

Canonical governance hierarchy for this repository:

1. `docs/governance/RULE_CARDS.jsonl`
2. `docs/governance/METAOS_CONSTITUTION.md`
3. `docs/governance/CHECKLIST_LAYER1_목표조건.md`
4. `docs/governance/CHECKLIST_LAYER2_모듈책임.md`
5. `docs/governance/CHECKLIST_LAYER3_REPO매핑.md`
6. `docs/governance/CHECKLIST_METHOD_패치.md`
7. `docs/governance/COVERAGE_AUDIT.csv`
8. `docs/governance/CONFLICT_LOG.csv`

Repository-specific interpretation:
- this repo is a web-novel production system
- all governance must be read through the domain objective of upper-tier web-novel quality
- when generic METAOS language conflicts with web-novel product quality, implementation must be interpreted in favor of auditable web-novel production quality
- the intended endpoint is 24-hour unattended high-quality automation, not operator-assisted batch generation
- required automation scope includes both inner-loop generation/repair and outer-loop scope selection for newly arrived materials
- new material should be screened, scoped, and promoted automatically when it fits the canonical objective
- success is not merely that humans can improve outputs, but that later human intervention has little remaining quality upside

Current repository runtime center:
- runtime entry: `app.py`
- generation core: `engine/`
- supporting operations: `market_layer/`, `portfolio_layer/`, `metaos_business/`
