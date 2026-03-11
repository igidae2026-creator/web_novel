# Web Novel Governance Agent

This repository is governed by the canonical document stack below.

1. `docs/governance/RULE_CARDS.jsonl`
2. `docs/governance/METAOS_CONSTITUTION.md`
3. `docs/governance/CHECKLIST_LAYER1_목표조건.md`
4. `docs/governance/CHECKLIST_LAYER2_모듈책임.md`
5. `docs/governance/CHECKLIST_LAYER3_REPO매핑.md`
6. `docs/governance/CHECKLIST_METHOD_패치.md`
7. `docs/governance/COVERAGE_AUDIT.csv`
8. `docs/governance/CONFLICT_LOG.csv`
9. `GOAL.md`
10. `SYSTEM_OBJECTIVE.md`
11. `METAOS_ANCHOR.md`
12. `docs/governance/WEBNOVEL_ALIGNMENT_STATUS.md`
13. `docs/governance/AUTONOMY_TARGET.md`

## Mission

Build a web-novel production system that repeatedly produces outputs ordinary readers would recognize as upper-tier commercial work.

Do not optimize for one-off wins.
Optimize for stable 24-hour unattended production quality.
Treat "human intervention adds little further quality" as the terminal product bar.

## Primary Product Standard

Protected outcome qualities:
- strong early hook
- addictive episode endings
- coherent long-running conflict
- persuasive protagonist fantasy
- clear genre fit
- readable prose
- durable character/world logic

Operational success conditions:
- the system can run for long periods without continuous operator intervention
- new incoming material is not only ingested but judged for scope fitness and automatically promoted when appropriate
- humans reviewing later should mostly confirm or audit quality, not rescue weak output

## Working Rules

- Treat governance docs as canonical before touching code.
- Treat `docs/governance/AUTONOMY_TARGET.md` as the unattended execution standard for operator involvement and quality preservation.
- Prefer changes that increase auditable quality, not cosmetic churn.
- If a canonical checklist item does not match the current repo, record the mismatch in `docs/governance/WEBNOVEL_ALIGNMENT_STATUS.md`.
- Do not silently pretend checklist coverage exists when the repo does not implement it.
- When patching code, connect the change to at least one quality target and one repo-mapped module.
- Keep the app functional.
- Add or update tests when behavior changes.

## Current Runtime Center

- UI/runtime entrypoint: `app.py`
- Core generation and validation logic: `engine/`
- Market/rank support: `market_layer/`
- Portfolio scheduling: `portfolio_layer/`
- Revenue/campaign dashboards: `metaos_business/`

## First Priority

Raise the system toward stable production of high-quality Korean web novels.

Any future refactor should be judged by whether it improves that outcome or improves governance clarity for that outcome.
