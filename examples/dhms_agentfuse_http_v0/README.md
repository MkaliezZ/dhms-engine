# DHMS HTTP Fuse Non-Executing Examples v0.9.4

These examples are static and non-executing. They illustrate how inert
HTTP/network request proposal cases map to DHMS safety decisions, execution
gates, and protocol lifecycle traces.

The examples map back to the v0.6 DHMS Execution Fuse Protocol lifecycle
through:

`docs/dhms_proof_line_protocol_lifecycle_mapping_v0_9_3_1.md`

## Files

* `non_executing_examples.json` contains 8 selected static examples from the
  v0.9.2 HTTP Fuse static manifest.
* `trace_examples.json` contains 4 static lifecycle trace examples.

## Non-Execution Boundary

These examples do not authorize HTTP execution. URLs, methods, headers, bodies,
credential indicators, and targets are inert documentation data only.

The examples do not create HTTP clients, sockets, browser actions, adapters,
API clients, credentials, or external mutations. They do not perform network
calls and do not add runtime behavior.

## Next Step

v0.9.5 should review and freeze the HTTP Fuse evidence chain.
