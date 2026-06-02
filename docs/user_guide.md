# User Guide

## Run the demo

```bash
python -m pip install -r requirements.lock
python master_orchestrator.py
```

The demo creates a synthetic enterprise DPA review, generates risk findings, routes reviewers and applies a documented human approval. The first assessment blocks export. The reviewed assessment allows export because the synthetic findings contain no blocker severity.

## Generate a review packet

```bash
python -m src.cli \
  --input examples/matters/enterprise_dpa.json \
  --json-output demo_output/assessment.json \
  --packet-output demo_output/review-packet.md \
  --commitments-output demo_output/customer-commitments.json
```

The packet includes the matter summary, findings, controls, customer commitment register and audit trail. The commitment export writes the same customer-facing commitments as portable JSON.

## Call the local runtime

```bash
PORT=18085 python -m runtime_agent.app
```

Health check:

```bash
curl -fsS http://127.0.0.1:18085/health
```

MCP-style manifest:

```bash
curl -fsS http://127.0.0.1:18085/mcp/manifest
```

## Review gate

Approval, rejection, revision requests and escalation require written review notes. This is intentional. The system is designed for auditability, not one-click legal output.

## Data boundary

Use synthetic or approved public data only. External model calls remain disabled unless `LEGAL_AGENT_EXTERNAL_MODEL_ENABLED=true` is set deliberately.

Source references beginning with `client:`, `candidate:`, `privileged:` or `confidential:` are treated as blockers.
