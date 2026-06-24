# DHMS README Public Surface Polish v0.8.9

## Purpose

v0.8.9 is a documentation-only public surface polish milestone. It clarifies
the README structure, keeps SQL Fuse and File Fuse as the primary public
quickstarts, preserves historical Agent Harness reproduction commands as legacy
material, and simplifies the Trademark Notice without changing DHMS proof
semantics or adding runtime behavior.

Audited base commit:

`4217638acfe0003d9dc1d91572dd01eb3c54eff0`

## README Public Surface Issue

The upper README already presents the current DHMS AgentFuse public surface:
SQL Fuse and File Fuse quickstarts, the DHMS Execution Fuse Protocol narrative,
and current v0.8 evidence links.

The lower README still had an older generic `Quickstart` section that contained
Agent Harness reproduction commands. Those commands remain useful historical
evidence, but they should not compete with the current SQL Fuse and File Fuse
quickstarts as the public entry point.

The README also had a long Trademark Notice first sentence that listed many
protocol and tool-family names. The naming hierarchy remains documented in the
v0.8.8 naming document, but the README footer should be concise.

## Changes Made

The README public surface was polished as follows:

* Updated current milestone status to `v0.8.9 DHMS README Public Surface Polish`.
* Preserved the SQL Fuse quickstart command: `python3 cli.py demo-sql-fuse`.
* Preserved the File Fuse quickstart command: `python3 cli.py demo-file-fuse`.
* Renamed the lower generic `Quickstart` section to `Legacy Agent Harness Reproduction Commands`.
* Added a note that those commands are historical Agent Harness reproduction material.
* Renamed `Caveats` to `Historical Caveats and Boundaries`.
* Renamed `Documentation` to `Documentation and Evidence Archive`.
* Added this v0.8.9 document to the README archive and package index.
* Updated the roadmap to mark v0.8.9 as the current/completed public surface polish milestone.

## Trademark Notice Simplification

The README Trademark Notice first sentence was simplified to:

`DHMS, DHMS Engine, DHMS AgentFuse, and DHMS Agent Harness are project names and marks of Huaxinsheng Zhong.`

The existing permission and Apache-2.0 license boundary wording remains:

`Use of these names is permitted for accurate reference to this project, but does not imply endorsement, sponsorship, or affiliation unless explicitly authorized.`

`The Apache-2.0 license applies to the source code and documentation in this repository. It does not grant trademark rights.`

The longer v0.8.8 naming hierarchy remains documented in:

`docs/dhms_agentfuse_naming_and_trademark_alignment_v0_8_8.md`

## Preserved Boundaries

v0.8.9 preserves:

* SQL Fuse proof semantics.
* File Fuse proof semantics.
* v0.8.7 File Fuse CLI wrapper behavior.
* v0.8.8 naming hierarchy documentation.
* Historical Agent Harness reproduction commands.
* Architecture and evidence sections.
* Apache-2.0 License text.
* Trademark Notice permission and license boundary wording.

## Explicit Non-Claims

v0.8.9 preserves these explicit boundaries:

* no code changes
* no runtime behavior changes
* no new CLI behavior
* no new proof line
* no repo rename
* no branch rename
* no tag
* no GitHub Release
* no legal advice
* no formal trademark registration claim
* no production-readiness claim
* no MCP replacement claim
* no arbitrary SQL/file/tool execution claim

## Validation and Scans

The intended validation set for this polish milestone is:

```bash
python3 cli.py demo-sql-fuse
python3 cli.py demo-file-fuse
python3 validation/run_dhms_agentfuse_bench_sql_v0.py
python3 validation/run_dhms_agentfuse_bench_file_v0.py
git diff --check
git diff --cached --check
```

Targeted scans should check:

* no duplicate generic `## Quickstart` confusion remains.
* SQL Fuse and File Fuse quickstarts remain near the top of the README.
* the README Trademark Notice uses the simplified first sentence.
* no source code, validation runner, benchmark, manifest, example, or schema file changed.
* no repo or branch rename instruction was introduced.
* no tag or GitHub Release was created.
* no secret, API key, or private key pattern was introduced.

## Next Recommended Milestone

`v0.9.0 Next DHMS Proof Line Selection and Risk Review`

Final document verdict:

`READY_FOR_V0_9_0_NEXT_DHMS_PROOF_LINE_SELECTION_AND_RISK_REVIEW`
