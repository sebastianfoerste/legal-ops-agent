# Legal Agent Governance Control Plane

**Synthetic snapshot: 2026-07-30T12:00:00+00:00**

## Demonstrated decisions

| Tool | Decision | Reasons |
| --- | --- | --- |
| `legal.sources.verify` | allowed | local_policy_allows_tool |
| `legal.review.decide` | approval_required | documented_human_approval_required |
| `legal.matter.assess` | blocked | blocked_source_prefix |
| `legal.external.send` | blocked | external_or_prohibited_action, unknown_tool_fail_closed |

## Runtime assurance

- Action events: 5
- Chain verified: True
- Kill switch active: False
- Raw arguments included: false
- External actions allowed: false

## Review gate

Only the human-facing local CLI can issue a consequential approval token. This demonstration issues no token and executes no consequential action.
