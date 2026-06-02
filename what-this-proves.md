# What This Proves for a General Counsel Candidate

This repository is a public proof of legal engineering for an AI-native SaaS legal function. It shows how legal work can be decomposed into typed intake, deterministic controls, reviewer routing and human-approved outputs.

## Structured Legal Operations

The app turns a legal matter into a `MatterIntake`, deterministic `RiskFinding` records, `ControlCheck` records, `SourceVerificationRecord` records and a `LegalOpsAssessment`. The result is a legal workflow that engineering teams can inspect, test and integrate.

The current demo covers:

- Enterprise DPA review.
- AI product-launch review.
- Public regulatory monitoring.
- Customer-commitment tracking.
- Source-boundary verification.
- Human review gates before export.

## Source And Data Discipline

The app treats source boundaries as product architecture. Synthetic demo sources pass. Public regulatory references are checked against a fixed domain allowlist without network access. Sensitive prefixes such as `client:`, `candidate:`, `privileged:` and `confidential:` become blocker inputs.

This matters for a legal AI function because confidentiality and provenance need to be built into the workflow, rather than added as prose after the fact.

## Human Review Gates

Assessments begin in `needs_review`. Export remains blocked until a reviewer records an approval decision with a sufficiently detailed note. Blocker findings continue to prevent export after approval.

The architecture therefore supports AI-assisted legal operations while preserving review, accountability and human judgment.

## Engineering Signal

The repo uses Pydantic contracts, deterministic functions, a local MCP-style tool surface, CLI fixtures, runtime health checks and tests for validation, source boundaries, review gates, packet generation and documentation integrity.

For a first General Counsel role at an AI-native SaaS company, that is the practical signal: legal judgment translated into systems that product and engineering teams can use safely.
