# Code Architecture

LegalOps Agent is a small supervised workflow, not an autonomous legal adviser.

## Core components

### `models.py`

Defines the Pydantic contracts:

- `MatterIntake`
- `RiskFinding`
- `RoutingDecision`
- `ReviewDecision`
- `LegalOpsAssessment`

The export gate is enforced at model level. A record cannot set `export_allowed=true` unless the review state is `approved` and no blocker finding remains.

### `src/legal_ops.py`

Contains deterministic workflow logic:

- Builds a synthetic sample matter.
- Generates risk findings from matter type, data categories and customer commitments.
- Routes review to privacy, AI-governance, commercial or GC reviewers.
- Applies a human review decision with an audit note.

### `src/mcp_tools.py`

Exposes the local MCP-style tool surface:

- `legal.matter.assess`
- `legal.review.decide`
- `legal.sources.list`

### `runtime_agent/app.py`

Provides a small HTTP canary for CI and local testing. It exposes `/health`, `/mcp/manifest` and `/tools/call`.

### `master_orchestrator.py`

Runs the synthetic end-to-end demo and prints the initial and reviewed assessments as JSON.
