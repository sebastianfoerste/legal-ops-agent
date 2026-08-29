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
    expected = {
        "agent-governance-control-plane.json": json.dumps(demo, indent=2) + "\n",
        "agent-governance-control-plane.md": render_governance_demo_markdown(demo),
        "agent-governance-control-plane.html": render_governance_demo_html(demo),
    }
    drift: list[str] = []
    for name, document in expected.items():
        path = ROOT / "examples" / name
        if not path.is_file():
            drift.append(f"missing committed artifact: examples/{name}")
        elif path.read_text(encoding="utf-8") != document:
            drift.append(f"generated artifact drift: examples/{name}")
    if drift:
        print("\n".join(drift))
        print("Run `make governance-demo` and commit the regenerated artifacts.")
        return 1
    print("governance demonstration check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
