#!/usr/bin/env python3
import json
import sys


RESULT = {
    "case_id": "file_read_allowlisted_readme_candidate",
    "operation_type": "file_read_proposal",
    "requested_path_template": "README.md",
    "risk_tier": "L1",
    "sensitivity_flags": [
        "public_documentation_candidate",
        "allowlisted_path_candidate"
    ],
    "expected_safety_decision": "FAST_PASS_CANDIDATE",
    "expected_gate_state": "OBSERVED_OR_FAST_PASS_CANDIDATE",
    "expected_direct_execution_allowed": False,
    "direct_execution_allowed": False,
    "expected_executed": False,
    "actual_executed": False,
    "execution_result": None,
    "path_template_treated_as_inert": True,
    "path_template_opened": False,
    "path_template_resolved": False,
    "final_verdict": "DHMS_FILE_FUSE_EXAMPLE_PASS"
}


def main() -> int:
    print(json.dumps(RESULT, indent=2, sort_keys=True))
    return 0 if RESULT["final_verdict"] == "DHMS_FILE_FUSE_EXAMPLE_PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
