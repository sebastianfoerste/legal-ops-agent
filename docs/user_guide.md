# Legal Agent Orchestrator - User Guide

The **Legal Agent Orchestrator** is an autonomous multi-agent system designed for **Gunnercooke** to automate high-value partner recruiting, content generation, and risk monitoring.

## 🚀 Quick Start

### 1. Requirements
Ensure you have the required dependencies:
```bash
pip install -r requirements.txt
```
(Requires `google-generative-ai`, `duckduckgo-search`, `trafilatura`, `beautifulsoup4`, `python-dotenv`)

### 2. Environment Setup
Create a `.env` file in the root directory:
```bash
GOOGLE_API_KEY=your_gemini_key_here
```

### 3. Running the Orchestrator
The main entry point is `master_orchestrator.py`. It runs the demonstration pipelines.

```bash
python master_orchestrator.py
```

By default, this will trigger:
1.  **Content Pipeline**: Search for legal signals and generate LinkedIn posts.
2.  **Summary Generation**: Print a report of all actions.
3.  **Result Saving**: Outputs `orchestrator_results.json`.

---

## 🧩 Pipelines Explained

### 1. Recruiting Pipeline (Agents A → B → C → D)
*Automated Headhunting for High-Value Partners.*
- **Agent A (Glass Ceiling Scout)**: Analyzes LinkedIn profiles to calculate a "Frustration Score" (likelihood of moving).
- **Agent B (Rainmaker Profiler)**: Estimates portable book of business (Revenue). Filters candidates < €200k.
- **Agent C (Outreach Architect)**: Drafts hyper-personalized outreach messages based on the candidate's recent wins.
- **Agent D (Scheduling Concierge)**: Handlers scheduling and briefing.

### 2. Content Pipeline (Agents E → F)
*Thought Leadership Automation.*
- **Agent E (Signal Hunter)**: Scans legal news (DuckDuckGo/Brave) for regulatory updates or insolvency news.
- **Agent F (Ghostwriter)**: Writes viral LinkedIn posts in the voice of a "Senior Partner" based on the signals.

### 3. Daily Dashboard (Agents K, L, E)
*Risk & Opportunity Monitor.*
- **Agent K (Revenue Predictor)**: Checks partner financials for risk (Revenue drops).
- **Agent L**: Insolvency finder (Not yet fully active).

---

## 📂 Output Files
- `orchestrator_results.json`: Complete dump of all pipeline data.
- `LinkedIn_Posts/`: Markdown files containing generated content (from `agent.py` standalone runs).
