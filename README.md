# Surplus Autonomy – Agent Test Harness (Colab-first)

This repo is a production-aligned, Colab-friendly framework for testing agentic AI
modules (agents) in isolation with deterministic fixtures.

## Key properties
- Strict agent input/output contract
- Mode gating: TEST / DRY_RUN / LIVE
- Network gating: OFF (fixtures) / ON (live HTTP)
- Artifact output with SHA-256 hashing
- Auditable run results

## Quick Start (Google Colab)
1) Open Colab
2) Run:
```python
!git clone https://github.com/<YOUR_USER_OR_ORG>/surplus-autonomy-agents.git
%cd surplus-autonomy-agents
