# DHMS DeepSeek Real API Smoke Test Report

## Summary

* Status: PASS
* Real DeepSeek API used: yes
* Fallback used: no
* Total API calls: 9
* Total cases: 3
* Model: deepseek-chat
* Timestamp: 2026-06-19T11:39:03+00:00

## Environment

* DEEPSEEK_API_KEY present: true
* DEEPSEEK_MODEL: deepseek-chat
* Endpoint: DeepSeek chat completions

## Test Cases

### agent_memory_case

* Status: PASS
* v2_result_present: True
* real_api_result_present: True
* drift_analysis_present: True
* noise_estimation_present: True
* fallback_used: False
* latency_ms: 6134.982
* short response snippet: A memory perturbation test assesses system stability and error resilience by intentionally introducing controlled memory faults.

### long_conversation_case

* Status: PASS
* v2_result_present: True
* real_api_result_present: True
* drift_analysis_present: True
* noise_estimation_present: True
* fallback_used: False
* latency_ms: 6591.259
* short response snippet: The safest next action is to run a controlled comparison of the agent's outputs on the same input with and without the memory perturbation, using a predefined success metric.

### rag_context_case

* Status: PASS
* v2_result_present: True
* real_api_result_present: True
* drift_analysis_present: True
* noise_estimation_present: True
* fallback_used: False
* latency_ms: 6247.629
* short response snippet: The input must remain identical across regimes.

## Metric Integrity

* v2_results remained authoritative.
* v2_metrics_overridden = false
* DHMS metrics were not redefined.

## Failure Modes Observed

* none

## Productization Implications

* Is Product Layer safe to build now? yes
* Product Layer should expose API availability, fallback status, bounded call count, drift score, instability index, and v2 metric integrity.
* Product reports must show timeout, rate limit, auth failure, fallback use, response format mismatch, and adapter routing issues.

## Next Step Recommendation

* Proceed to DHMS Product Diagnosis v1.3
