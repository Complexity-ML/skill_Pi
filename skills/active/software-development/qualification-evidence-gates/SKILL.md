---
name: qualification-evidence-gates
description: Audit test coverage and qualification claims with exact inventories, terminal results and artifact provenance. Use before declaring a port, regression suite or release complete.
metadata:
  origin: blockchain-nano documentation synthesis
  source_revision: "153bfd516ca2c04b80bef7d0b3754123a3fda812"
  runtime_verified: "false"
  license_review: pending
---

## Pi usage and scope

Use only tools declared in this session. Read `references/sources.md` before applying the workflow; resolve that path from this skill directory. Locate the user's target repository explicitly: it is not the skill directory and need not be Nano. Inspect its current code, configuration and authoritative specifications before transferring project-specific rules. Check prerequisites before commands; this package installs no runtime dependencies. No deployment, remote access, destructive cleanup, signing or real-fund operations are authorized by loading this skill.

# Qualification Evidence Gates

## Procedure

1. Define the claim and its exclusions before running anything: component, revision, architecture, profile, fixture versions, workload and required scenarios.
2. Capture the configured test registry and compare exact names against the expected inventory. Reject missing or duplicate registrations, absent executables, disabled tests, skip properties and unbounded waits. A subset must be labeled partial.
3. Record selected, executed, passed, failed, skipped, unsupported and unexecuted cases separately. Zero executed cases is not success. An interrupted run, timeout, truncated report or running CI job has no successful terminal verdict.
4. Bind results to full source revisions, executable hashes, dependency pins, configuration hashes, exact commands and raw logs. A marker or image label alone does not prove source-to-binary provenance.
5. Preserve failures. For each incident link original case/log → cause → exact correction → regression test → replay of the same case → remaining limits. Use open, correction-to-verify, resolved-with-scope or reopened states.
6. Test the evidence validator itself with empty reports, altered hashes, duplicates, wrong case/fork IDs, omitted tests, false green summaries and truncated logs. Propagate command failures through logging pipelines.
7. Report separate gates for local behavior, independent conformance, distributed operation, durability, portability and release reproducibility. Do not turn a successful smoke/CI subset into production approval.

## Deliverable

Produce a claim/evidence/limits table and incident ledger. State the actual terminal result and the next unmet gate. File or method counts demonstrate inventory, not behavioral parity.
