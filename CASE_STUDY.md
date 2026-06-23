# Case Study: Supervised Legal Operations Agent

## Legal problem

Recurring legal operations work often arrives as unstructured requests. A lawyer or legal operations team must understand the matter, identify risk, route it to the right reviewer and prevent premature external output.

When AI is added to this process, the main risk is not only wrong drafting. The larger risk is that a workflow jumps from intake to output without visible review, provenance or approval.

## Product problem

A useful legal AI workflow needs structure around the AI step. It should show what was submitted, how the matter was classified, who should review it and whether export is allowed.

The product challenge is to create a helpful agentic workflow without pretending that legal judgment has disappeared.

## Workflow design

The prototype models a supervised legal operations workflow with:

1. Typed matter intake
2. Deterministic risk triage
3. Reviewer routing
4. Review status
5. Approval controlled export

The design separates intake, classification, review and export so that the system can assist the legal team without bypassing human control.

## AI risk addressed

The project addresses:

1. Premature autonomous output
2. Invisible escalation decisions
3. Unclear review ownership
4. Loss of provenance between intake and output
5. Confusion between draft, reviewed and approved artifacts

## Human review model

The human reviewer remains the gatekeeper. The workflow can structure and route the matter, but final export depends on approval status.

This reflects the way professional legal teams actually work: automation can accelerate coordination and preparation, but approval remains visible and accountable.

## Evaluation or quality control

The project uses structured schemas, deterministic routing logic and tests to make the workflow predictable and reviewable.

The quality goal is not to maximize generation. The quality goal is to preserve control, traceability and review status.

## What I would improve next

1. Add an architecture diagram to the README
2. Add CLI screenshots showing intake, triage and blocked export
3. Add more synthetic matter types
4. Add audit log events for review and approval transitions
5. Add a reviewer dashboard or simple web UI
6. Add policy based routing rules that can be edited without changing code

## Relevance for Legal Engineer / Product Specialist roles

This project demonstrates practical understanding of supervised agentic legal workflows.

It is relevant for product roles where legal expertise must be translated into user journeys, review states, approval gates, escalation logic and trustworthy AI assisted outputs.
