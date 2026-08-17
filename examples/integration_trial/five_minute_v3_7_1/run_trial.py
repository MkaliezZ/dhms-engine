#!/usr/bin/env python3
"""Run the AgentFuse v3.7.1 public LangGraph consumer trial."""

from __future__ import annotations

import argparse
import json

from consumer import run_trial


FINAL_VERDICT = "AGENTFUSE_FIVE_MINUTE_INTEGRATION_TRIAL_V3_7_1_PASS"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args()
    result = run_trial()
    if args.json_only:
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
        return
    print(json.dumps(result, indent=2, sort_keys=True))
    print(FINAL_VERDICT)


if __name__ == "__main__":
    main()
