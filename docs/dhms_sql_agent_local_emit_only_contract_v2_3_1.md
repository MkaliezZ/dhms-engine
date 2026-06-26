# DHMS SQL Agent Local Emit-Only Contract v2.3.1

## Metadata

* Milestone: `v2.3.1 SQL Agent Local Emit-Only Contract`
* Repository branch: `agent-harness-v1`
* Prior milestone: `v2.3.0 SQL Agent Local Emit-Only Test Planning`
* Next recommended milestone: `v2.3.2 SQL Agent Static Proposal Fixtures`

## Current Status

v2.3.1 is docs-only and prose-contract-only. It converts v2.3.0 planning into a
contract for the `SQL Proposal Agent Candidate` without adding implementation,
schema, fixtures, validation, or runtime behavior.

## Scope

The contract subject is a future local emit-only proposal boundary:

Natural language request -> inert SQL proposal envelope -> DHMS boundary
evaluation

DHMS remains the boundary evaluator before execution. The future candidate may
only emit inert proposal envelopes.

## Non-Scope

v2.3.1 does not implement a SQL agent, add code, add schema, add JSON examples,
add fixtures, add parser, add runner, add validator, add CLI, add quickstart,
add adapter, add hook, add execution path, execute SQL, connect to a database,
integrate with a database, inspect schemas, access real schemas, read real data,
mutate databases, use sqlite/postgres/mysql clients, use ORM, integrate
LangChain, integrate LlamaIndex, use SQLDatabaseToolkit, add SQL agent runtime,
use subprocesses, use shell, execute commands, mutate files, access network,
read env values, access credentials, access user data, call SDK/model/runtime
surfaces, integrate KerniQ, add a KerniQ runtime call, integrate E2B, add E2B
handoff, create a release, or create a tag.

## Relationship to v2.3.0

v2.3.0 selected the SQL Agent Local Emit-Only planning line. v2.3.1 preserves
that planning boundary and turns it into prose contract language for a future
`SQL Proposal Agent Candidate`.

## Contract Subject

`SQL Proposal Agent Candidate` is only a future emit-only candidate for inert
proposal metadata. It is not LangChain SQL Agent, LlamaIndex SQL Agent, a real
database agent, DB execution agent, SQL runner, SQL parser, SQL validator, ORM
adapter, or runtime integration.

## Envelope Field Contract, Prose-Only

Future envelope fields may include:

* `proposal_id`: stable identifier for the inert proposal.
* `agent_profile`: declared emit-only candidate profile.
* `natural_language_request`: synthetic or local request summary.
* `sql_dialect`: declared dialect label only.
* `sql_candidate`: inert proposal text, not executable input.
* `sql_operation_type`: declared operation class.
* `declared_tables`: declared or synthetic table names only.
* `declared_columns`: declared or synthetic column names only.
* `declared_side_effects`: declared side-effect expectations.
* `read_write_class`: declared read/write class.
* `risk_markers`: declared risk taxonomy markers.
* `where_clause_present`: declared boolean-like metadata.
* `limit_clause_present`: declared boolean-like metadata.
* `credential_scope`: credential scope declaration.
* `user_data_scope`: user-data scope declaration.
* `db_connection_scope`: database connection scope declaration.
* `schema_source`: synthetic or declared-only schema source label.
* `runtime_target`: runtime target declaration.
* `dry_run`: dry-run declaration.
* `expected_dhms_decision`: expected DHMS decision.
* `expected_fail_closed_reason`: expected fail-closed reason when applicable.
* `non_execution_assertions`: assertions denying execution and access.

These are prose-only contract fields. v2.3.1 does not create schema, JSON
examples, fixtures, parser behavior, runner behavior, validator behavior, or
runtime behavior.

## Required Inert Boundary Values

Future fixtures must preserve these inert boundary values:

* `dry_run` must be true.
* `db_connection_scope` must be empty.
* `credential_scope` must be empty.
* `user_data_scope` must be empty.
* `schema_source` must be synthetic or declared-only.
* `runtime_target` must be `no-runtime`.
* `sql_candidate` must be inert metadata, not executable input.
* `declared_tables` and `declared_columns` must be declared or synthetic only.

