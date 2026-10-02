---
name: onchain-contract-qualification
description: Qualify Solidity/OpenZeppelin behavior on the actual target chain with signed replay and adversarial invariants. Use for token callbacks, proxies, marketplaces or runtime compatibility claims.
metadata:
  origin: blockchain-nano documentation synthesis
  source_revision: "153bfd516ca2c04b80bef7d0b3754123a3fda812"
  runtime_verified: "false"
  license_review: pending
---

## Pi usage and scope

Use only tools declared in this session. Read `references/sources.md` before applying the workflow; resolve that path from this skill directory. Locate the user's target repository explicitly: it is not the skill directory and need not be Nano. Inspect its current code, configuration and authoritative specifications before transferring project-specific rules. Check prerequisites before commands; this package installs no runtime dependencies. No deployment, remote access, destructive cleanup, signing or real-fund operations are authorized by loading this skill.

# On-chain Contract Qualification

## Procedure

1. Inventory the exact dependency version and distinguish concrete contracts, abstract contracts, interfaces and libraries. Pin compiler, fork target, optimizer and source/bytecode hashes. A compilation catalogue is not a behavioral qualification.
2. Execute signed transactions on the actual target engine or node. A Forge/Hardhat test on its own engine is only generator/reference evidence; generate reproducible sequences and replay them on the target.
3. Compare receipts, all logs, roots and relevant balances/storage after every step. Replay on a second target instance to check determinism and reopen/audit persisted state; label same-engine replay as non-independent conformance.
4. Cover authorization, revoked/finite/infinite allowances, zero/boundary values, duplicate batch IDs, cumulative insufficiency, malformed ABI/calldata and invalid recipients. For receiver callbacks test success, wrong selector, revert after writes and reentrant transfer.
5. Require complete rollback of reverted writes/events while preserving protocol-required gas and nonce effects. Demonstrate a healthy transaction can execute after bounded exceptional or infinite-loop workloads.
6. Test cross-chain replay with distinct chain IDs for supported transaction types; rewriting a domain without resigning must not authorize the original account. Explicitly exclude same-chain-ID replay protection claims.
7. Define invariants for the actual economics: lending includes cash, claims, debt, interest and rounding; fee-bearing AMMs need not preserve an exact constant product. Test composed sale/payment/royalty/admin/upgrade paths rather than trusting primitives in isolation.
8. Use an independent client differential with identical transactions and pre-state for gas/semantics claims. Preserve discrepancies and minimize them; deterministic replay alone is not an independent implementation check.

## Deliverable and limits

Provide component-by-scenario coverage with pending items visible, fixtures/seeds and counterexamples. Deliberately vulnerable contracts stay isolated test fixtures. Primitive library tests do not audit a marketplace, AMM or bridge and never authorize real funds.
