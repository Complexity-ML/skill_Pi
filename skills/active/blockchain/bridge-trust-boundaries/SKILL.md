---
name: bridge-trust-boundaries
description: Review bridge proof domains, signer compromise assumptions and reserve invariants before real funds. Use for cross-chain mint/burn, relayers, withdrawals or bridge security requirements.
metadata:
  origin: blockchain-nano documentation synthesis
  source_revision: "153bfd516ca2c04b80bef7d0b3754123a3fda812"
  runtime_verified: "false"
  license_review: pending
---

## Pi usage and scope

Use only tools declared in this session. Read `references/sources.md` before applying the workflow; resolve that path from this skill directory. Locate the user's target repository explicitly: it is not the skill directory and need not be Nano. Inspect its current code, configuration and authoritative specifications before transferring project-specific rules. Check prerequisites before commands; this package installs no runtime dependencies. No deployment, remote access, destructive cleanup, signing or real-fund operations are authorized by loading this skill.

# Bridge Trust Boundaries

## Procedure

1. Define source/destination chains, asset and contracts, finality requirement, proof verification and responsibilities of contracts, relayers, signers, administrators and upgrade controllers.
2. Map signing quorum to real compromise domains. Several keys/containers on one operator's VPS do not imply independence. BLS or a larger threshold does not distinguish an honest quorum from a fully compromised quorum.
3. Bind each authorized action to chain pair, contract, asset, amount, recipient and one-time consumed identifier. Verify finalized deposits/events before mint or release; reject replay across chains, forks and contracts.
4. Enumerate mint, withdrawal, pause, admin, upgrade and revocation privileges. Test stale delegations and revoked signers after the documented activation boundary; expose every bypass of the announced proof/quorum model.
5. Reconcile reserves, circulating backed supply and pending withdrawals under the chosen accounting model. Do not credit an application pool with an asset described as guaranteed before backing is qualified.
6. Define approved loss controls: caps, delays, alerts, bridge-specific halt and revocation/rotation. Document their governance and effects on legitimate withdrawals. They limit loss; they do not constitute deposit proofs or justify blanket L1 censorship.
7. Test fabricated deposits, compromised relayers, stolen sub-quorum keys, fully compromised quorum, admin compromise, repeated deposits/withdrawals, pre-finality reorgs, altered amount/asset/recipient, relayer restart and complete return to the source asset.

## Deliverable

Return a threat-model table with test evidence, open requirements, loss limits and explicit trust assumptions. A requirements document is not implementation evidence; EVM or L1 consensus qualification is not reserve/bridge security. Use isolated synthetic assets, obtain independent review and explicit authorization before real funds.
