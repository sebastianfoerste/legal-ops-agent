# Sample Output

This file shows the current shape of the deterministic demo output. It is intentionally concise. The canonical source of truth is the CLI and the tests.

## Enterprise DPA Review

Run:

```bash
python -m src.cli \
  --input examples/matters/enterprise_dpa.json \
  --json-output demo_output/assessment.json \
  --packet-output demo_output/review-packet.md \
  --commitments-output demo_output/customer-commitments.json \
  --sources-output demo_output/source-verification.json
```

Expected assessment shape:

```json
{
  "assessment_id": "loa_c6ac9d9dddb6d43b",
  "review_state": "needs_review",
  "export_allowed": false,
  "findings": [
    {"category": "privacy", "severity": "medium"},
    {"category": "customer_commitments", "severity": "high"},
    {"category": "ai_governance", "severity": "medium"}
  ],
  "controls": [
    {"control_id": "source-boundary", "status": "pass"},
    {"control_id": "human-review-gate", "status": "pass"},
    {"control_id": "commitment-register", "status": "warning"},
    {"control_id": "data-map", "status": "warning"}
  ],
  "source_verifications": [
    {
      "source_ref": "synthetic:dpa-review-example",
      "category": "synthetic",
      "status": "pass",
      "requires_human_review": false
    }
  ]
}
```

The generated review packet includes findings, controls, source verification, customer commitments and an audit trail. Export remains blocked until a reviewer records an approval note.

## Public Regulatory Monitoring

Run:

```bash
python -m src.cli \
  --input examples/matters/public_regulatory_monitoring.json \
  --json-output demo_output/regulatory-assessment.json \
  --packet-output demo_output/regulatory-packet.md \
  --sources-output demo_output/regulatory-sources.json
```

Expected source-verification shape:

```json
{
  "source_verifications": [
    {
      "source_ref": "public:https://www.esma.europa.eu/",
      "category": "public_regulatory",
      "status": "pass",
      "public_authority": "esma.europa.eu",
      "requires_human_review": true
    }
  ]
}
```

This verifier checks source boundaries only. It does not fetch external content or state any current legal position.
