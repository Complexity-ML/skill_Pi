---
name: durable-validator-recovery
description: Implement or audit reserve-before-sign journals and fail-closed validator backup/recovery. Use for anti-double-signing, rollback protection, signer migration or coupled consensus/execution stores.
metadata:
  origin: blockchain-nano documentation synthesis
  source_revision: "153bfd516ca2c04b80bef7d0b3754123a3fda812"
  runtime_verified: "false"
  license_review: pending
---

## Pi usage and scope

Use only tools declared in this session. Read `references/sources.md` before applying the workflow; resolve that path from this skill directory. Locate the user's target repository explicitly: it is not the skill directory and need not be Nano. Inspect its current code, configuration and authoritative specifications before transferring project-specific rules. Check prerequisites before commands; this package installs no runtime dependencies. No deployment, remote access, destructive cleanup, signing or real-fund operations are authorized by loading this skill.

# Durable Validator Recovery

## Procedure

1. Map chain/genesis identity, validator key identity, fork domains, journal, coupled consensus/execution checkpoint, witness and external freshness commitments. Keep secrets out of logs, archives intended for sharing and manifests.
2. Validate the actual duty, state, branch, fork and execution before journal use. A low-level signing primitive is not authorization to perform a validator duty.
3. Reserve the signing root durably before invoking the secret-key provider. Keep the reservation after backend failure or invalid signature; verify returned signatures before publication. Fail storage errors closed until explicit reopening.
4. Define replay/conflict semantics and serialize concurrent instances using expected sequence/digest checks. Fork changes must not create a loophole for a conflicting vote at the same protected position.
5. For witness recovery, persist the intention before the primary publication. Accept only the exact successor or completion from the exact predecessor after identity/digest checks. Missing, contradictory, stale or wrong-identity evidence must never trigger fallback to bootstrap.
6. Store independently approved freshness commitments outside the suspect backup. A primary and witness restored together cannot establish independent anti-rollback evidence. An exact commitment is not a minimum sequence.
7. Stop every user of the key before coherent backup or migration. Preserve chain, witnesses, all signer journals/witnesses, identity and reviewed configuration; hash and audit stopped copies. Do not run source and restored signers simultaneously.
8. For interchange export, retire the source durably before returning history. Validate imports completely, preserve unknown roots conservatively and document whether atomicity is per key or across keys. Never reset protection to make a migration work.
9. Test failures before/after reservation, witness and primary commits, callback errors, stale instances, concurrent export, missing witness, wrong commitment and old/incomplete backups. Separate SIGKILL tests from power-loss/storage-fault claims.

## Recovery acceptance

Require preserved identities and finalized commitments, safe duty resumption and execution-linked common finality. Do not restore older signer journals during software rollback: retain the newest reservations and prove format compatibility or keep signing stopped.
