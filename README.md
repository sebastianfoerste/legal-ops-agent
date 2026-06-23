# legal-ops-agent

Supervised legal-operations workflow: typed intake, deterministic risk triage, reviewer routing, human-approved export, audit trail. Not legal advice; data is synthetic.

> **If you don't code:** scroll to [What the demo produces](#what-the-demo-produces). This repo ships a sample output you can read in the browser. The point isn't the code; it's whether the legal work is structured, cited, reviewable, and testable.

![demo](docs/demo.png)

## Run it

```bash
git clone https://github.com/sebastianfoerste/legal-ops-agent
cd legal-ops-agent
make install
PYTHONPATH=. .venv/bin/python master_orchestrator.py
```

Runs end to end, offline and deterministically.

## What the demo produces

The workflow runs triage over a matter intake, generates deterministic findings, and routes to reviewers. Export remains blocked until a human reviewer records an approval decision. You can read the committed sample output: [`examples/matter-run.md`](examples/matter-run.md).

```markdown
# LegalOps Review Packet: Enterprise customer DPA review

- Review state: approved
- Export: allowed

## Routing
- Owner role: Privacy Counsel
- Reviewers: Legal Ops, Privacy Counsel, AI Governance Lead, Commercial Counsel, General Counsel

## Findings
- MEDIUM: privacy | Personal or customer data categories are in scope.
- HIGH: customer_commitments | The matter includes bespoke customer commitments.
- MEDIUM: ai_governance | AI processing or model-training restrictions require review.
```

In the sample run, export stays blocked until a reviewer approves — the audit trail shows who and when.

## What it checks / does

| Check / Step | Focus | Verification Method |
|---|---|---|
| Typed Matter Intake | Input validation | Ensures all details are provided according to strict Pydantic models |
| Risk Triage | Deterministic risk scoring | Catches known issues (e.g. data retention demands, specific vendor terms) |
| Source Verification | Provenance tracking | Verifies that references use allowed source prefixes and formats |

---

> **What workflow does this improve?** Recurring legal operations triage and gating.
> **Who is the user?** A General Counsel or Legal Operations lead running the workflow.
> **Where does human review happen?** At the Review Gate, which must be approved by the GC.
> **What is blocked until approval?** Persisted output and downstream data export.
> **What would I tell Product?** Real-world friction patterns and common DPA deviations to automate them in templates.

![Supervised review: a SaaS MSA matter triaged to high risk, routed to four reviewers, export blocked until human approval is recorded](docs/review-gate.svg)

## 90-second evaluator path

```bash
python3.13 -m venv .venv
source .venv/bin/activate
make install
python -m src.cli --input examples/matters/saas_msa_deviation.json
```

The first run returns `review_state: "needs_review"` and
`export_allowed: false`. Inspect the risk decision, reviewer routing, source
verification records and audit trail in the JSON output.

Approve the same synthetic matter with a documented human decision:

```bash
python -m src.cli \
  --input examples/matters/saas_msa_deviation.json \
  --approve-note "Approved after commercial counsel review of the synthetic MSA deviation." \
  --packet-output demo_output/saas-msa-review-packet.md \
  --manifest-output demo_output/saas-msa-artifact-manifest.json
```

Export remains blocked until approval is recorded, and it remains blocked after
approval if a blocker finding is still present.

Run the public proof gate:

```bash
make check
```

## Core workflow

```mermaid
flowchart TD
  A[Typed matter intake] --> B[Deterministic risk assessment]
  B --> C[Source verification]
  C --> D[Reviewer routing]
  D --> E[Human approval gate]
  E -->|Approved with note and no blockers| F[Export allowed]
  E -->|Needs review, rejected, revised, or blocker present| G[Export blocked]
  F --> H[Artifact manifest and review packet]
```

## Design principles

- Human review before consequential use.
- Deterministic rules before model synthesis.
- Pydantic schemas for every handoff.
- Review notes required for approval, rejection and escalation.
- Blocked source prefixes for client, candidate, privileged and confidential material.
- Public regulatory source verification without external fetching.
- Local MCP configuration for controlled tool access.
- Synthetic sample data only.

## Repository structure

- [`models.py`](models.py): Pydantic contracts for matters, findings, routing, review decisions and assessments.
- [`src/legal_ops.py`](src/legal_ops.py): Deterministic intake, risk and routing workflow.
- [`src/source_verification.py`](src/source_verification.py): Source-boundary verification for synthetic and public regulatory references.
- [`src/exports.py`](src/exports.py): Customer-commitment register export.
- [`src/mcp_tools.py`](src/mcp_tools.py): Local tool manifest and tool dispatcher for MCP-style integrations.
- [`src/review_packet.py`](src/review_packet.py): Markdown review-packet renderer for legal sign-off.
- [`src/cli.py`](src/cli.py): Fixture-driven command line entry point.
- [`examples/matters/`](examples/matters): Synthetic SaaS, DPA, AI-vendor, product and regulatory-monitoring fixtures.
- [`examples/clauses/`](examples/clauses): Synthetic redacted clause fixtures.
- [`runtime_agent/app.py`](runtime_agent/app.py): Small HTTP canary for health checks and local workflow calls.
- [`mcp.json`](mcp.json): Explicit local MCP server configuration.
- [`tests/`](tests): Unit tests for validation, risk logic, review gates, MCP manifest and runtime behavior.

## Quick start

Prerequisites: Python 3.13+.

```bash
git clone https://github.com/sebastianfoerste/legal-ops-agent
cd legal-ops-agent
python -m pip install -r requirements.lock
python master_orchestrator.py
```

The demo uses synthetic data and does not call an external model by default.

To assess a fixture and write a reviewer-ready packet:

```bash
python -m src.cli \
  --input examples/matters/enterprise_dpa.json \
  --json-output demo_output/assessment.json \
  --packet-output demo_output/review-packet.md \
  --commitments-output demo_output/customer-commitments.json \
  --sources-output demo_output/source-verification.json \
  --review-runner-output demo_output/source-verified-review-runner.json \
  --manifest-output demo_output/artifact-manifest.json
```

The manifest records SHA-256 digests for each generated review artifact and a
local integrity signature over the digest set. It is designed for reviewer
traceability. It is not an eIDAS signature.

## Checks

```bash
make check
```

This runs Ruff, Black, MyPy and Pytest.

## MCP surface

`mcp.json` exposes a local `legal-ops-agent` server with six controlled tools:

- `legal.matter.assess`: create a structured assessment from a typed legal matter.
- `legal.review.decide`: apply a documented human review decision.
- `legal.review.packet`: render a markdown review packet from an assessment.
- `legal.review.packet.run`: assess a matter and return the source-verified packet, source manifest and policy envelope in one payload.
- `legal.sources.list`: show the public or synthetic source boundary for the demo.
- `legal.sources.verify`: verify source-reference boundaries without fetching external content.

These tools are designed for local evaluation. They do not send client, candidate, matter or account data to an external system.

See [docs/API.md](docs/API.md) for input schemas, output schemas, safety limits
and example calls.

## What this proves

This repository demonstrates supervised legal operations as software. It shows
typed intake, deterministic triage, source-boundary controls, reviewer routing,
human approval gates, artifact manifests and local MCP-style tool calls. The
important signal is the control model: automation prepares the matter, but a
qualified human decision controls export.

## Safety note

This is a prototype. It does not provide legal advice, legal representation or filing-ready regulatory conclusions. Consequential legal work requires qualified human review, source verification and organisation-specific controls.

## Contact

Built by Sebastian Förste: [github.com/sebastianfoerste](https://github.com/sebastianfoerste)
