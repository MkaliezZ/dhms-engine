# DHMS SQL/File/HTTP Evidence Alignment v0.9.8

## Purpose

v0.9.8 aligns the public evidence presentation for the three completed DHMS
proof lines: SQL, File, and HTTP.

This milestone is evidence-alignment only. It does not add runtime behavior,
execution capability, CLI commands, adapters, API clients, credential handling,
SDK integration, MCP integration, OpenClaw integration, DeepSeek integration, or
new proof semantics.

DHMS is an execution fuse protocol for AI agents. DHMS AgentFuse is the
benchmark, demo, API, and adapter-skeleton tool family around that protocol.

## Three-Line Evidence Matrix

| Proof line | Required classification | Current evidence | Public command |
| --- | --- | --- | --- |
| SQL Fuse | Controlled runtime-path SQLite sandbox release proof | The v0.5 SQL Sandbox Execution Fuse line includes exactly one authorized allowlisted SELECT executed inside a temporary local SQLite sandbox, with rejected paths non-executing and mutation SQL non-executing. | `python3 cli.py demo-sql-fuse` |
| File Fuse | Constrained synthetic temp-directory proof | The v0.8 File Operation Safety Fuse line includes static inert cases, a non-executing benchmark, non-executing examples, and an explicitly constrained synthetic temp-directory proof with approved synthetic operations only. | `python3 cli.py demo-file-fuse` |
| HTTP Fuse | Static inert cases + non-executing benchmark + constrained local mock HTTP proof | The v0.9 HTTP / Network Request Safety Fuse line includes static inert cases, a non-executing benchmark, non-executing examples, and exactly one approved constrained local mock GET proof with no external network, DNS, credentials, or rejected request execution. | `python3 cli.py demo-http-fuse` |

## Proof Strength Classification

SQL currently has the strongest runtime-path evidence among the three lines:
one controlled SQLite sandbox release was executed under a fixed allowlisted SQL
statement and verified with deterministic synthetic data.

File has constrained synthetic local proof evidence: two approved synthetic file
operations were exercised inside a disposable temp-directory boundary while
rejected path proposals remained unopened, unresolved, and non-executing. This
does not claim arbitrary file operation support or production filesystem
safety.

HTTP has a staged local mock proof chain: static inert cases, a non-executing
benchmark, non-executing examples, and one constrained loopback-only mock GET
proof. This does not claim arbitrary HTTP support, external network access,
API-client capability, credential handling, browser/tool invocation, or
production HTTP safety.

## Shared DHMS Lifecycle Mapping Summary

All three proof lines map back to the same DHMS Execution Fuse Protocol shape:

1. Observable request or proposed action enters DHMS.
2. DHMS normalizes the proposal into a tool-call proposal or proof-line case.
3. DHMS assigns a safety decision with fail-closed defaults.
4. DHMS applies an execution gate before any side effect can occur.
5. Rejected, malformed, unsupported, or unsafe proposals terminate before
   execution.
6. Controlled-release candidates must pass an explicit constrained proof path.
7. Any approved constrained proof must produce observable evidence, verification
   results, teardown checks where applicable, and a traceable final verdict.

This alignment does not mean the proof lines have identical implementation
strength. It means their public evidence is now described through the same
DHMS lifecycle vocabulary.

## CLI Command Matrix

| Command | Proof line | Expected verdict | Evidence role |
| --- | --- | --- | --- |
| `python3 cli.py demo-sql-fuse` | SQL Fuse | `SQL_FUSE_DEMO_PASS` | Public wrapper for the SQL benchmark and linked v0.5 controlled SQLite sandbox proof line. |
| `python3 cli.py demo-file-fuse` | File Fuse | `DHMS_FILE_FUSE_DEMO_PASS` | Public wrapper for File Fuse static manifest, benchmark, examples, and constrained synthetic temp-directory proof. |
| `python3 cli.py demo-http-fuse` | HTTP Fuse | `DHMS_HTTP_FUSE_DEMO_PASS` | Public wrapper for HTTP Fuse non-executing benchmark and constrained local mock HTTP proof. |

## Frozen Non-Claims

DHMS v0.9.8 does not claim:

* production readiness
* real agent runtime interception
* arbitrary SQL support
* direct SQL execution
* mutation SQL execution
* arbitrary file operation support
* production filesystem safety
* arbitrary HTTP or network request support
* external network access
* credentialed DB, filesystem, or HTTP execution
* user data safety certification
* OpenClaw runtime integration
* DeepSeek/provider integration
* provider SDK integration
* agent SDK integration
* HTTP adapter support
* file adapter support
* shell adapter support
* MCP integration
* MCP replacement
* API client support
* browser/tool invocation support
* production-ready agent runtime
* universal agent safety
* industry-standard status

## Boundary Before v0.10

v0.9.8 is the boundary alignment step before v0.10. It freezes the public
evidence presentation for SQL, File, and HTTP without changing any runner,
manifest, example, schema, CLI behavior, source code, proof semantics, or
execution capability.

Before v0.10.0, the next step should be a v0.9.8 GitHub Release that marks the
three-line evidence package without publishing a new proof line or claiming
production readiness.

## Next Step

Recommended next milestone:

`v0.9.8 GitHub Release before v0.10.0`

Final document verdict:

`READY_FOR_V0_9_8_GITHUB_RELEASE_BEFORE_V0_10_0`
