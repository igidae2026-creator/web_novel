# OPS_RUNBOOK

## Canonical Stack
- `event log -> typed snapshots -> job queue -> supervisor`
- do not introduce supervisor-first background automation without the lower layers
- outer-loop automation must cover new material intake, scope selection, promotion, rejection, and recovery

## Contracts Rule
- one canonical owner locks runtime contracts
- other sessions review and try to break contracts instead of silently redefining them
- post-lock changes require `proposal -> review -> version bump`
- version compatibility impact must be written before rollout

## Start
- docker-compose up --build

## Backup
- backup outputs/ and data/ daily.

## Recovery
- restore outputs/<project>/state.json to resume.
- prefer recovery from logged events and validated snapshots over manual state surgery
