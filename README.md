# LegalAgent Swarm

A supervised multi-agent prototype for legal operations, structured intake, risk triage, review routing and human-approved outputs.

[![Stack](https://img.shields.io/badge/Stack-Python%20%7C%20AsyncIO%20%7C%20Pydantic-brightgreen?style=flat-square)](https://github.com/sebastianforste/legal_agent)
[![Domain](https://img.shields.io/badge/Domain-Legal%20Operations-blue?style=flat-square)](https://github.com/sebastianforste/legal_agent)
[![AI](https://img.shields.io/badge/AI-Google%20Gemini%20Pro-orange?style=flat-square)](https://ai.google.dev/)
[![Orchestration](https://img.shields.io/badge/Orchestration-Multi--Agent%20AsyncIO-purple?style=flat-square)](https://github.com/sebastianforste/legal_agent)
[![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square)](./LICENSE)

## Overview

LegalAgent demonstrates how a coordinated set of specialized AI agents can handle structured legal operations work: matter intake, product counsel review, contract risk review, regulatory monitoring and approval workflow design.

Each agent handles a bounded task, passes typed outputs to the next stage, and routes to a human approval step before any output is persisted or acted upon. The architecture is intentionally supervisor-controlled rather than autonomous.

**Core capabilities:**
- Structured matter intake and classification
- Contract risk triage and routing to appropriate review workflows
- Regulatory change monitoring with summarization and alert drafting
- Product counsel review support for privacy, AI governance and vendor contracts
- Approval gate design with escalation logic and audit trail
- Calendar routing and scheduling coordination

## Architecture

A **Master Orchestrator** manages asynchronous concurrent execution across specialized agents using Python AsyncIO. Each agent communicates through strict Pydantic schema contracts, ensuring all agent-to-agent data exchanges are validated before processing.

**Agents:**
- **Intake Agent:** Classifies and structures incoming matters by type, urgency and routing path
- **Review Agent:** Applies rule-based and LLM-assisted risk analysis to contracts and regulatory documents
- **Monitor Agent:** Tracks regulatory sources and generates structured change alerts
- **Concierge Agent:** Handles scheduling, routing and human-in-the-loop handoff

**Additional modules:**
- **Signal Hunter:** Real-time regulatory and case law alerts
- **Approval Router:** Escalation triggers, data minimisation and reusable legal playbooks

## Tech Stack

- **Language:** Python 3.12+
- **Concurrency:** `asyncio`, `aiohttp`
- **AI Model:** Google Gemini Pro / Flash
- **Data Validation:** Pydantic v2
- **Build/CI:** `uv`, `ruff`, `mypy`, GitHub Actions
- **Testing:** `pytest`, `pytest-asyncio`

## Quick Start

**Prerequisites:** Python 3.12+ and a Google Gemini API Key.

```bash
# Clone and install
git clone https://github.com/sebastianforste/legal_agent
cd legal_agent
pip install -r requirements.txt

# Configure
cp .env.example .env
# Add GEMINI_API_KEY to .env

# Run
python master_orchestrator.py
# or
make run
```

## Legal-Tech Domain Concepts

The project covers:

- **Contract Lifecycle Management (CLM):** Monitoring contract events and triggering review workflows
- **Compliance Automation:** Real-time regulatory change detection and structured summarization
- **Legal Process Optimization:** Automated triage, routing and human approval gates
- **Audit Trail Design:** Schema-validated outputs with persistence only after human review

## Key Design Decisions

1. **Human-in-the-loop by default:** No output is acted upon without an explicit approval step
2. **Schema-first communication:** Pydantic contracts enforce data integrity across all agent boundaries
3. **High-concurrency AsyncIO:** Parallel processing of intake items without blocking the review pipeline
4. **Modular agents:** Each agent can be tested, replaced or extended independently

## Security

API keys are managed via `.env` and never logged. All LLM outputs undergo Pydantic schema validation before persistence. See [SECURITY.md](./SECURITY.md) for responsible disclosure.

## Contact

Built by Sebastian Forste — [sebastianforste.github.io](https://sebastianforste.github.io/)
