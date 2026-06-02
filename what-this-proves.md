# What This Proves for a General Counsel Candidate

This repository serves as a concrete proof of work demonstrating the legal engineering and operational capabilities required of a first General Counsel at an AI-native SaaS company.

## 1. Legal Workflows as Structured Internal Product Infrastructure
Traditional legal teams operate reactively via email inboxes. This repository demonstrates the ability to translate recurring legal tasks into structured, scalable Python workflows:
- **Typed Handoffs and Pydantic Schemas**: Matters, risk findings, reviewer routing, review decisions, and assessments are modeled as strict Pydantic classes (`models.py`).
- **Deterministic Risk Triage**: Every request is validated and triaged programmatically through rules (such as custom data retention, GDPR special category data, copyleft licenses). This makes routine intake self-serve and routes high-stakes issues directly to the GC.
- **Reviewer Routing**: Based on the urgency, type, and risk profile of a matter, the engine determines the required approvals and routes to the appropriate human reviewers (e.g. DPO, GC, InfoSec).

## 2. Technical Alignment with Core Engineering and Product
A General Counsel in an AI-native company must speak the same language as the engineering and product teams:
- **Local MCP Server Integration**: Exposes core legal functions as a Model Context Protocol (MCP) server (`mcp.json`). This shows how the legal function can interface directly with AI systems, allowing developers or customer agents to query risk assessment and review states programmatically.
- **Robust Software Hygiene**: Pytest unit test suites, linting, Ruff style enforcement, and type checking verify that legal tools can be held to the same operational standards as production software.

## 3. Practical AI Governance and Risk Mitigation
For a platform running agents on customer data, this prototype implements real-world governance boundaries:
- **Zero Autonomous Legal Advice**: The system is designed to check rules and compile information, but **never** creates final legal decisions or submissions.
- **Hard Approval Gates**: Assessments are locked and export is blocked until a qualified human lawyer submits a signed review decision and note.
- **Redaction & Data Hygiene**: Synthetic data fixtures are used to prevent leakage of client-confidential or candidate-specific material.
