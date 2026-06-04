import json

from src.cli import build_parser, run


def test_cli_writes_json_and_review_packet(tmp_path):
    json_output = tmp_path / "assessment.json"
    packet_output = tmp_path / "packet.md"
    commitments_output = tmp_path / "commitments.json"
    sources_output = tmp_path / "sources.json"
    manifest_output = tmp_path / "manifest.json"
    parser = build_parser()
    args = parser.parse_args(
        [
            "--input",
            "examples/matters/enterprise_dpa.json",
            "--json-output",
            str(json_output),
            "--packet-output",
            str(packet_output),
            "--commitments-output",
            str(commitments_output),
            "--sources-output",
            str(sources_output),
            "--manifest-output",
            str(manifest_output),
        ]
    )

    payload = run(args)

    assert payload["export_allowed"] is False
    assert json.loads(json_output.read_text(encoding="utf-8"))["assessment_id"].startswith("loa_")
    assert "LegalOps Review Packet" in packet_output.read_text(encoding="utf-8")
    commitments = json.loads(commitments_output.read_text(encoding="utf-8"))
    assert commitments["assessment_id"] == payload["assessment_id"]
    assert len(commitments["commitments"]) == 3
    sources = json.loads(sources_output.read_text(encoding="utf-8"))
    assert sources["assessment_id"] == payload["assessment_id"]
    assert sources["source_verifications"][0]["status"] == "pass"
    manifest = json.loads(manifest_output.read_text(encoding="utf-8"))
    assert manifest["schema"] == "legal-ops-agent.artifact-manifest.v1"
    assert manifest["assessment_id"] == payload["assessment_id"]
    assert manifest["local_integrity_signature"]["algorithm"] == "sha256"
    assert len(manifest["local_integrity_signature"]["value"]) == 64
    assert {item["name"] for item in manifest["artifacts"]} == {
        "assessment_json",
        "review_packet_markdown",
        "customer_commitment_register_json",
        "source_verification_json",
    }
