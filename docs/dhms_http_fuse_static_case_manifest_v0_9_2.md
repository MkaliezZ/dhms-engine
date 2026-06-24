# DHMS HTTP Fuse Static Case Manifest v0.9.2

## Purpose

v0.9.2 adds a static inert HTTP Fuse case manifest. The manifest records
synthetic HTTP/network request proposal cases as data-only safety contracts.

Audited base commit:

`275443c06aedb3c6ab6c1f62b6ceb951334217b2`

## Relationship to v0.9.0 and v0.9.1

v0.9.0 selected `HTTP / Network Request Safety Fuse` as the next DHMS proof
line after the SQL Sandbox Execution Fuse and File Operation Safety Fuse lines.

v0.9.1 planned inert HTTP/network request proposal fields, risk categories,
decision classes, trace expectations, future metrics, fail-closed behavior, and
approval requirements.

v0.9.2 is the static inert cases step only. It does not add a runner, examples,
HTTP clients, adapters, or network behavior.

## Bounded Claim

v0.9.2 adds a static inert HTTP Fuse case manifest containing synthetic HTTP/network request proposal cases as data-only safety contracts. It does not implement HTTP execution, perform network calls, create HTTP clients, add HTTP adapters, add benchmark runners, add examples, handle credentials, integrate MCP/provider/agent SDKs, or authorize real network activity.

## Manifest Path

`benchmarks/dhms_agentfuse_http_v0/cases.json`

## Case Schema Summary

The static manifest includes:

* `benchmark_id`
* `version`
* `proof_line`
* `case_count`
* `non_execution_invariant`
* `aggregate_counts`
* `cases`

Each case includes:

* `case_id`
* `request_intent`
* `method`
* `url`
* `scheme`
* `host`
* `path`
* `query_present`
* `headers_present`
* `credential_indicator`
* `body_present`
* `body_summary`
* `target_classification`
* `side_effect_risk`
* `data_exfiltration_risk`
* `ssrf_like_risk`
* `external_mutation_risk`
* `expected_decision`
* `expected_gate`
* `expected_trace_fields`
* `non_execution_requirement`

## Static Cases

The manifest contains exactly 16 cases:

1. `http_safe_public_get_allow_inert`
2. `http_query_present_hold_for_review`
3. `http_authorization_header_blocked`
4. `http_secret_query_blocked`
5. `http_post_external_api_blocked`
6. `http_delete_external_api_blocked`
7. `http_request_body_exfiltration_blocked`
8. `http_customer_data_exfiltration_blocked`
9. `http_webhook_trigger_blocked`
10. `http_localhost_target_blocked`
11. `http_metadata_service_target_blocked`
12. `http_private_network_target_blocked`
13. `http_unsupported_scheme_fail_closed`
14. `http_malformed_url_fail_closed`
15. `http_hidden_network_request_fail_closed`
16. `http_unknown_method_fail_closed`

## Expected Aggregate Counts

Expected manifest counts:

* `cases_total = 16`
* `allow_inert_count = 1`
* `hold_for_review_count = 1`
* `blocked_count = 10`
* `fail_closed_count = 4`
* `network_calls_executed_count = 0`
* `http_clients_created_count = 0`
* `credentials_used_count = 0`
* `external_mutation_attempted_count = 0`

## Non-Execution Invariant

`network_calls_executed_count == 0`

All URLs, methods, headers, query indicators, body summaries, and credential
indicators in the manifest are inert strings or booleans. The manifest must not
be interpreted as an HTTP client, an adapter, a browser action, or permission
to send network traffic.

## Explicit Non-Claims

v0.9.2 does not claim:

* real HTTP execution
* real network calls
* web browsing
* HTTP adapter support
* API client support
* credential handling
* SSRF protection
* production outbound request safety
* data exfiltration protection
* external API mutation safety
* webhook safety
* redirect safety
* MCP integration
* OpenClaw integration
* DeepSeek/provider integration
* provider SDK integration
* agent SDK integration
* shell execution
* arbitrary tool execution
* production readiness
* industry standard status
* replacement of MCP, guardrails, sandboxes, SDKs, or human approval systems

## Implementation Boundaries

v0.9.2 does not add:

* HTTP execution
* network calls
* HTTP clients
* HTTP adapters
* API clients
* credential handling
* HTTP benchmark runners
* HTTP examples
* validation runners
* socket usage
* web browsing
* MCP integration
* OpenClaw integration
* DeepSeek/provider integration
* provider SDK integration
* agent SDK integration
* arbitrary tool execution

## Next Recommended Milestone

`v0.9.3 Non-Executing HTTP Fuse Benchmark`

Final document verdict:

`READY_FOR_V0_9_3_NON_EXECUTING_HTTP_FUSE_BENCHMARK`
