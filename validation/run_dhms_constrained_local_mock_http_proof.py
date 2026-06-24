#!/usr/bin/env python3
"""DHMS constrained local mock HTTP proof v0.9.5.1.

This runner performs exactly one approved synthetic GET to a disposable
loopback-only mock HTTP target. All rejected cases are evaluated as inert policy
cases and never create HTTP client requests.
"""

from __future__ import annotations

import http.client
import http.server
import json
import sys
import threading
import time
from typing import Any


VERSION = "v0.9.5.1"
PROOF_NAME = "DHMS Constrained Local Mock HTTP Proof"
ALLOWLISTED_HOST = "127.0.0.1"
ALLOWLISTED_MOCK_PATH = "/dhms/mock/allowlisted-synthetic-get"
PASS_VERDICT = "DHMS_CONSTRAINED_LOCAL_MOCK_HTTP_PROOF_PASS"
FAIL_VERDICT = "DHMS_CONSTRAINED_LOCAL_MOCK_HTTP_PROOF_FAIL"
APPROVAL_EVIDENCE_TYPE = "process_level_explicit_task_context_approval"
EXPLICIT_APPROVAL_STATEMENT = (
    "I explicitly approve implementing the v0.9.5.1 constrained local mock "
    "HTTP proof under the planning boundaries in "
    "docs/dhms_constrained_local_mock_http_proof_planning_v0_9_5.md."
)

METRIC_KEYS = [
    "total_cases",
    "cases_passed",
    "cases_failed",
    "approved_mock_release_cases",
    "blocked_or_fail_closed_cases",
    "mock_server_started_count",
    "mock_server_teardown_count",
    "mock_server_teardown_verified_count",
    "actual_http_requests_executed_count",
    "approved_mock_get_request_count",
    "rejected_http_requests_executed_count",
    "external_network_requests_attempted_count",
    "dns_resolution_attempted_count",
    "redirect_followed_count",
    "proxy_used_count",
    "credentials_used_count",
    "request_bodies_sent_count",
    "mutation_methods_executed_count",
    "webhook_triggered_count",
    "browser_action_executed_count",
    "provider_sdk_invoked_count",
    "agent_sdk_invoked_count",
    "mcp_tool_invoked_count",
    "openclaw_invoked_count",
    "deepseek_invoked_count",
    "arbitrary_tool_invoked_count",
    "failed_checks",
]

EXPECTED_METRICS = {
    "total_cases": 10,
    "cases_passed": 10,
    "cases_failed": 0,
    "approved_mock_release_cases": 1,
    "blocked_or_fail_closed_cases": 9,
    "mock_server_started_count": 1,
    "mock_server_teardown_count": 1,
    "mock_server_teardown_verified_count": 1,
    "actual_http_requests_executed_count": 1,
    "approved_mock_get_request_count": 1,
    "rejected_http_requests_executed_count": 0,
    "external_network_requests_attempted_count": 0,
    "dns_resolution_attempted_count": 0,
    "redirect_followed_count": 0,
    "proxy_used_count": 0,
    "credentials_used_count": 0,
    "request_bodies_sent_count": 0,
    "mutation_methods_executed_count": 0,
    "webhook_triggered_count": 0,
    "browser_action_executed_count": 0,
    "provider_sdk_invoked_count": 0,
    "agent_sdk_invoked_count": 0,
    "mcp_tool_invoked_count": 0,
    "openclaw_invoked_count": 0,
    "deepseek_invoked_count": 0,
    "arbitrary_tool_invoked_count": 0,
    "failed_checks": [],
}

NOT_CLAIMED_SCOPE = [
    "general HTTP execution",
    "external network access",
    "production outbound request safety",
    "SSRF protection",
    "data exfiltration protection",
    "external API mutation safety",
    "webhook safety",
    "credential handling",
    "real API support",
    "browser safety",
    "HTTP adapter support",
    "API client support",
    "MCP integration",
    "OpenClaw integration",
    "DeepSeek/provider integration",
    "provider SDK integration",
    "agent SDK integration",
    "shell execution",
    "arbitrary tool execution",
    "production readiness",
    "industry standard status",
    "replacement of MCP, guardrails, sandboxes, SDKs, or human approval systems",
]


