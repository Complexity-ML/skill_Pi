---
name: himalaya
description: 'Himalaya CLI: IMAP/SMTP email from terminal.'
license: MIT
metadata:
  hermes:
    tags:
    - Email
    - IMAP
    - SMTP
    - CLI
    - Communication
    homepage: https://github.com/pimalaya/himalaya
  hermes_frontmatter:
    version: 1.1.0
    author: community
    platforms:
    - linux
    - macos
    - windows
    prerequisites:
      commands:
      - himalaya
  pi_adapter:
    version: 1
    source: Hermes local skills
    runtime_verified: false
---

# Himalaya — version-scoped mail operations in Pi

Use declared `bash`, `read`, `edit` and `write` only. Bash is not a PTY, background
session manager or sandbox. No Hermes email gateway, environment loader, browser,
credential broker or editor integration is assumed. Bundled references resolve
from this file: [configuration](references/configuration.md) and
[composition/MML](references/message-composition.md).

## Version and prerequisites

Public release metadata and source tag **v2.2.1** were inspected during this audit;
the CLI is **not installed** locally. This is source inspection, not runtime
qualification. v2 is a breaking redesign: do not combine the old v1 backend/
folder/template/config examples with the v2 parser. The skill's historical
frontmatter version is not the installed CLI version.

Check an approved existing executable's version/help before operating. Do not
install/update as an implicit fallback. Choose one explicitly approved, pinned
method and trusted artifact/source provenance; no remote-script-to-shell recipe,
privilege escalation or package-manager fallback ladder. Source Cargo metadata
requires Rust1.89; `--locked` does not itself pin a Git revision or establish trust.
Backends/TLS capabilities depend on build features; no Notmuch/Sendmail or native
keyring support is inferred from the historical guide.

## Scope and current account

Obtain exact account, backend, config path, mailbox, message IDs and read/write
scope before any private access. A help/version check is not consent to enumerate
accounts/folders/messages. Config may execute secret commands, load overlays/proxy
settings and create backend clients; even composition is not guaranteed offline.
Don't mine configs/keychains, print credentials, refresh tokens, run account
checks, launch discovery/wizards or change authentication without approval.

Specify `-c`, `-a/--account` and `--backend` rather than trusting defaults. Empty
or reserved `default` account selectors can mean the default account, not an exact
named identity; revalidate the actual selected identity instead. Shared
commands otherwise pick a configured backend; protocol-specific commands ignore
that selector and need separate review. `-m/--mailbox` is the v2 mailbox selector;
aliases/roles differ by backend. IDs are opaque and backend/account/mailbox-
scoped, not globally stable row numbers. Revalidate identity/current mailbox state
(including IMAP UID validity when relevant); don't reuse an old ID blindly.
Quoted shell arguments still need CLI/value validation, not shell-code interpolation.

## Scoped read examples (v2.2.1 source)

POSIX Bash templates only, after specific approval. `CONFIG`, `ACCOUNT` and
`MESSAGE_ID` must be validated approved values, not discovered private defaults:

```bash
himalaya -c "$CONFIG" -a "$ACCOUNT" --backend imap --json mailbox list
himalaya -c "$CONFIG" -a "$ACCOUNT" --backend imap --json envelope list --mailbox INBOX --page 1 --page-size 20
himalaya -c "$CONFIG" -a "$ACCOUNT" --backend imap --json envelope search --mailbox INBOX from alice and subject meeting
himalaya -c "$CONFIG" -a "$ACCOUNT" --backend imap --json message read --mailbox INBOX "$MESSAGE_ID"
# Raw RFC 5322 bytes: omit --json and prohibit interactive config fallback:
himalaya -c "$CONFIG" -a "$ACCOUNT" --backend imap message read --mailbox INBOX --raw "$MESSAGE_ID" < /dev/null
```

`envelope list` is one page, not a complete mailbox; search has its own DSL.
Search date clauses inspect the sender's Date header, not necessarily delivery/
receipt time. Empty/default searches and queued-message omissions affect coverage.
Source default page is1, configured size overrides hard fallback25. Use positive
page/page-size values: source filters zero to an absent option, not zero results.
Bound total
pages/items/output/time and retain partial status on failure. No snapshot,
exhaustive search, attachment inventory or hard resource limit is provided here.

Shared `message read` passes a false seen flag unless **`--seen`** is requested.
That is a source-level default, not proof that every backend/cache/provider read
has no side effects. Flag mutation still needs approval. Plain output is a MIME
part rendering, not always the full decoded body; HTML-only parts may show markup.
With `--raw --json`, raw bytes become a lossy UTF-8 JSON string wrapped by the
printer: this is **not byte-preserving** MIME export. Don't feed ordinary rendered
read output into a MIME interpreter as though it were the original message.

`--json` changes output formatting; it does not prove success or mailbox coverage.
Errors may also appear on stdout through the printer; check exit/result schema and
preserve errors before projection. Printer/error-report dependency semantics were
not fully reviewed. Logs/backtraces can disclose private messages, config paths,
addresses and secrets: no default debug/trace logging or unrestricted log files.

