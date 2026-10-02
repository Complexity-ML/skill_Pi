---
name: distributed-finality-qualification
description: Design bounded multi-node finality and partition campaigns with weighted quorum and execution-linked checkpoints. Use for consensus safety, WAN recovery and validator topology tests.
metadata:
  origin: blockchain-nano documentation synthesis
  source_revision: "153bfd516ca2c04b80bef7d0b3754123a3fda812"
  runtime_verified: "false"
  license_review: pending
---

## Pi usage and scope

Use only tools declared in this session. Read `references/sources.md` before applying the workflow; resolve that path from this skill directory. Locate the user's target repository explicitly: it is not the skill directory and need not be Nano. Inspect its current code, configuration and authoritative specifications before transferring project-specific rules. Check prerequisites before commands; this package installs no runtime dependencies. No deployment, remote access, destructive cleanup, signing or real-fund operations are authorized by loading this skill.

# Distributed Finality Qualification

## Procedure

1. Declare the active consensus profile, validator weights, fork schedule, independently approved genesis and immutable node binaries. Map processes to physical hosts and compromise/failure domains; three processes on two hosts are not three independent domains.
2. Generate fresh synthetic fixtures, allocate disjoint signer keys and refuse reused output directories. Never fund published fixture keys or expose signing/RPC endpoints publicly.
3. Establish actual peer connections and common finalized checkpoints before fault injection. Capture immutable state/block roots rather than mixing changing head reads.
4. Check agreement on every required node, monotonic finalized epochs/heights, no conflicting root at the same finalized position and linkage to the corresponding execution block. For the Nano campaign pattern require three consecutive common advances, not merely a reachable RPC or moving head.
5. Define partition topology and lost vote weight, not just process count. For strict weighted BFT test the exact integer condition 3 * signed_weight > 2 * total_weight. Do not transplant this formula blindly to another protocol. Treat long-term inactivity/weight changes separately from short-term quorum loss.
6. Inject only authorized, isolated and bounded failures. Keep recovery observations private and restore connectivity even after captured orchestration failures. Record limits of cleanup if the orchestrator or transport dies.
7. Preserve the original recovery deadline. Later convergence is useful diagnostic evidence but does not convert a missed deadline into a pass. Missing observations receive no safety or liveness credit.
8. Verify terminal signer/process health, exit status, OOM state and durable shutdown receipts; archive traces, identities, latencies and failure logs.

## Deliverable and limits

Report safety, liveness and recovery separately, including participating weights and independent host count. Unit tests of an orchestrator do not qualify a live network. BLS is a signature primitive, not a finality algorithm; a quorum certificate alone does not prove lock-rule correctness.
