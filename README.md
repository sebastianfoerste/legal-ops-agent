# LegalAgent Swarm 🤖⚖️

[![Stack](https://img.shields.io/badge/Stack-Python%20%7C%20AsyncIO%20%7C%20Pydantic-brightgreen?style=flat-square)](https://github.com/sebastianforste/legal_agent)
[![Domain](https://img.shields.io/badge/Domain-Legal%20Recruiting%20%26%20BD-blue?style=flat-square)](https://github.com/sebastianforste/legal_agent)
[![AI](https://img.shields.io/badge/AI-Google%20Gemini%20Pro-orange?style=flat-square)](https://ai.google.dev/)
[![Orchestration](https://img.shields.io/badge/Orchestration-Multi--Agent%20AsyncIO-purple?style=flat-square)](https://github.com/sebastianforste/legal_agent)
[![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square)](./LICENSE)

> **LegalAgent Swarm** is a production-grade, highly concurrent **Multi-Agent Intelligence Swarm** for automated legal recruiting, corporate partner headhunting, and strategic business development — powered by Python AsyncIO and Google Gemini Pro.

---

## 📋 Overview

Legal recruiting and business development in law firms is time-intensive, high-stakes, and repetitive. LegalAgent replaces manual candidate scouting, revenue profiling, and outreach drafting with a coordinated swarm of specialized AI agents that run concurrently — achieving a **3–5× throughput improvement** over sequential approaches.

**Core capabilities:**
- Automated candidate discovery and signals-based scouting
- Partner revenue estimation from public dockets and business records
- AI-driven outreach composition matching individual partner personas
- Calendar routing and scheduling automation
- Real-time regulatory and market monitoring

---

## 🏗️ Architecture

```
                        ┌──────────────────────┐
                        │  Master Orchestrator  │
                        │  (master_orchestrator) │
                        └──────────┬───────────┘
                                   │  AsyncIO Concurrent Execution
          ┌────────────────────────┼─────────────────────────┐
          ▼                        ▼                          ▼
  ┌───────────────┐      ┌─────────────────┐      ┌──────────────────┐
  │  Agent A      │      │  Agent B         │      │  Agent C          │
  │  Scout        │      │  Revenue         │      │  Outreach         │
  │               │      │  Profiler        │      │  Architect        │
  │ • Scouting    │      │ • Revenue est.   │      │ • Persona match   │
  │ • Signal scan │      │ • Risk analysis  │      │ • Tone compliance │
  └───────┬───────┘      └────────┬────────┘      └────────┬─────────┘
          │                       │                         │
          └───────────────────────┴─────────────────────────┘
                                  │
                                  ▼
                      ┌───────────────────────┐
                      │  Agent D: Concierge   │
                      │  Calendar routing &   │
                      │  triage scheduling    │
                      └───────────────────────┘
```

**Additional Agent Modules:**
| Agent | Role | Legal-Tech Function |
|-------|------|---------------------|
| Signal Hunter (E) | Market monitoring | Real-time regulatory & case law alerts |
| Thought Leader (F) | Content generation | High-status partner content for LinkedIn |
| Revenue Predictor (K) | Risk profiling | Partner retention risk assessment |
| Insolvency Finder (L) | BD intelligence | Identifies distressed companies for BD targeting |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Language** | Python 3.12+ |
| **Concurrency** | `asyncio`, `aiohttp` |
| **AI Model** | Google Gemini Pro / Flash (via `google-generativeai`) |
| **Data Validation** | Pydantic v2 (strict schema contracts) |
| **Build Tools** | `uv`, `ruff`, `mypy`, `pre-commit` |
| **Testing** | `pytest`, `pytest-asyncio` |
| **CI/CD** | GitHub Actions |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Google Gemini API Key ([get one here](https://ai.google.dev/))

### Installation

```bash
# Clone the repository
git clone https://github.com/sebastianforste/legal_agent.git
cd legal_agent

# Install dependencies (using uv — recommended)
pip install uv
uv pip install -r requirements.txt

# Or using standard pip
pip install -r requirements.txt
```

### Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Add your Gemini API key
echo "GEMINI_API_KEY=your_api_key_here" >> .env
```

### Running the Swarm

```bash
# Run the full agent pipeline
python master_orchestrator.py

# Or use the Makefile shortcuts
make install   # Install all dependencies
make run       # Execute the orchestrator
make check     # Run linting + type checks + tests
make test      # Run test suite only
```

---

## 📂 Project Structure

```
legal_agent/
├── agents/
│   ├── agent_a_glass_ceiling_scout.py    # Candidate signals scouting
│   ├── agent_b_rainmaker_profiler.py     # Revenue & risk profiling
│   ├── agent_c_outreach_architect.py     # Persona-matched outreach
│   ├── agent_d_scheduling_concierge.py   # Calendar routing
│   ├── agent_e_signal_hunter.py          # Regulatory monitoring
│   └── agent_f_thought_leader.py         # LinkedIn content generation
├── src/
│   └── ...                               # Core utilities
├── tests/                                 # pytest test suite
├── models.py                              # Shared Pydantic schemas
├── master_orchestrator.py                 # AsyncIO pipeline coordinator
├── recruiting_agent.py                    # Standalone recruiting workflow
├── agent.py                               # Base agent class
├── pyproject.toml                         # Project config (ruff, mypy)
├── requirements.in                        # Pinned dependencies
└── Makefile                               # Dev task shortcuts
```

---

## ⚖️ Legal-Tech Domain: Key Concepts

This project applies modern AI engineering to core **legal operations** and **law firm business development** challenges:

- **Contract Lifecycle Management (CLM)**: Signal-based monitoring of partner contract events and milestones
- **Compliance Automation**: Real-time statutory and regulatory change detection
- **eDiscovery Integration**: Document parsing and semantic indexing of legal texts
- **Legal Process Optimization**: Automated triage and workflow routing for intake processes
- **Regulatory Workflows**: Jurisdictional routing and compliance status tracking

---

## 🔬 Key Innovations

### 1. High-Concurrency AsyncIO Pipeline
All agents execute concurrently via Python's `asyncio` event loop. Candidate batches processed in **parallel** yield a 3–5× throughput improvement vs sequential LLM calls.

### 2. Rainmaker Revenue Profiler
Mathematical revenue estimation models applied to public court dockets and business records produce a structured "Partner Onboarding Viability Score" — quantifying book-of-business potential before outreach.

### 3. Persona-Matched Outreach Engine
Outreach campaigns are synthesized to match each target's communication style, seniority, and specialization — maintaining professional tone compliance without robotic boilerplate.

### 4. Pydantic Schema Contracts
All agent-to-agent data exchanges are validated through strict Pydantic v2 models, eliminating type mismatches and ensuring deterministic pipeline behavior at scale.

---

## ✅ Recent Milestones

- ✅ **Async refactor**: Full parallel candidate processing with `asyncio`
- ✅ **Type safety**: Pydantic v2 schemas for all agent data contracts
- ✅ **Performance**: 3–5× throughput on multi-candidate batches
- ✅ **Pre-commit hooks**: `ruff` + `mypy` enforced on every commit
- ✅ **Test suite**: `pytest-asyncio` integration and unit tests

---

## 🔒 Security & Compliance

- API keys managed via `.env` (never committed — see `.gitignore`)
- See [SECURITY.md](./SECURITY.md) for responsible disclosure
- All LLM outputs are validated through Pydantic schemas before persistence

---

## 📬 Contact & Portfolio

Built by **Sebastian Forste** — Legal Engineer & AI Architect

- 🌐 Portfolio: [sebastianforste.github.io](https://sebastianforste.github.io)
- 💼 LinkedIn: [linkedin.com/in/sebastianforste](https://linkedin.com/in/sebastianforste)
- 📧 Email: [sebastianforste@gmail.com](mailto:sebastianforste@gmail.com)

---

*Part of the [StrategyOS](https://github.com/sebastianforste/strategy-os) legal engineering ecosystem.*
