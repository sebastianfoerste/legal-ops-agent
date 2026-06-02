# LegalOps Agent Readiness

## Current status

Ready as a public portfolio prototype for supervised legal-operations workflows.

## Boundaries

- Synthetic demo data only.
- External model calls disabled by default.
- Human approval required before export.
- No client, candidate, matter or account data should be processed through external tools without explicit approval.

## Validation path

```bash
make check
python -m compileall master_orchestrator.py models.py src runtime_agent tests
```