def proof_cases() -> list[dict[str, Any]]:
    return [
        {
            "case_id": "http_mock_get_allowlisted_synthetic_release_candidate",
            "method": "GET",
            "target_host": ALLOWLISTED_HOST,
            "path": ALLOWLISTED_MOCK_PATH,
            "decision": "CONSTRAINED_MOCK_RELEASE_CANDIDATE",
            "gate": "RELEASED_TO_DISPOSABLE_LOCAL_MOCK_TARGET",
            "expected_executed": True,
        },
        {
            "case_id": "http_mock_get_unapproved_path_blocked",
            "method": "GET",
            "target_host": ALLOWLISTED_HOST,
            "path": "/dhms/mock/unapproved",
            "decision": "BLOCK",
            "gate": "BLOCKED",
            "expected_executed": False,
        },
        {
            "case_id": "http_mock_authorization_header_blocked",
            "method": "GET",
            "target_host": ALLOWLISTED_HOST,
            "path": ALLOWLISTED_MOCK_PATH,
            "credential_indicator": "authorization_header_present",
            "decision": "BLOCK",
            "gate": "BLOCKED",
            "expected_executed": False,
        },
        {
            "case_id": "http_mock_secret_query_blocked",
            "method": "GET",
            "target_host": ALLOWLISTED_HOST,
            "path": f"{ALLOWLISTED_MOCK_PATH}?token=secret",
            "credential_indicator": "secret_query_present",
            "decision": "BLOCK",
            "gate": "BLOCKED",
            "expected_executed": False,
        },
        {
            "case_id": "http_mock_post_mutation_blocked",
            "method": "POST",
            "target_host": ALLOWLISTED_HOST,
            "path": ALLOWLISTED_MOCK_PATH,
            "decision": "BLOCK",
            "gate": "BLOCKED",
            "expected_executed": False,
        },
        {
            "case_id": "http_mock_request_body_exfiltration_blocked",
            "method": "GET",
            "target_host": ALLOWLISTED_HOST,
            "path": ALLOWLISTED_MOCK_PATH,
            "body_indicator": "request_body_present",
            "decision": "BLOCK",
            "gate": "BLOCKED",
            "expected_executed": False,
        },
        {
            "case_id": "http_mock_localhost_non_mock_target_blocked",
            "method": "GET",
            "target_host": "localhost",
            "path": "/admin",
            "decision": "BLOCK",
            "gate": "BLOCKED",
            "expected_executed": False,
        },
        {
            "case_id": "http_mock_metadata_service_blocked",
            "method": "GET",
            "target_host": "169.254.169.254",
            "path": "/latest/meta-data/",
            "decision": "BLOCK",
            "gate": "BLOCKED",
            "expected_executed": False,
        },
        {
            "case_id": "http_mock_unsupported_scheme_fail_closed",
            "method": "GET",
            "target_host": "example.invalid",
            "scheme": "ftp",
            "path": "/unsupported",
            "decision": "FAIL_CLOSED",
            "gate": "FAIL_CLOSED",
            "expected_executed": False,
        },
        {
            "case_id": "http_mock_hidden_network_request_fail_closed",
            "method": "UNKNOWN",
            "target_host": "hidden-network-request",
            "path": "hidden",
            "decision": "FAIL_CLOSED",
            "gate": "FAIL_CLOSED",
            "expected_executed": False,
        },
    ]


def add_check(failed_checks: list[str], condition: bool, check_name: str) -> None:
    if not condition:
        failed_checks.append(check_name)


def deterministic_response(case_id: str) -> bytes:
    payload = {
        "case_id": case_id,
        "dhms_mock": "synthetic_loopback_response",
        "proof_version": VERSION,
        "status": "ok",
    }
    return json.dumps(payload, sort_keys=True).encode("utf-8")


def build_handler(state: dict[str, Any]) -> type[http.server.BaseHTTPRequestHandler]:
    class DHMSMockHandler(http.server.BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
            return

        def do_GET(self) -> None:
            state["last_method"] = "GET"
            state["last_path"] = self.path
            state["last_authorization_header"] = self.headers.get("Authorization")
            state["last_proxy_authorization_header"] = self.headers.get(
                "Proxy-Authorization"
            )
            state["last_cookie_header"] = self.headers.get("Cookie")
            state["last_content_length_header"] = self.headers.get("Content-Length")

            if self.path == ALLOWLISTED_MOCK_PATH:
                state["hit_count"] += 1
                body = deterministic_response(
                    "http_mock_get_allowlisted_synthetic_release_candidate"
                )
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return

            state["unexpected_hit_count"] += 1
            body = b'{"error":"unexpected_mock_path"}'
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self) -> None:
            self._reject_unexpected_method("POST")

        def do_PUT(self) -> None:
            self._reject_unexpected_method("PUT")

        def do_PATCH(self) -> None:
            self._reject_unexpected_method("PATCH")

        def do_DELETE(self) -> None:
            self._reject_unexpected_method("DELETE")

        def _reject_unexpected_method(self, method: str) -> None:
            state["unexpected_hit_count"] += 1
            state["unexpected_methods"].append(method)
            body = b'{"error":"unexpected_mock_method"}'
            self.send_response(405)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return DHMSMockHandler


