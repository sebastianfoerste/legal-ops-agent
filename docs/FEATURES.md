# Features: LegalOps Agent

## Matter Assessment

Turns a typed `MatterIntake` into deterministic findings, control checks, reviewer routing, source verification records and audit events.

Implementation:

1. `models.py`
2. `src/legal_ops.py`
3. `tests/test_legal_ops.py`

## Source Verification

Classifies source references without external fetching. Synthetic references pass for demo use, public regulatory domains are allowlisted for review, and sensitive prefixes become blockers.

Implementation:

1. `src/source_verification.py`
2. `docs/tool-risk-registry.md`
3. `tests/test_source_verification.py`

## MCP-Style Tool Surface

Exposes controlled local tools for assessment, review decisions, review packets, source listing and source verification.

Implementation:

1. `src/mcp_tools.py`
2. `mcp.json`
3. `tests/test_mcp_tools.py`

## Review Packets And Artifact Manifests

Renders Markdown review packets and local integrity manifests for generated artifacts. The manifest records SHA-256 digests for traceability and is not an eIDAS signature.

Implementation:

1. `src/review_packet.py`
2. `src/artifact_manifest.py`
3. `tests/test_review_packet.py`
4. `tests/test_cli.py`

## Runtime Canary

Provides local health and tool-call endpoints for development and proof checks.

Implementation:

1. `runtime_agent/app.py`
2. `tests/test_runtime_agent.py`