## SQL Risk Taxonomy Contract, Prose-Only

Future risk category names may include:

* read-only query proposal
* write or mutation proposal
* destructive DDL proposal
* missing WHERE mutation proposal
* broad table scan proposal
* sensitive-data query proposal
* cross-database access proposal
* credential-seeking proposal
* schema-introspection proposal

These are category names only. v2.3.1 does not include SQL statements.

## DHMS Decision Boundary

The candidate does not decide release, block, hold, or fail-closed outcomes. It
may only emit inert proposal metadata for later DHMS boundary evaluation. DHMS
remains the policy owner and boundary evaluator before any execution boundary.

## Fail-Closed Rules

Future SQL proposals must fail closed if:

* `dry_run` is false or missing.
* `db_connection_scope` is non-empty.
* `credential_scope` is non-empty.
* `user_data_scope` is non-empty.
* `runtime_target` is not `no-runtime`.
* `schema_source` claims real schema access.
* proposal metadata requests DB connection.
* proposal metadata requests SQL execution.
* proposal metadata requests schema introspection.
* proposal metadata requests real data access.
* proposal metadata requests database mutation without explicit safe boundary.
* proposal metadata contains credential-seeking intent.
* proposal metadata claims LangChain, LlamaIndex, or SQLDatabaseToolkit runtime.
* proposal metadata claims KerniQ runtime.
* proposal metadata claims E2B handoff.

## DB Boundary

v2.3.1 does not connect to any database, execute SQL, inspect schemas, access
real schemas, read real data, mutate databases, use sqlite/postgres/mysql
clients, use ORM, access credentials, access user data, or authorize database
runtime behavior.

## LangChain / LlamaIndex Boundary

v2.3.1 does not use LangChain, LlamaIndex, SQLDatabaseToolkit, SQL agent
runtime, provider SDKs, agent SDKs, or runtime adapters. Any future discussion
of third-party frameworks requires separate planning and approval.

## KerniQ Boundary

KerniQ remains deferred to a later candidate line. v2.3.1 does not install
KerniQ, run KerniQ, invoke KerniQ, integrate KerniQ, or add a KerniQ runtime
call.

## E2B Boundary

E2B remains later handoff-boundary planning. v2.3.1 does not call E2B, add E2B
integration, create an E2B sandbox, or add an E2B handoff.

## Later Milestone Boundary

The next recommended milestone is `v2.3.2 SQL Agent Static Proposal Fixtures`.

v2.3.2 may add static inert fixtures only. v2.3.2 must not add code, schema,
parser, runner, validator, CLI, SQL execution, DB connection, LangChain,
LlamaIndex, KerniQ, E2B, or runtime behavior.

## Public Claims

v2.3.1 may claim only that DHMS has a prose-only emit-only contract for the
future `SQL Proposal Agent Candidate`.

## Public Non-Claims

v2.3.1 does not claim:

* SQL agent implementation
* LangChain SQL Agent support
* LlamaIndex SQL Agent support
* real database agent support
* DB execution agent support
* SQL runner support
* SQL parser support
* SQL validator support
* ORM adapter support
* runtime integration
* SQL execution
* DB connection
* database integration
* schema introspection
* real schema access
* real data access
* database mutation
* sqlite/postgres/mysql client support
* credential access
* user-data access
* KerniQ integration
* KerniQ runtime call
* E2B integration
* E2B handoff
* production readiness
* implementation readiness
* runtime behavior

## Acceptance Checklist

* docs-only milestone
* prose-contract-only milestone
* no SQL examples added
* no code added
* no schema added
* no JSON examples added
* no fixtures added
* no parser added
* no runner added
* no validator added
* no CLI added
* no quickstart added
* no adapter added
* no hook added
* no execution path added
* no SQL execution added
* no DB connection added
* no database integration added
* no schema introspection added
* no real data access added
* no database mutation added
* no sqlite/postgres/mysql client added
* no ORM added
* no LangChain integration added
* no LlamaIndex integration added
* no KerniQ integration added
* no E2B integration added
* final verdict set correctly

## Final Verdict

`READY_FOR_V2_3_2_SQL_AGENT_STATIC_PROPOSAL_FIXTURES`
