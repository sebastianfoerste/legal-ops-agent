# Legal Agent - Gunnercooke Automation Suite

Legal Agent is a **Multi-Agent Intelligence Swarm** designed for legal recruiting and business development. It follows the [2026 StrategyOS Development Manifesto](file:///Users/sebastian/Developer/DEVELOPMENT_MANIFESTO_2026.md).

## 🚀 Features

### Recruiting Swarm (Agents A→D)
- **Glass Ceiling Scout**: Signals-based headhunting using autonomous browser agents.
- **Rainmaker Profiler**: Semantic revenue estimation and business case drafting.
- **Outreach Architect**: Hyper-personalized messaging using the StrategyOS Persona Engine.
- **Scheduling Concierge**: Context-aware calendar orchestration.

### Content Swarm (Agents E→F)
- **Signal Hunter**: Real-time regulatory and market monitoring.
- **Thought Leader Ghostwriter**: High-status content generation for partners.

### Additional Agents
- **Revenue Predictor** (Agent K): Risk assessment for partner retention
- **Insolvency Finder** (Agent L): Identifies distressed companies for business development

## 📦 Architecture

The system now uses **AsyncIO** for parallel execution:
- Candidates are processed concurrently (3-5x speedup)
- Shared data models via `models.py` (Pydantic) ensure type safety
- Master orchestrator (`master_orchestrator.py`) chains all agents

## 🛠️ Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure API keys in `.env`:
   ```
   GEMINI_API_KEY=your_key_here
   ```

3. Run the orchestrator:
   ```bash
   python master_orchestrator.py
   ```

## 📂 Project Structure

```
agents/
  ├── agent_a_glass_ceiling_scout.py
  ├── agent_b_rainmaker_profiler.py
  ├── agent_c_outreach_architect.py
  └── ...
models.py              # Shared Pydantic schemas
master_orchestrator.py # Async pipeline coordinator
```

## Recent Improvements

- ✅ **Async refactor**: Parallel candidate processing
- ✅ **Type safety**: Pydantic schemas for all agent data
- ✅ **Performance**: 3-5x faster on multi-candidate batches

## Run and Checks
<!-- CODEx_RUN_CHECKS -->
```bash
make install
make check
```
