---
name: durable-monitor-alerting
description: Design read-only stateful monitoring with sticky safety faults and a durable idempotent alert outbox. Use for finality monitoring, retry queues or crash-safe notification delivery.
metadata:
  origin: blockchain-nano documentation synthesis
  source_revision: "153bfd516ca2c04b80bef7d0b3754123a3fda812"
  runtime_verified: "false"
  license_review: pending
---

## Pi usage and scope

Use only tools declared in this session. Read `references/sources.md` before applying the workflow; resolve that path from this skill directory. Locate the user's target repository explicitly: it is not the skill directory and need not be Nano. Inspect its current code, configuration and authoritative specifications before transferring project-specific rules. Check prerequisites before commands; this package installs no runtime dependencies. No deployment, remote access, destructive cleanup, signing or real-fund operations are authorized by loading this skill.

# Durable Monitor Alerting

## Procedure

1. Load expected identity from independently reviewed local configuration, never learn it from the remote endpoint. Bound timeouts, response bytes, history and pending messages; use private transports and private state files.
2. Capture checkpoints by immutable state identity. Validate chain/genesis/profile, peers, progression, conflicts and regressions. A first healthy observation is only a baseline, not evidence of progress; missing observations create no progress.
3. Persist safety faults as sticky state. Later normal samples must not clear conflicts, regressions or lost history automatically. Reject backward local clocks and incompatible/corrupt state instead of silently resetting them.
4. Prevent simultaneous monitor writers. After a crash, remove a stale lock only after verifying the owner is gone; never erase history or queues to make the monitor green.
5. Commit a pending alert in the same durable transaction as monitor state before handing it to a delivery queue. Drain pending handoff before new observations and clear it only after durable enqueue; keep outbox state on local failure.
6. Use exclusive temporary writes, file fsync, atomic replacement and directory fsync for the file-based design. Test the actual guarantees of the target filesystem and distinguish process-crash from power-loss claims.
7. Persist queue entries before POST, retain them on error and remove them only after the agreed acknowledgement plus durable local commit. Preserve order and reject queue overflow without deleting old alerts. An explicit drain must not invent observations.
8. Use stable event IDs and the same ID in body/idempotency key. Require durable receiver deduplication: a crash after remote acceptance but before local commit can repeat the POST. A 2xx does not prove a human read the alert.
9. Test monitor failure, wrong identity, stale/conflicting checkpoints, full queues, receiver failure, crash between every handoff/ack commit and restart replay. Qualify synthetic endpoints, live daemons, receiver delivery and operator scheduling as separate gates.

## Deliverable

Describe exit-code semantics for healthy, alert/delivery failure and local/configuration failure; define operator actions without autonomous restart, signing or safety-state reset. Do not provision or contact an external alert receiver without approval.
