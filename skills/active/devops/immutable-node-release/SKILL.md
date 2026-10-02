---
name: immutable-node-release
description: Prepare and promote immutable node images with binary/config provenance and signer-safe rollback. Use for Docker candidates, multi-architecture packaging or validator software updates.
metadata:
  origin: blockchain-nano documentation synthesis
  source_revision: "153bfd516ca2c04b80bef7d0b3754123a3fda812"
  runtime_verified: "false"
  license_review: pending
---

## Pi usage and scope

Use only tools declared in this session. Read `references/sources.md` before applying the workflow; resolve that path from this skill directory. Locate the user's target repository explicitly: it is not the skill directory and need not be Nano. Inspect its current code, configuration and authoritative specifications before transferring project-specific rules. Check prerequisites before commands; this package installs no runtime dependencies. No deployment, remote access, destructive cleanup, signing or real-fund operations are authorized by loading this skill.

# Immutable Node Release

## Procedure

1. Keep the running checkout/image untouched while preparing the candidate. Record full source revision, architecture, dependency/toolchain pins and hashes for every runtime executable, genesis, node configuration, profile and qualification artifact.
2. Distinguish a dependency image, mounted build volume and actual deployable runtime image. Package already qualified binaries without silently rebuilding or downloading different ones during promotion.
3. Bind candidate identity to an immutable digest and verify executable hashes from inside it. An image label or manually created source marker alone is not provenance. Integrity of an evidence file is not proof its contents pass qualification.
4. Probe using ephemeral no-network containers, no chain mounts, read-only filesystem and bounded resources. Check libraries, architecture, intended user and help/startup surface without enabling signing.
5. Review complete runtime/architecture/profile gates and licenses/notices separately from packaging. One architecture's build or a subset CI pass does not qualify the other architecture or a release bit-for-bit.
6. Before promotion, prove capacity to recover, stop the unique signer, verify terminal exit/OOM status and preserve external chain/signer commitments. Back up the coherent stopped state and audit it without mutating originals.
7. Promote only the reviewed immutable image and adapted network configuration. Prevent implicit build/pull; never remove data volumes, change genesis on an existing database or start duplicate signers.
8. Verify identities, duties and execution-linked common finality after startup. Keep the previous software recoverable until acceptance, without interpreting RPC availability as success.
9. A software rollback must keep the newest signer reservations/witnesses. Prove the old binary accepts the current data format before restarting; otherwise stop signing and repair forward. Never revert the whole backup to erase duties emitted by the candidate.

## Deliverable

Provide candidate manifest, preflight verdict, qualification gates, promotion steps and an explicitly proven rollback target. Do not deploy, publish images, contact a VPS or access validator keys unless authorized.
