from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from models import MatterIntake, ReviewDecision
from src.artifact_manifest import write_artifact_manifest
from src.exports import write_customer_commitment_register, write_source_verification_report
from src.legal_ops import apply_review_decision, assess_matter, build_sample_matter
from src.review_packet import write_review_packet
from src.review_packet_runner import write_source_verified_review_packet_run


def load_matter(path: Path | None) -> MatterIntake:
    if path is None:
        return build_sample_matter()
    return MatterIntake.model_validate_json(path.read_text(encoding="utf-8"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the LegalOps Agent workflow.")
    parser.add_argument("--input", type=Path, help="Path to an approved JSON matter intake file.")
    parser.add_argument("--json-output", type=Path, help="Write assessment JSON to this path.")
    parser.add_argument(
        "--packet-output", type=Path, help="Write markdown review packet to this path."
    )
    parser.add_argument(
        "--commitments-output",
        type=Path,
        help="Write the customer-commitment register JSON to this path.",
    )
    parser.add_argument(
        "--sources-output",
        type=Path,
        help="Write the source-verification report JSON to this path.",
    )
    parser.add_argument(
        "--manifest-output",
        type=Path,
        help="Write a local integrity manifest for generated review artifacts.",
    )
    parser.add_argument(
        "--review-runner-output",
        type=Path,
        help="Write a source-verified review packet runner JSON payload.",
    )
    parser.add_argument("--approve-note", help="Apply an approval note after assessment.")
    parser.add_argument(
        "--reviewer", default="General Counsel", help="Reviewer for approval notes."
    )
    return parser


def run(args: argparse.Namespace) -> dict[str, Any]:
    matter = load_matter(args.input)
    assessment = assess_matter(matter)

    if args.approve_note:
        assessment = apply_review_decision(
            assessment,
            ReviewDecision(reviewer=args.reviewer, state="approved", note=args.approve_note),
        )

    payload = assessment.model_dump(mode="json")
    artifacts: dict[str, Any] = {"assessment_json": payload}
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        artifacts["assessment_json"] = args.json_output
    if args.packet_output:
        write_review_packet(assessment, args.packet_output)
        artifacts["review_packet_markdown"] = args.packet_output
    if args.commitments_output:
        write_customer_commitment_register(assessment, args.commitments_output)
        artifacts["customer_commitment_register_json"] = args.commitments_output
    if args.sources_output:
        write_source_verification_report(assessment, args.sources_output)
        artifacts["source_verification_json"] = args.sources_output
    if args.review_runner_output:
        write_source_verified_review_packet_run(assessment, args.review_runner_output)
        artifacts["source_verified_review_packet_runner_json"] = args.review_runner_output
    if args.manifest_output:
        write_artifact_manifest(assessment, args.manifest_output, artifacts)
    return payload


def main() -> None:
    payload = run(build_parser().parse_args())
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
