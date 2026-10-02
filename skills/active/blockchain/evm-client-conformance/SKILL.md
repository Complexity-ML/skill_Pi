---
name: evm-client-conformance
description: Qualify an EVM implementation using pinned official fixtures and independent client differentials. Use for hard-fork support, gas/state discrepancies or EEST adapters.
metadata:
  origin: blockchain-nano documentation synthesis
  source_revision: "153bfd516ca2c04b80bef7d0b3754123a3fda812"
  runtime_verified: "false"
  license_review: pending
---

## Pi usage and scope

Use only tools declared in this session. Read `references/sources.md` before applying the workflow; resolve that path from this skill directory. Locate the user's target repository explicitly: it is not the skill directory and need not be Nano. Inspect its current code, configuration and authoritative specifications before transferring project-specific rules. Check prerequisites before commands; this package installs no runtime dependencies. No deployment, remote access, destructive cleanup, signing or real-fund operations are authorized by loading this skill.

# EVM Client Conformance

## Procedure

1. Fix the fork, activation rules, chain identity, genesis/pre-state, compiler target and fixture/client versions. Check the authoritative specification before deciding which engine is wrong.
2. Pin the official corpus and verify archive/file checksums before extraction. Inventory supported fixture formats and forks; do not advertise unimplemented Engine API or transaction formats as covered.
3. Trace the adapter to the real engine under test. Never substitute a reference interpreter, Anvil or Geth for the target and then claim target conformance.
4. Execute exact case IDs and preserve command, raw engine output, fixture identity and binary hash. Missing cases, wrong forks, unsupported formats, timeouts and zero executions must not silently pass.
5. Add adapter negative controls: a known-good official case, deliberately false state root, absent case ID and unsupported fork. Mutate a receipt or rejection reason to ensure the comparator detects it.
6. For differentials, feed identical signed bytes sequentially from equivalent pre-states. Compare validation outcome, transaction identity, receipts, logs, gas, state/storage and roots available from each engine.
7. Distinguish admission from inclusion and execution: returning a transaction hash then excluding it is not equivalent to rejecting admission. Distinguish REVERT from exceptional gas exhaustion and absent accounts from empty accounts.
8. Preserve the original mismatch, minimize it, add a regression and replay on the corrected binary. Do not weaken a protocol rule solely to match one reference client's policy.

## Deliverable and limits

Report counts by fork/format with failures, unsupported and unexecuted cases explicit. State tests do not prove full header/consensus validation; EVM conformance does not prove RPC, P2P, finality, disk recovery or production readiness. Compiler success is not execution conformance.
