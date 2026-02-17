from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

WORKSPACE_NAME = "legal_agent"
SERVICE_NAME = "legal_agent_runtime_service"
ROOT_DIR = Path(__file__).resolve().parent.parent
TELEMETRY_DIR = ROOT_DIR / ".telemetry"
EVENT_LOG_PATH = TELEMETRY_DIR / "events.ndjson"
ACTIONS_LOG_PATH = TELEMETRY_DIR / "actions.ndjson"
STATE_PATH = ROOT_DIR / ".companion" / "state.json"
FEATURE_FLAG_KEY = "enable_legal_agent_automatic_dispatch"
SUPPORTED_ACTIONS = {
    "approve_outreach",
    "retry_pipeline",
    "pause_pipeline",
    "resume_pipeline",
    "dismiss_risk_alert",
}
ALLOWED_EVENT_NAMES = {
    "session_started",
    "onboarding_completed",
    "first_value_completed",
    "feature_engaged",
    "purchase_or_upgrade_initiated",
    "error_shown",
    "session_ended",
}
REQUIRED_EVENT_KEYS = {
    "event_name",
    "workspace_name",
    "user_id_hash",
    "session_id",
    "platform",
    "timestamp_utc",
    "properties",
}


def utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + "\n")


def read_state() -> dict[str, dict[str, Any]]:
    if not STATE_PATH.exists():
        return {}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def write_state(state: dict[str, dict[str, Any]]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def has_existing_actions() -> bool:
    if not ACTIONS_LOG_PATH.exists():
        return False
    return any(line.strip() for line in ACTIONS_LOG_PATH.read_text(encoding="utf-8").splitlines())


def is_valid_event_payload(payload: Any) -> bool:
    if not isinstance(payload, dict):
        return False
    if set(payload.keys()) != REQUIRED_EVENT_KEYS:
        return False
    if payload.get("workspace_name") != WORKSPACE_NAME:
        return False
    if payload.get("event_name") not in ALLOWED_EVENT_NAMES:
        return False
    if not isinstance(payload.get("properties"), dict):
        return False
    return True


def parse_env_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    return None


def is_feature_flag_enabled(flag_key: str) -> bool:
    payload = os.getenv("PRODUCT_CORE_FEATURE_FLAGS")
    if payload:
        try:
            parsed = json.loads(payload)
            if isinstance(parsed, dict) and isinstance(parsed.get(flag_key), bool):
                return bool(parsed[flag_key])
        except json.JSONDecodeError:
            pass

    values = [
        os.getenv(flag_key),
        os.getenv(flag_key.upper()),
        os.getenv(f"FLAG_{flag_key.upper()}"),
    ]
    for value in values:
        parsed = parse_env_bool(value)
        if parsed is not None:
            return parsed
    return False


class RuntimeHandler(BaseHTTPRequestHandler):
    server_version = "LegalAgentRuntime/1.0"

    def _write_json(self, status_code: int, payload: dict[str, Any]) -> None:
        content = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _read_json_body(self) -> Any:
        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            return json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            return None

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self._write_json(
                200,
                {
                    "status": "ok",
                    "service_name": SERVICE_NAME,
                    "version": os.getenv("APP_VERSION", "1.0.0"),
                    "timestamp_utc": utc_now_iso(),
                    "dependencies": [
                        {"name": "agent_orchestrator", "status": "ok", "latency_ms": 1},
                        {"name": "event_log_storage", "status": "ok", "latency_ms": 1},
                    ],
                },
            )
            return

        if parsed.path.startswith("/companion/status/"):
            execution_id = parsed.path.split("/")[-1]
            state = read_state()
            record = state.get(execution_id)
            if not record:
                self._write_json(404, {"error": "execution_not_found"})
                return
            self._write_json(200, record)
            return

        if parsed.path == "/companion/summary":
            state = read_state()
            pending = [
                record
                for record in state.values()
                if isinstance(record, dict) and str(record.get("status", "")).lower() == "accepted"
            ]
            self._write_json(
                200,
                {
                    "workspace_name": WORKSPACE_NAME,
                    "pending_actions": pending,
                    "pending_action_count": len(pending),
                    "return_to_pending_action": pending[0] if pending else None,
                    "recommended_actions": ["retry_pipeline", "dismiss_risk_alert"],
                    "generated_at_utc": utc_now_iso(),
                },
            )
            return

        self._write_json(404, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/api/product-core/events":
            payload = self._read_json_body()
            if not is_valid_event_payload(payload):
                self._write_json(400, {"accepted": False, "message": "invalid_event_schema"})
                return
            append_jsonl(EVENT_LOG_PATH, payload)
            self._write_json(202, {"accepted": True})
            return

        if self.path == "/companion/action":
            payload = self._read_json_body()
            if not isinstance(payload, dict):
                self._write_json(400, {"accepted": False, "error": "invalid_json"})
                return

            workspace_name = str(payload.get("workspace_name", ""))
            action_type = str(payload.get("action_type", ""))
            if workspace_name != WORKSPACE_NAME:
                self._write_json(400, {"accepted": False, "error": "invalid_workspace_name"})
                return
            if action_type not in SUPPORTED_ACTIONS:
                self._write_json(
                    400,
                    {"accepted": False, "error": "unsupported_action", "supported_actions": sorted(SUPPORTED_ACTIONS)},
                )
                append_jsonl(
                    EVENT_LOG_PATH,
                    {
                        "event_name": "error_shown",
                        "workspace_name": WORKSPACE_NAME,
                        "user_id_hash": "companion",
                        "session_id": f"error_{uuid.uuid4()}",
                        "platform": "runtime_agent",
                        "timestamp_utc": utc_now_iso(),
                        "properties": {
                            "source": "companion_action",
                            "message": "unsupported_action",
                            "entry_surface": "companion_api",
                            "release_version": "1.0.0",
                            "build_channel": os.getenv("ENVIRONMENT", "development"),
                        },
                    },
                )
                return
            if action_type == "approve_outreach" and not is_feature_flag_enabled(FEATURE_FLAG_KEY):
                self._write_json(
                    403,
                    {"accepted": False, "error": "feature_flag_disabled", "flag_key": FEATURE_FLAG_KEY},
                )
                append_jsonl(
                    EVENT_LOG_PATH,
                    {
                        "event_name": "error_shown",
                        "workspace_name": WORKSPACE_NAME,
                        "user_id_hash": "companion",
                        "session_id": f"error_{uuid.uuid4()}",
                        "platform": "runtime_agent",
                        "timestamp_utc": utc_now_iso(),
                        "properties": {
                            "source": "companion_action",
                            "message": "feature_flag_disabled",
                            "flag_key": FEATURE_FLAG_KEY,
                            "requested_action": action_type,
                            "entry_surface": "companion_api",
                            "release_version": "1.0.0",
                            "build_channel": os.getenv("ENVIRONMENT", "development"),
                        },
                    },
                )
                return

            execution_id = str(uuid.uuid4())
            accepted_at_utc = utc_now_iso()
            first_action = not has_existing_actions()
            record = {
                "execution_id": execution_id,
                "workspace_name": WORKSPACE_NAME,
                "action_type": action_type,
                "target_id": str(payload.get("target_id", "")),
                "requested_by": str(payload.get("requested_by", "companion_user")),
                "requested_at_utc": str(payload.get("requested_at_utc", accepted_at_utc)),
                "accepted_at_utc": accepted_at_utc,
                "status": "accepted",
            }
            state = read_state()
            state[execution_id] = record
            write_state(state)
            append_jsonl(ACTIONS_LOG_PATH, record)
            if first_action:
                append_jsonl(
                    EVENT_LOG_PATH,
                    {
                        "event_name": "session_started",
                        "workspace_name": WORKSPACE_NAME,
                        "user_id_hash": "companion",
                        "session_id": execution_id,
                        "platform": "runtime_agent",
                        "timestamp_utc": accepted_at_utc,
                        "properties": {
                            "entry": "companion_action",
                            "entry_surface": "companion_api",
                            "release_version": "1.0.0",
                            "build_channel": os.getenv("ENVIRONMENT", "development"),
                        },
                    },
                )
                append_jsonl(
                    EVENT_LOG_PATH,
                    {
                        "event_name": "onboarding_completed",
                        "workspace_name": WORKSPACE_NAME,
                        "user_id_hash": "companion",
                        "session_id": execution_id,
                        "platform": "runtime_agent",
                        "timestamp_utc": accepted_at_utc,
                        "properties": {
                            "flow": "first_companion_action",
                            "entry_surface": "companion_api",
                            "release_version": "1.0.0",
                            "build_channel": os.getenv("ENVIRONMENT", "development"),
                        },
                    },
                )
                append_jsonl(
                    EVENT_LOG_PATH,
                    {
                        "event_name": "first_value_completed",
                        "workspace_name": WORKSPACE_NAME,
                        "user_id_hash": "companion",
                        "session_id": execution_id,
                        "platform": "runtime_agent",
                        "timestamp_utc": accepted_at_utc,
                        "properties": {
                            "value_surface": "first_companion_action",
                            "entry_surface": "companion_api",
                            "release_version": "1.0.0",
                            "build_channel": os.getenv("ENVIRONMENT", "development"),
                        },
                    },
                )
            append_jsonl(
                EVENT_LOG_PATH,
                {
                    "event_name": "feature_engaged",
                    "workspace_name": WORKSPACE_NAME,
                    "user_id_hash": "companion",
                    "session_id": execution_id,
                    "platform": "runtime_agent",
                    "timestamp_utc": accepted_at_utc,
                    "properties": {
                        "feature": action_type,
                        "entry_surface": "companion_api",
                        "release_version": "1.0.0",
                        "build_channel": os.getenv("ENVIRONMENT", "development"),
                    },
                },
            )
            self._write_json(
                200,
                {
                    "accepted": True,
                    "execution_id": execution_id,
                    "status_url": f"/companion/status/{execution_id}",
                },
            )
            return

        self._write_json(404, {"error": "not_found"})


def run() -> None:
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "18085"))
    server = ThreadingHTTPServer((host, port), RuntimeHandler)
    print(f"legal_agent runtime service listening on {host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
