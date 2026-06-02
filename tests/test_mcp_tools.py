import pytest

from src.legal_ops import build_sample_matter
from src.mcp_tools import legal_ops_mcp_manifest, run_tool


def test_mcp_manifest_exposes_controlled_tools():
    manifest = legal_ops_mcp_manifest()
    tool_names = {tool["name"] for tool in manifest["tools"]}
    assert tool_names == {
        "legal.matter.assess",
        "legal.review.decide",
        "legal.sources.list",
    }


def test_mcp_assess_tool_returns_blocked_assessment():
    result = run_tool("legal.matter.assess", build_sample_matter().model_dump(mode="json"))
    assert result["review_state"] == "needs_review"
    assert result["export_allowed"] is False


def test_mcp_rejects_unknown_tool():
    with pytest.raises(ValueError):
        run_tool("legal.unknown", {})