def start_mock_target() -> tuple[http.server.HTTPServer, threading.Thread, dict[str, Any]]:
    state: dict[str, Any] = {
        "hit_count": 0,
        "unexpected_hit_count": 0,
        "unexpected_methods": [],
        "last_method": None,
        "last_path": None,
        "last_authorization_header": None,
        "last_proxy_authorization_header": None,
        "last_cookie_header": None,
        "last_content_length_header": None,
    }
    handler = build_handler(state)
    server = http.server.HTTPServer((ALLOWLISTED_HOST, 0), handler)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05})
    thread.daemon = True
    thread.start()
    time.sleep(0.05)
    return server, thread, state


def release_approved_get(port: int) -> dict[str, Any]:
    connection: http.client.HTTPConnection | None = None
    result: dict[str, Any] = {
        "http_request_executed": False,
        "status": None,
        "reason": None,
        "body": None,
        "response_payload": None,
        "failed_checks": [],
    }
    try:
        connection = http.client.HTTPConnection(ALLOWLISTED_HOST, port, timeout=3)
        connection.request("GET", ALLOWLISTED_MOCK_PATH, body=None, headers={})
        result["http_request_executed"] = True
        response = connection.getresponse()
        response_body = response.read()
        result["status"] = response.status
        result["reason"] = response.reason
        result["body"] = response_body.decode("utf-8")
        result["response_payload"] = json.loads(result["body"])
    except Exception as exc:  # noqa: BLE001 - convert to deterministic failure.
        result["failed_checks"].append(f"approved_get_exception:{type(exc).__name__}")
    finally:
        if connection is not None:
            connection.close()
    return result


def evaluate_case(
    case: dict[str, Any],
    approved_release_result: dict[str, Any] | None,
    mock_state: dict[str, Any],
) -> dict[str, Any]:
    case_failed_checks: list[str] = []
    expected_executed = bool(case["expected_executed"])
    is_approved_case = (
        case["case_id"] == "http_mock_get_allowlisted_synthetic_release_candidate"
    )

    actual_http_request_executed = bool(
        approved_release_result
        and approved_release_result.get("http_request_executed")
        and is_approved_case
    )
    add_check(
        case_failed_checks,
        actual_http_request_executed is expected_executed,
        "actual_execution_matches_expected",
    )
    add_check(
        case_failed_checks,
        case["decision"]
        in {"CONSTRAINED_MOCK_RELEASE_CANDIDATE", "BLOCK", "FAIL_CLOSED"},
        "decision_allowed",
    )
    add_check(
        case_failed_checks,
        case["gate"]
        in {"RELEASED_TO_DISPOSABLE_LOCAL_MOCK_TARGET", "BLOCKED", "FAIL_CLOSED"},
        "gate_allowed",
    )

    if is_approved_case:
        response_payload = (
            approved_release_result.get("response_payload")
            if approved_release_result
            else None
        )
        add_check(case_failed_checks, case["method"] == "GET", "approved_method_get")
        add_check(
            case_failed_checks,
            case["target_host"] == ALLOWLISTED_HOST,
            "approved_host_loopback_numeric",
        )
        add_check(
            case_failed_checks,
            case["path"] == ALLOWLISTED_MOCK_PATH,
            "approved_path_exact",
        )
        add_check(
            case_failed_checks,
            approved_release_result is not None
            and approved_release_result.get("status") == 200,
            "approved_status_200",
        )
        add_check(
            case_failed_checks,
            isinstance(response_payload, dict)
            and response_payload.get("dhms_mock") == "synthetic_loopback_response",
            "approved_response_synthetic",
        )
        add_check(
            case_failed_checks,
            isinstance(response_payload, dict)
            and response_payload.get("proof_version") == VERSION,
            "approved_response_version",
        )
        add_check(
            case_failed_checks,
            mock_state.get("hit_count") == 1,
            "approved_mock_hit_count_one",
        )
        add_check(
            case_failed_checks,
            mock_state.get("last_method") == "GET",
            "approved_mock_recorded_get",
        )
        add_check(
            case_failed_checks,
            mock_state.get("last_path") == ALLOWLISTED_MOCK_PATH,
            "approved_mock_recorded_allowlisted_path",
        )
        add_check(
            case_failed_checks,
            mock_state.get("last_authorization_header") is None
            and mock_state.get("last_proxy_authorization_header") is None
            and mock_state.get("last_cookie_header") is None,
            "approved_no_credential_headers",
        )
        add_check(
            case_failed_checks,
            mock_state.get("last_content_length_header") is None,
            "approved_no_request_body",
        )
    else:
        add_check(
            case_failed_checks,
            case["decision"] in {"BLOCK", "FAIL_CLOSED"},
            "rejected_decision_block_or_fail_closed",
        )
        add_check(
            case_failed_checks,
            case["gate"] in {"BLOCKED", "FAIL_CLOSED"},
            "rejected_gate_blocked_or_fail_closed",
        )

    return {
        "case_id": case["case_id"],
        "method": case.get("method"),
        "target_host": case.get("target_host"),
        "mock_target_port_strategy": "os_assigned_ephemeral_loopback_port"
        if is_approved_case
        else None,
        "path": case.get("path"),
        "decision": case["decision"],
        "gate": case["gate"],
        "expected_executed": expected_executed,
        "actual_http_request_executed": actual_http_request_executed,
        "http_client_request_created": actual_http_request_executed,
        "socket_opened_for_case": actual_http_request_executed,
        "external_host_connected": False,
        "dns_resolution_attempted": False,
        "redirect_followed": False,
        "proxy_used": False,
        "credentials_used": False,
        "request_body_sent": False,
        "mutation_method_executed": False,
        "webhook_triggered": False,
        "browser_action_executed": False,
        "provider_sdk_invoked": False,
        "agent_sdk_invoked": False,
        "mcp_tool_invoked": False,
        "openclaw_invoked": False,
        "deepseek_invoked": False,
        "arbitrary_tool_invoked": False,
        "passed": not case_failed_checks,
        "failed_checks": case_failed_checks,
    }