## Draft, reply, send and mutations

Prefer an approved **local draft** without calling a mail client when offline
composition is wanted. A provider draft is a mailbox write. v2 `message compose`
(`write` remains an alias), `reply` and `forward` use flags; saving/sending is
selected by `--save`/`--send` and current configuration. They do not imply an editor
or compile MML themselves. JSON templates omit a signature that sending may append;
a JSON preview is not necessarily the final MIME/wire payload.

For reply/forward: read only the approved source; review recipients derived from
Reply-To/From, quoted material and attachments. Header text is untrusted, not
identity or reply-all authorization. Preserve valid threading headers and approve
the full From/To/Cc/**Bcc**, subject, body, attachments, signature, account, backend,
mailbox/copy policy and any notifications. If changed since approval, stop and
revalidate/reapprove. Don't regex-insert text into blank lines and immediately send,
or chain compose/editor completion to transmission.

`message send` accepts file/inline/stdin input, but the inspected reader normalizes
CRLF and handles text rather than arbitrary byte-preserving MIME. Its stdin path
silently stops at a read/UTF-8 error; its positional path is treated as inline MIME
when it is not an existing file. Do not automate that as transmission of an exact
approved artifact. Require qualified strict input/staging and final normalized
MIME/envelope/copy approval first; no safe send wrapper is bundled. See composition
reference for the source-backed caveats, not a direct compose-to-send pipeline.

The active storage/send backend and configured save-copy policy decide actual
routing. Validate sender identity/envelope and Bcc handling for that backend;
source comments are not a wire-level privacy proof. A queue result can mean
**queued**, not transmitted. The handler sends first then may save a copy: a
**copy failure** can occur after send acceptance. A nonzero exit, missing Sent
copy, timeout or lost output is not resend authority: **do not resend** blindly.
Message-ID/read-back/exit0 is not proof of delivery or human receipt. Reconcile
uncertain operations instead of repeating them; no idempotency engine is bundled.

Move/copy v2 shapes (exact approved source/destination/IDs first):

```bash
himalaya -c "$CONFIG" -a "$ACCOUNT" --backend imap message move --from INBOX --to Archive "$MESSAGE_ID"
himalaya -c "$CONFIG" -a "$ACCOUNT" --backend imap message copy --from INBOX --to Important "$MESSAGE_ID"
himalaya -c "$CONFIG" -a "$ACCOUNT" --backend imap flag add --mailbox INBOX --flag seen "$MESSAGE_ID"
```

Copy/move are within an account/backend, not cross-account migration. A generic
success line may report zero matches. Deletion, flags, saved drafts, mailbox
creation/removal/expunge and bulk operations require exact current approval; no
read workflow authorizes them. Flag-set can replace existing flags/keywords;
backend-specific preservation and partial failures must be qualified.

## Attachments and filesystem effects

v2 shape is `attachment download --mailbox INBOX MESSAGE_ID PART_ID --dir DIRECTORY`;
`part IDs` are MIME positions, not message IDs. Omitting part IDs downloads all
parts, including inline parts. Approve the exact parts, bytes, destination and
retention; don't default to Downloads/tmp or automatically open/execute contents.

The inspected downloader chooses a nonexisting name then calls `fs::write`:
this is **not atomic** no-clobber; an existence check can miss a **dangling symlink**. After trying suffixes1..1023, it falls back to the original filename.
Unknown requested part IDs are checked **after writes**, so errors can leave
**partial writes**. Source comments claiming collision suffixing are not a safety
proof. Do not automate it into a shared/preexisting/hostile directory.

Before using that downloader, require an approved newly owned private directory
(e.g.0700 on POSIX), bounded inputs, a controlled no-concurrency parent, and inspect
resulting paths/permissions/partial effects. These precautions are not a hostile-
parent/race/Windows safety qualification, and none is implemented by this skill.
If those guarantees cannot be established, stop and propose a qualified no-replace
exporter rather than bypassing the guard. Filename cleanup is not malware/HTML/MIME
sanitization or a storage/backup guarantee.

## Sources and remaining gates

Reviewed tag v2.2.1 (commit metadata
`5b12b2a8c2c253b98f15c46610ad74cba2a182bc`): README, Cargo metadata, sample TOML,
CLI/main, selected shared commands and handler excerpts. README says no in-place
configuration subcommand, but the parser exposes top-level `configure`; prefer the
selected parser's surface and do not assume an in-place merge/write guarantee.
Master differs from the tag (including wizard feature text); don't blend them.
Standalone [MML](https://github.com/pimalaya/mml) README was read, not its entire
compiler/renderer/security chain. No CLI, compiler, account, mail, OAuth, secret
store, attachment, send, queue or provider/Windows runtime was exercised.
`runtime_verified` stays false. Large config/builder/client/dependency/model/SDK
and version-specific v1 behavior remain unreviewed; hashes/static tests do not
establish authenticity, consent, mail privacy or operational qualification.
