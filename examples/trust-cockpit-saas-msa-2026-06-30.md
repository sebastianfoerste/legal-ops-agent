# LegalOps Trust Cockpit: SaaS MSA deviation review

## Evidence Metadata
- Schema: legal-ops-agent.trust-cockpit.v1
- Assessment: loa_0b5d728ed132582a
- Generated: 2026-06-30T18:55:59Z
- Fixture: examples/matters/saas_msa_deviation.json
- Command: `python -m src.cli --input examples/matters/saas_msa_deviation.json --json-output demo_output/assessment.json --packet-output demo_output/review-packet.md --commitments-output demo_output/customer-commitments.json --sources-output demo_output/source-verification.json --review-runner-output demo_output/source-verified-review-runner.json --manifest-output demo_output/artifact-manifest.json --trust-cockpit-output examples/trust-cockpit-saas-msa-2026-06-30.md --trust-cockpit-json-output examples/trust-cockpit-saas-msa-2026-06-30.json`
- Python: 3.13.14
- Application version: 0.1.0
- Source runner schema: legal-ops-agent.source-verified-review-packet-run.v1

## Decision State
- Status: review_required
- Review state: needs_review
- Export allowed: false
- Human review required: true
- Highest severity: high
- Findings: 2
- Blockers: 0
- Owner role: Privacy Counsel
- Reviewers: Legal Ops, Privacy Counsel, Commercial Counsel, General Counsel
- SLA hours: 24

## Source Boundary
- Boundary: verified_demo_or_public_regulatory_sources
- Pass: 1
- Warning: 0
- Blocker: 0
- pass: synthetic:saas-msa-deviation-example (synthetic, review=False)

## Review Gate
- Delivery mode: local_review_only
- External actions allowed: false
- Blocked actions: external_delivery, publication, filing, outreach
- Legal advice status: draft_for_human_review

## Commitments
- Count: 3
- Review required: 3
- Owner roles: Commercial Counsel
- higher liability cap for security incidents | owner=Commercial Counsel | source=synthetic:saas-msa-deviation-example
- controlled annual audit right | owner=Commercial Counsel | source=synthetic:saas-msa-deviation-example
- non-binding roadmap review | owner=Commercial Counsel | source=synthetic:saas-msa-deviation-example

## Artifact Integrity
- Manifest schema: legal-ops-agent.artifact-manifest.v1
- Artifact count: 5
- Local integrity: sha256 14ce8a2d7460a5dc542e5d8c3655cc5c0ff2359665d72b1c3e1eeffd6c4166bd
- assessment_json: c96f732b4262380b568c874a4a7bdbadd5975e18f2956e5e90db5f75cb4b3bb6 (4247 bytes)
- customer_commitment_register_json: 20075426d24f82bef01118bbf7a143827cec5740093d17092e7bceb5752c06de (770 bytes)
- review_packet_markdown: cb5e6e7b25592e2d585e9ecf7123c8f2c4e2965965725bdcf719e32a79ae5c6a (2869 bytes)
- source_verification_json: 4e776746d98a80e06474dd3433f3e87154a069cf8ad9f124ecfdff8452df2971 (408 bytes)
- source_verified_review_packet_runner_json: ef9baee288714ee46dd9471b8c4dc08c88a21fe7fad4d78518517959ce5a92d7 (5416 bytes)

## Next Actions
- Record a documented human review decision before export.
- Record customer commitments in the obligations register before signature.
- Confirm DPA roles, transfer basis, subprocessors and deletion mechanics.
- Record each commitment in the customer obligations register before approval.