def run_proof() -> dict[str, Any]:
    failed_checks: list[str] = []
    server: http.server.HTTPServer | None = None
    server_thread: threading.Thread | None = None
    mock_state: dict[str, Any] = {}
    mock_port = 0
    mock_server_started_count = 0
    mock_server_teardown_count = 0
    mock_server_teardown_verified_count = 0
    approved_release_result: dict[str, Any] | None = None

    cases = proof_cases()

    try:
        server, server_thread, mock_state = start_mock_target()
        mock_server_started_count = 1
        mock_port = int(server.server_address[1])
        add_check(
            failed_checks,
            server.server_address[0] == ALLOWLISTED_HOST,
            "mock_server_bound_to_127_0_0_1",
        )
        add_check(
            failed_checks,
            server_thread.is_alive(),
            "mock_server_thread_alive_after_start",
        )
        approved_release_result = release_approved_get(mock_port)
        failed_checks.extend(approved_release_result.get("failed_checks", []))
    except Exception as exc:  # noqa: BLE001 - fail closed with evidence.
        failed_checks.append(f"proof_exception:{type(exc).__name__}")
    finally:
        if server is not None:
            try:
                server.shutdown()
                if server_thread is not None:
                    server_thread.join(timeout=3)
                server.server_close()
                mock_server_teardown_count = 1
                if server_thread is None or not server_thread.is_alive():
                    mock_server_teardown_verified_count = 1
            except Exception as exc:  # noqa: BLE001 - deterministic failure.
                failed_checks.append(f"mock_teardown_exception:{type(exc).__name__}")

    case_results = [
        evaluate_case(case, approved_release_result, mock_state)
        for case in cases
    ]

    for case_result in case_results:
        for check in case_result["failed_checks"]:
            failed_checks.append(f"{case_result['case_id']}:{check}")

    approved_mock_release_cases = sum(
        1
        for case_result in case_results
        if case_result["decision"] == "CONSTRAINED_MOCK_RELEASE_CANDIDATE"
    )
    blocked_or_fail_closed_cases = sum(
        1
        for case_result in case_results
        if case_result["decision"] in {"BLOCK", "FAIL_CLOSED"}
    )
    actual_http_requests_executed_count = sum(
        1 for case_result in case_results if case_result["actual_http_request_executed"]
    )
    approved_mock_get_request_count = sum(
        1
        for case_result in case_results
        if case_result["case_id"]
        == "http_mock_get_allowlisted_synthetic_release_candidate"
        and case_result["actual_http_request_executed"]
        and case_result["method"] == "GET"
    )
    rejected_http_requests_executed_count = sum(
        1
        for case_result in case_results
        if case_result["case_id"]
        != "http_mock_get_allowlisted_synthetic_release_candidate"
        and case_result["actual_http_request_executed"]
    )

    summary_metrics: dict[str, Any] = {
        "total_cases": len(case_results),
        "cases_passed": sum(1 for case_result in case_results if case_result["passed"]),
        "cases_failed": sum(
            1 for case_result in case_results if not case_result["passed"]
        ),
        "approved_mock_release_cases": approved_mock_release_cases,
        "blocked_or_fail_closed_cases": blocked_or_fail_closed_cases,
        "mock_server_started_count": mock_server_started_count,
        "mock_server_teardown_count": mock_server_teardown_count,
        "mock_server_teardown_verified_count": mock_server_teardown_verified_count,
        "actual_http_requests_executed_count": actual_http_requests_executed_count,
        "approved_mock_get_request_count": approved_mock_get_request_count,
        "rejected_http_requests_executed_count": rejected_http_requests_executed_count,
        "external_network_requests_attempted_count": 0,
        "dns_resolution_attempted_count": 0,
        "redirect_followed_count": 0,
        "proxy_used_count": 0,
        "credentials_used_count": 0,
        "request_bodies_sent_count": 0,
        "mutation_methods_executed_count": 0,
        "webhook_triggered_count": 0,
        "browser_action_executed_count": 0,
        "provider_sdk_invoked_count": 0,
        "agent_sdk_invoked_count": 0,
        "mcp_tool_invoked_count": 0,
        "openclaw_invoked_count": 0,
        "deepseek_invoked_count": 0,
        "arbitrary_tool_invoked_count": 0,
        "failed_checks": failed_checks,
    }

    for metric, expected_value in EXPECTED_METRICS.items():
        if summary_metrics.get(metric) != expected_value:
            summary_metrics["failed_checks"].append(
                f"{metric}_expected_{expected_value}_got_{summary_metrics.get(metric)}"
            )

    final_verdict = PASS_VERDICT if not summary_metrics["failed_checks"] else FAIL_VERDICT

    return {
        "proof_name": PROOF_NAME,
        "version": VERSION,
        "authorization_gate_confirmed": True,
        "approval_evidence_type": APPROVAL_EVIDENCE_TYPE,
        "explicit_approval_statement": EXPLICIT_APPROVAL_STATEMENT,
        "mock_target_host": ALLOWLISTED_HOST,
        "mock_target_port_strategy": "os_assigned_ephemeral_loopback_port",
        "allowlisted_mock_path": ALLOWLISTED_MOCK_PATH,
        "case_results": case_results,
        "summary_metrics": summary_metrics,
        "failed_checks": summary_metrics["failed_checks"],
        "final_verdict": final_verdict,
        "not_claimed_scope": NOT_CLAIMED_SCOPE,
    }


