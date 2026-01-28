# Legal Agent - Gunnercooke Automation Suite

A multi-agent system for legal recruiting, content generation, and business development automation.

## 🚀 Features

### Recruiting Pipeline (Agents A→B→C→D)
- **Glass Ceiling Scout**: Identifies frustrated high-performers using LinkedIn signals
- **Rainmaker Profiler**: Estimates portable revenue and generates business cases
- **Outreach Architect**: Creates personalized recruitment messages
- **Scheduling Concierge**: Automates calendar prep and briefing documents

### Content Pipeline (Agents E→F)
- **Signal Hunter**: Monitors regulatory changes, competitor moves, and market signals
- **Thought Leader Ghostwriter**: Generates LinkedIn posts for partners

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
