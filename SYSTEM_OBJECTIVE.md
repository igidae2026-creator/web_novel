## System Objective

This repository exists to build a web-novel production system that can repeatedly generate outputs perceived as upper-tier by general readers.

The system objective is:

`stable 24-hour unattended production of high-ranking web-novel quality`

Operational interpretation:
- generic readability is necessary but insufficient
- domain competitiveness for Korean web novels is mandatory
- the system must optimize for repeated pass rates against quality gates
- architecture, prompts, validators, repair logic, and repo mapping must all support that objective
- internal automation alone is insufficient if it only operates on already-included scope
- the system also needs outer-loop automation that can evaluate newly arrived material, decide whether it belongs inside the active scope, and automatically promote it when it strengthens the product objective
- the practical success criterion is a state where later human intervention produces little additional quality lift

Production target:
- increase the probability that a generated work is judged commercially competitive
- reduce dependence on one-off model luck
- preserve a patchable governance stack from rules to repo implementation
- reduce the operational need for human triage, routing, and quality rescue during 24-hour runs
