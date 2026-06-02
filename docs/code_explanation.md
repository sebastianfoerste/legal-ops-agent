# Code Architecture

LegalOps Agent is a small supervised workflow, not an autonomous legal adviser.

## Core components

### `models.py`

Defines the Pydantic contracts:

- `MatterIntake`
- `RiskFinding`
- `RoutingDecision`
- `ControlCheck`
- `CustomerCommitmentRecord`
- `AuditEvent`
- `ReviewDecision`
- `LegalOpsAssessment`

The export gate is enforced at model level. A record cannot set `export_allowed=true` unless the review state is `approved`, a written review note is present and no blocker finding remains.

### `src/legal_ops.py`

Contains deterministic workflow logic:

- Builds a synthetic sample matter.
- Generates risk findings from matter type, data categories and customer commitments.
- Blocks client, candidate, privileged and confidential source references.
- Routes review to privacy, AI-governance, commercial or GC reviewers.
- Applies a human review decision with an audit note.

### `src/exports.py`

Builds and writes the customer-commitment register as portable JSON.

### `src/mcp_tools.py`

Exposes the local MCP-style tool surface:

- `legal.matter.assess`
- `legal.review.decide`
- `legal.review.packet`
- `legal.sources.list`

### `src/review_packet.py`

Renders a reviewer-ready markdown packet with findings, controls, customer commitments and audit events, including packet-generation evidence.

### `src/cli.py`

Loads approved JSON matter fixtures, runs the workflow and writes JSON and markdown outputs.

### `runtime_agent/app.py`

Provides a small HTTP canary for CI and local testing. It exposes `/health`, `/mcp/manifest` and `/tools/call`.

### `master_orchestrator.py`

Runs the synthetic end-to-end demo and prints the initial and reviewed assessments as JSON.
