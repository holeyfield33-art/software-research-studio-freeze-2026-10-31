"""Deterministic threat-to-test planning. Never executes a test or scans a target."""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any

VERSION = "0.1.0"
MAX_BYTES = 1_048_576
MAX_THREATS = 40
_ID = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,63}$")

# These are candidate test contracts, not evidence of an exploit or permission to test.
PATTERNS = {
    "path_traversal": {
        "hypothesis": "Path handling could escape an explicitly allowed fixture root.",
        "positive_control": "Known in-root file is accepted and its exact content is accounted for.",
        "negative_control": "A controlled outside-root path and symlink alias are refused or recorded as unknown.",
        "oracle": "Independent fixture manifest and host-observed path resolution; response text alone is insufficient.",
    },
    "prompt_injection": {
        "hypothesis": "Untrusted content could be mistaken for a higher-priority instruction.",
        "positive_control": "Authorized benign document contents remain processable.",
        "negative_control": "A deliberately planted instruction in fixture text cannot change permitted operations.",
        "oracle": "Host-owned policy and externally observed actions, not the agent's own assurance.",
    },
    "tool_authority": {
        "hypothesis": "A claimed caller or purpose could be mistaken for verified tool authority.",
        "positive_control": "An explicit trusted-host grant permits one bounded fixture request.",
        "negative_control": "A caller value supplied only in untrusted input cannot grant access.",
        "oracle": "Trusted-host decision and action receipt bound to the exact attempted operation.",
    },
    "secret_exposure": {
        "hypothesis": "Sensitive fixture data could appear in an output or diagnostic.",
        "positive_control": "Public marker remains visible in the expected output.",
        "negative_control": "A known synthetic private canary never appears in exported results.",
        "oracle": "Independent canary comparison against complete output bytes and logs; non-disclosure alone does not prove no read.",
    },
}

class IntakeError(ValueError):
    """A malformed/unsupported intake. No plan should be produced."""


def _pairs_unique(pairs: list[tuple[str, Any]]) -> dict:
    out = {}
    for key, value in pairs:
        if key in out:
            raise IntakeError(f"Duplicate JSON key: {key}")
        out[key] = value
    return out


def parse_input(raw: bytes) -> dict:
    if len(raw) > MAX_BYTES:
        raise IntakeError("Intake exceeds the 1 MiB limit")
    try:
        obj = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs_unique,
                         parse_constant=lambda x: (_ for _ in ()).throw(IntakeError("Non-finite number")))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IntakeError(f"Invalid UTF-8 JSON: {exc}") from exc
    if not isinstance(obj, dict):
        raise IntakeError("Intake must be an object")
    return obj


def _closed(obj: Any, keys: set[str], label: str):
    if not isinstance(obj, dict):
        raise IntakeError(f"{label} must be an object")
    if set(obj) != keys:
        raise IntakeError(f"{label} keys mismatch: expected {', '.join(sorted(keys))}")


def _safe_string(value: Any, field: str, limit: int = 240) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit or any(ord(ch) < 32 or 0xD800 <= ord(ch) <= 0xDFFF for ch in value):
        raise IntakeError(f"{field} must be a nonempty short printable string")
    return value.strip()


def validate_intake(data: dict) -> None:
    _closed(data, {"version", "project_id", "subject", "scope", "threats"}, "intake")
    if data["version"] != VERSION:
        raise IntakeError("Unsupported intake version")
    if not isinstance(data["project_id"], str) or not _ID.fullmatch(data["project_id"]):
        raise IntakeError("Invalid project_id")
    _safe_string(data["subject"], "subject")
    scope = data["scope"]
    _closed(scope, {"review_owner", "fixture_only", "network_allowed"}, "scope")
    _safe_string(scope["review_owner"], "review_owner", 80)
    # This greenfield experiment is deliberately limited to planning controlled fixtures.
    if scope["fixture_only"] is not True or scope["network_allowed"] is not False:
        raise IntakeError("Only offline fixture planning is supported")
    threats = data["threats"]
    if not isinstance(threats, list) or not 1 <= len(threats) <= MAX_THREATS:
        raise IntakeError(f"Provide 1..{MAX_THREATS} threats")
    seen = set()
    for i, threat in enumerate(threats):
        _closed(threat, {"id", "kind", "component", "observation"}, f"threat[{i}]")
        tid = threat["id"]
        if not isinstance(tid, str) or not _ID.fullmatch(tid) or tid in seen:
            raise IntakeError("Threat IDs must be valid and unique")
        seen.add(tid)
        if not isinstance(threat["kind"], str) or threat["kind"] not in PATTERNS:
            raise IntakeError(f"Unknown threat kind in {tid}")
        _safe_string(threat["component"], f"component {tid}", 120)
        _safe_string(threat["observation"], f"observation {tid}", 500)


def canonical(obj: Any) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                       allow_nan=False) + "\n").encode("utf-8")


def build_plan(data: dict) -> dict:
    validate_intake(data)
    # Item order is normalized to make output independent of the order threats were entered.
    checks = []
    for item in sorted(data["threats"], key=lambda x: x["id"]):
        pattern = PATTERNS[item["kind"]]
        checks.append({
            "case_id": f"case-{item['id']}",
            "threat_id": item["id"],
            "kind": item["kind"],
            "component": item["component"].strip(),
            "observed_claim": item["observation"].strip(),
            "hypothesis": pattern["hypothesis"],
            "positive_control": pattern["positive_control"],
            "negative_control": pattern["negative_control"],
            "independent_oracle": pattern["oracle"],
            "execution": "NOT_RUN",
            "evidence": "NONE",
            "result": "UNKNOWN",
            "stop_trigger": "Stop without a scope-bound trusted host grant or independently observed oracle",
        })
    return {
        "plan_version": VERSION,
        "generator": "agent-b-scanplan-offline",
        "project_id": data["project_id"],
        "subject": data["subject"].strip(),
        "input_sha256": hashlib.sha256(canonical(data)).hexdigest(),
        "scope": {"mode": "LOCAL_FIXTURE_PLANNING", "network": "DISALLOWED",
                  "review_owner": data["scope"]["review_owner"].strip()},
        "execution_authority": "UNVERIFIED",
        "release_disposition": "HOLD",
        "coverage": {"requested": len(checks), "planned": len(checks), "executed": 0},
        "checks": checks,
        "limitations": [
            "Threat descriptions are untrusted claims, not confirmed vulnerabilities.",
            "Authorization fields are declarations, not verified host permissions.",
            "No scan, probe, network activity, test execution or release decision occurs.",
            "Risk and research applicability require independent project review.",
        ],
    }
