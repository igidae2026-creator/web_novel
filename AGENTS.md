# Autonomous Development Agent

This repository operates with an autonomous development loop.

The agent working in this repository must continuously improve the system by identifying and resolving the highest-leverage bottleneck.

The goal is to maintain and improve a **high-quality automated web-novel generation system with long-run reliability guarantees**.

---

# Core Objective

Improve the system without degrading protected quality axes.

The system must evolve through iterative improvement while maintaining deterministic validation and regression protection.

---

# Development Loop

Each cycle must follow this process:

1. Inspect repository state:
   - code
   - tests
   - docs
   - runtime signals
   - system_status metrics

2. Identify the **single most impactful bottleneck**.

3. Generate **2–3 candidate improvements**.

4. Select the option with the best:
   - impact
   - risk
   - implementation cost

5. Implement the change.

6. Run validation:
   - deterministic tests
   - static checks
   - simulation if needed

7. Reject the change if it introduces regression.

8. Report the result:


bottleneck
action taken
files modified
validation result
balanced_total delta
next bottleneck


9. Continue the next cycle automatically.

---

# Protected Quality Axes

Changes must **never materially degrade** these axes.

- fun
- coherence
- character persuasiveness
- pacing / rhythm
- reader retention
- emotional immersion
- information design
- long-run sustainability
- character chemistry
- world logic
- stability

Regression guard must block changes that harm these dimensions.

---

# System Signals

Use runtime metrics when available:

- balanced_total
- repair_rate
- drift detection
- portfolio signals
- release cadence
- simulation outputs (30/60/120 episode runs)

These signals should guide bottleneck selection.

---

# Preferred Improvements

Favor improvements that increase **structural leverage**, such as:

- architecture clarity
- causal correctness
- repair effectiveness
- portfolio coordination
- release scheduling quality
- long-run narrative stability
- evaluation robustness

Avoid low-value churn such as cosmetic refactors.

---

# Implementation Rules

- Work on **one bottleneck per cycle**.
- Keep the system functional at all times.
- Prefer small but high-impact changes.
- Update or add tests when behavior changes.
- Maintain deterministic execution where possible.
- Document architectural changes.

---

# Stop Condition

Stop only if:

- improvements become marginal, or
- a real external blocker appears.

Otherwise continue iterating.

---

# Mission Summary

This repository implements a **self-improving web-novel generation system**.

The agent must continuously evolve the system while protecting quality and ensuring long-run reliability.