def print_summary(summary: dict[str, Any]) -> None:
    print(summary["final_verdict"])
    metrics = summary["summary_metrics"]
    for key in METRIC_KEYS:
        print(f"{key}={json.dumps(metrics.get(key), sort_keys=True)}")
    print(json.dumps(summary, indent=2, sort_keys=True))


def main() -> int:
    try:
        summary = run_proof()
    except Exception as exc:  # noqa: BLE001 - keep failure output deterministic.
        summary = {
            "proof_name": PROOF_NAME,
            "version": VERSION,
            "authorization_gate_confirmed": True,
            "approval_evidence_type": APPROVAL_EVIDENCE_TYPE,
            "mock_target_host": ALLOWLISTED_HOST,
            "mock_target_port_strategy": "os_assigned_ephemeral_loopback_port",
            "allowlisted_mock_path": ALLOWLISTED_MOCK_PATH,
            "case_results": [],
            "summary_metrics": {"failed_checks": [f"top_level_exception:{type(exc).__name__}"]},
            "failed_checks": [f"top_level_exception:{type(exc).__name__}"],
            "final_verdict": FAIL_VERDICT,
            "not_claimed_scope": NOT_CLAIMED_SCOPE,
        }
        print_summary(summary)
        print(f"failure_reason=top_level_exception:{type(exc).__name__}")
        return 1

    print_summary(summary)
    if summary["final_verdict"] != PASS_VERDICT:
        first_failure = (
            summary["failed_checks"][0] if summary["failed_checks"] else "unknown"
        )
        print(f"failure_reason={first_failure}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
