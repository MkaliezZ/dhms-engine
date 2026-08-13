# Hermes #53021 External Proof

This proof models one session policy from NousResearch/hermes-agent issue #53021.
It is not a Hermes integration and does not modify Hermes.

The modeled rule is deny by default with one allowed command shape for skill scripts.
The proof verifies one allowed call, blocked calls, retry of the same blocked call,
and deterministic re-evaluation of that blocked call. Blocked calls do not start
the protected in-memory handler. Safe receipts contain an arguments digest rather
than the original command text.

Run:

```bash
python examples/external_integrations/hermes_53021/session_allowlist_proof.py
python -m pytest tests/test_hermes_53021_external_proof.py -q
```

Expected demo verdict:

```text
AGENTFUSE_HERMES_53021_EXTERNAL_PROOF_PASS
```

The re-evaluation case is not a claim about Hermes restart persistence. A real
consumer remains responsible for session lifecycle, approval state, dispatch,
and physical outcome recording.
