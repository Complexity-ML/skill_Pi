---
name: async-network-admission
description: Audit asynchronous network framing, deadlines, quotas and exactly-once callback completion. Use for P2P adapters, RPC streams, late callbacks or overload isolation.
metadata:
  origin: blockchain-nano documentation synthesis
  source_revision: "153bfd516ca2c04b80bef7d0b3754123a3fda812"
  runtime_verified: "false"
  license_review: pending
---

## Pi usage and scope

Use only tools declared in this session. Read `references/sources.md` before applying the workflow; resolve that path from this skill directory. Locate the user's target repository explicitly: it is not the skill directory and need not be Nano. Inspect its current code, configuration and authoritative specifications before transferring project-specific rules. Check prerequisites before commands; this package installs no runtime dependencies. No deployment, remote access, destructive cleanup, signing or real-fund operations are authorized by loading this skill.

# Async Network Admission

## Procedure

1. Trace connection, identity handshake, stream opening, framing, parser, application handler and cancellation. Validate peer chain/genesis against local reviewed identity before application exchange.
2. Bound message bytes, nesting, active streams, global/per-peer work, queue size and identity-table growth. Separate protocol limits from local operational budgets. Frame progressively and avoid reparsing the full partial JSON on every chunk.
3. Include stream establishment in the exchange deadline. Reset a stream that arrives after expiration, retain cancellation state and prevent late completions from delivering a second result.
4. Remove a callback explicitly from its storage before invoking it. Moving a std::function alone does not establish a portable consumed-state invariant. Exercise reentrancy, cancellation and delayed errors.
5. Hold admission permits for the whole asynchronous operation, not just the dispatch call. Reject overload explicitly rather than silently building an unbounded queue; release permits on every terminal path.
6. Use real reader/writer classes with controllable test streams. Cover timeout → reset → deferred cancellation error, late-open streams, partial/malformed frames, identity mismatch and quota exhaustion. Assert one user completion and no permit leak.
7. For sustained tests, bound duration and resource use. Pre-sign workload if measuring admission, reuse generator connections and distinguish client port exhaustion or transport failure from a valid application rejection.

## Deliverable and limits

List each budget, ownership and lifetime invariant with a negative test. Application stream quotas do not protect TCP handshakes, crypto negotiation, bandwidth or Sybil identities. Cancellation of application waiting does not prove immediate cleanup inside a transport library. Local load results are not distributed finalized throughput.
