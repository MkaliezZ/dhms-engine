# AgentFuse HTTP Policy Service Prototype

This example exposes the existing AgentFuse pre-dispatch decision API through
a minimal HTTP boundary. It lets a runtime written in Go, Rust, Java,
TypeScript, or another language request an `allow` or `block` decision without
importing the Python package directly.

AgentFuse already provides policy decisions, execution evidence, and runtime
integration patterns. This prototype adds language-neutral decision access for
one bounded example contract.

It is an experimental local example. It is not a production server, deployment
guide, authentication system, or replacement for packaged and external
AgentFuse integrations.

## Architecture

```text
External Agent Runtime
        |
        | HTTP request
        v
AgentFuse Policy Service
        |
        | decision
        v
Runtime execution boundary
```

The service evaluates policy only. The host runtime still owns tool execution,
approval, retries, persistence, and the final execution outcome.

## Contract

Send a JSON object to `POST /evaluate`:

```json
{
  "tool_call_id": "call-001",
  "tool_name": "delete_file",
  "arguments_digest": "sha256-example",
  "context": {
    "source": "example"
  }
}
```

Raw `arguments` are not accepted. The digest is treated as opaque boundary
metadata and is not copied into the response. The demo policy is intentionally
small:

- `read_profile` is allowed;
- `delete_file` and `transfer_money` are blocked; and
- every other tool fails closed because it is not allowlisted.

Allowed response:

```json
{
  "decision": "allow",
  "tool_call_id": "call-001"
}
```

Blocked response:

```json
{
  "decision": "block",
  "execution_status": "not_executed",
  "tool_call_id": "call-001"
}
```

`decision` and execution outcome remain separate. An `allow` response permits
the host to continue its own lifecycle; it does not claim that dispatch or
execution occurred. A `block` response carries `not_executed` because the
AgentFuse decision contains canonical non-execution evidence and this service
never dispatches a handler.

## Run Locally

From the repository root, install the package in editable mode and start the
server:

```bash
python -m pip install -e .
python -m examples.http_policy_service.server
```

In another terminal, run the example client:

```bash
python -m examples.http_policy_service.client
```

Expected output:

```json
{
  "decision": "allow",
  "tool_call_id": "call-read-001"
}
{
  "decision": "block",
  "execution_status": "not_executed",
  "tool_call_id": "call-delete-001"
}
```

## Run Tests

```bash
python -m pytest examples/http_policy_service/tests -q
```

The tests use a local ephemeral port and synthetic values. They make no model,
provider, database, filesystem mutation, or external network call.

## Boundaries

- This service does not execute tools or observe host execution outcomes.
- It does not provide authentication, authorization storage, deployment
  infrastructure, persistence, queues, or production API guarantees.
- The HTTP shape is an experimental adoption-boundary prototype, not a frozen
  public protocol.
- Existing AgentFuse runtime integrations and evidence semantics remain
  unchanged.
