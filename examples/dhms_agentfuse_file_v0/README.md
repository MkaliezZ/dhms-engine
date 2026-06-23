# DHMS File Fuse Non-Executing Examples

These examples are non-executing demonstrations for the DHMS File Operation
Safety Fuse proof line.

They show representative file operation proposals, expected safety decisions,
gate states, and trace fields. Requested path templates are inert strings only.
The examples do not open, resolve, list, write, append, delete, inspect,
normalize, or validate requested path templates as real filesystem paths.

This directory does not implement file policy, does not add file operation
capability, and does not add a file adapter. It prepares future v0.8.4
discussion, but it does not authorize a constrained temp-directory proof or any
file operation implementation.

Run the smoke validation:

```bash
python3 validation/run_dhms_file_fuse_non_executing_examples_smoke.py
```

Expected verdict:

`DHMS_FILE_FUSE_NON_EXECUTING_EXAMPLES_PASS`
