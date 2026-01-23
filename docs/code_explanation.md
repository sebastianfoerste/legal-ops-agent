# Code Architecture: Legal Agent

This project is structured as a **Hub-and-Spoke Multi-Agent System**.

## Core Components

### `master_orchestrator.py`
The brain of the operation. It uses the `GunnercookeOrchestrator` class to manage state and sequential execution.
- **State Management**: Keeps a `self.log` of all actions and `self.results` for the final JSON dump.
- **Pipelines**: Defined as methods (`run_recruiting_pipeline`, `run_content_pipeline`).
- **Error Handling**: Each step (Agent run) checks for errors before proceeding to the next.

### `agent.py`
A standalone "Content Agent" tailored for generic legal news newsjacking.
- **Search Logic**: Implements a robust 3-layer search fallback (DDG Specific -> DDG Broad -> Brave Search).
- **Scraping**: Uses `trafilatura` for clean text extraction.
- **Relevance Filter**: Uses a lightweight LLM call (`gemini-flash`) to strictly filter non-legal news.
- **Generation**: Uses `gemini-3-flash-preview` to write LinkedIn posts.

## Agents Directory (`agents/`)
Individual modules for specialized tasks.
- `agent_a_glass_ceiling_scout`: Profile analysis logic.
- `agent_b_rainmaker_profiler`: Revenue estimation logic.
- `agent_c_outreach_architect`: drafting logic.
- ...and others.

## Design Patterns
- **Chain of Responsibility**: The recruiting pipeline passes a candidate dict from Agent A through to D, enriching it at each step.
- **Fallback Search**: The `search_legal_news` function demonstrates high-reliability automation by handling failure at multiple provider levels.
- **Mock vs Real**: The orchestrator currently supports "Demo Mode" with injected sample data (see `sample_profiles` in `main`), but is wired for real inputs.
