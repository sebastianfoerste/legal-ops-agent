import json

from src.cli import build_parser, run


def test_cli_writes_json_and_review_packet(tmp_path):
    json_output = tmp_path / "assessment.json"
    packet_output = tmp_path / "packet.md"
    commitments_output = tmp_path / "commitments.json"
    sources_output = tmp_path / "sources.json"
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
