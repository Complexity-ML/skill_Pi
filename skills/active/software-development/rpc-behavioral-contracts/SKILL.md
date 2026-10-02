---
name: rpc-behavioral-contracts
description: Audit JSON-RPC envelopes, batch side effects and canonical-head fee caches without mistaking route counts for compatibility. Use for RPC ports, parameter validation or fee-estimator reorg bugs.
metadata:
  origin: blockchain-nano documentation synthesis
  source_revision: "153bfd516ca2c04b80bef7d0b3754123a3fda812"
  runtime_verified: "false"
  license_review: pending
---

## Pi usage and scope

Use only tools declared in this session. Read `references/sources.md` before applying the workflow; resolve that path from this skill directory. Locate the user's target repository explicitly: it is not the skill directory and need not be Nano. Inspect its current code, configuration and authoritative specifications before transferring project-specific rules. Check prerequisites before commands; this package installs no runtime dependencies. No deployment, remote access, destructive cleanup, signing or real-fund operations are authorized by loading this skill.

# RPC Behavioral Contracts

## Procedure

1. Fix the intended standard and compatibility policy. Build a per-method matrix of parameter shapes, boundary values, errors, results and side effects. Preserve intentional corrections to a legacy implementation rather than claiming exact parity.
2. Test identifiers independently: absent/null notification policy, strings, exact wide integers and rejected booleans/fractions/structures. Test omitted parameters separately from invalid non-array parameters for a positional-only API.
3. Cover empty batches, invalid elements among valid requests, unknown methods, execution errors and notification-only responses. Verify actual state changes and ordering; do not assume batch atomicity or universal sequential execution.
4. Keep internal exceptions generic at the public boundary; do not leak traceback, secrets or implementation details. Test the concrete HTTP status/body behavior for notifications and transport errors.
5. For historical fee data, validate block range, genesis truncation, percentiles, empty-block rules and actual gas-weighted tips. Keep local recommendation policy distinct from protocol base-fee calculation and user-signed fee fields.
6. Capture canonical head hash once, traverse by hash and key caches by immutable block identity. Equal-height reorgs must invalidate head-derived estimates. Recheck head stability before publishing and never publish partial results after missing data or a race.
7. Bound history, samples and cache retention. Invalid configuration reloads preserve the last valid policy; valid reloads invalidate dependent caches. Preserve explicit wallet prices and saturate numeric arithmetic under the declared domain.
8. Test a healthy call after malformed/error requests on reusable connections. Classify explicit application rejection separately from generator exhaustion, transport failure and timeout; do not count those as expected refusal.

## Deliverable and limits

Provide method coverage, intentional divergences, regression tests and cache lifetime guarantees. Method-name counts, one client happy path or admission latency do not prove full RPC compatibility, finalization throughput or future transaction inclusion.
