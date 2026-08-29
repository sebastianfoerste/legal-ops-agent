from __future__ import annotations

import json
from pathlib import Path

from src.governance_demo import (
    build_governance_demo,
    render_governance_demo_html,
    render_governance_demo_markdown,
)

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    demo = build_governance_demo()
    output = ROOT / "examples"
    output.mkdir(parents=True, exist_ok=True)
    (output / "agent-governance-control-plane.json").write_text(
        json.dumps(demo, indent=2) + "\n",
        encoding="utf-8",
    )
    (output / "agent-governance-control-plane.md").write_text(
        render_governance_demo_markdown(demo),
        encoding="utf-8",
    )
    (output / "agent-governance-control-plane.html").write_text(
        render_governance_demo_html(demo),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
