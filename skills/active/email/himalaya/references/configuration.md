# Himalaya configuration — v2.2.1 source reference

This is the v2 schema, not a drop-in update to v1 `backend.*`/folder mappings.
A TOML parse succeeds independently of whether a selected Himalaya build accepts
or uses those fields. Don't silently migrate an account or infer success from an
ignored key. Confirm version, build features, account/backend and exact approved
config/overlays before reading private configuration or running any client.

## Config selection and wizard boundaries

Source paths: `$XDG_CONFIG_HOME/himalaya/config.toml`, then
`$HOME/.config/himalaya/config.toml`, then `$HOME/.himalayarc`; explicit `-c` or
`HIMALAYA_CONFIG` overrides defaults. Prefer one owner-approved absolute file;
never enumerate/mine these paths to discover accounts or credentials.

Multiple `-c` paths are colon-delimited, base plus deep-merged overlays. Review all
inputs and precedence; a filename containing a colon/Windows drive syntax needs
version-specific handling, not just shell quoting. Files/tools do not universally
expand `~` or shell variables. Don't overwrite a file by redirecting a wizard into
it, copy secrets into examples, or replace the whole configuration from a partial
read. Updates/backups/permissions/current version require explicit approval.

The tagged README says no in-place configuration subcommand; tagged CLI source
has top-level **`himalaya configure`** (`wizard` alias), while `account` exposes
`list` and `check`, not the old `account configure` surface. This documentation
conflict is not resolved by assuming safe in-place persistence. Missing config
can trigger an interactive wizard when input is a TTY; JSON/non-TTY account
resolution suppresses the offer. Wizard discovery probes email-domain services,
authenticates/tests connections and can write config: not an offline helper.
Pi Bash provides no assumed PTY; run no wizard/check/discovery automatically.

## Representative IMAP + SMTP TOML (inert placeholders)

Owner-supplied account/servers/credentials must replace placeholders after review.
This example is only syntax-parsed offline; it is not a working/live account.

```toml
[accounts.example]
email = "user@example.invalid"
display-name = "Example User"

imap.server = "imaps://imap.example.invalid:993"
imap.sasl.plain.username = "user@example.invalid"
imap.sasl.plain.password.command = ["pass", "show", "APPROVED_IMAP_ENTRY"]

smtp.server = "smtp://smtp.example.invalid:587"
smtp.starttls = true
smtp.sasl.plain.username = "user@example.invalid"
smtp.sasl.plain.password.command = ["pass", "show", "APPROVED_SMTP_ENTRY"]

mailbox.alias.inbox = "INBOX"
mailbox.alias.sent = "Sent"
mailbox.alias.drafts = "Drafts"
mailbox.alias.trash = "Trash"
```

`mailbox.alias` is the current mapping (not either old folder-alias spelling).
Aliases/roles bind to native mailbox names/IDs and can override backend roles.
Localized/provider names may differ. Verify exact destinations and save-copy policy;
Gmail/Graph can file sent messages themselves. Do not enable a duplicate copy by
default or treat a missing Sent copy as send failure. Signature, sender, default
account, proxy and global settings can change the effective operation.

## Secrets, OAuth and TLS

- v2 removed **native keyring** and embedded OAuth flows. A credential command or
  **external broker** supplies a secret/access token; this does not install `pass`,
  `ortie`, a keyring, browser OAuth or provider scopes.
- Command sources execute programs and may refresh/persist tokens or contact a
  provider. Approve the exact executable, arguments, credential entry, environment,
  network and persistence scope. A vector avoids constructing shell text but is
  not a sandbox. The command must output only the expected credential; check its
  failure/format behavior without printing secrets. Do not mine the keyring.
- Raw literals expose secrets in plaintext TOML and backups; no raw-password
  default. Restrict approved files/parents (0600/0700 on POSIX as appropriate),
  refuse symlink/unexpected files and protect logs; these are not Windows ACL,
  hostile-parent or race guarantees. No secure writer/migration is bundled.
- Explicit IMAPS/SMTPS or properly configured mandatory STARTTLS, verified trust
  and approved endpoints are required. Loopback is not identity/security proof.
  Do not disable TLS/auth or accept an arbitrary certificate to fix connectivity.
- Per-backend/account **proxy** config or proxy environment variables can route
  connections elsewhere; review rather than assuming a direct/private connection.
- Native Gmail/Graph/JMAP and other SASL schemes need their selected schema,
  permissions, scopes and broker configuration checked separately. Provider policy
  (e.g. whether Gmail app passwords are available) is not guaranteed by enabling
  2FA. Older iCloud recipes aren't universally correct username/policy evidence.
  No OAuth broker, app-password creation, refresh or provider login was tested.

## Sources and unresolved qualifications

`pimalaya/himalaya` tag v2.2.1: README and `config.sample.toml` fully read; `src/cli.rs`
fully read. The large `src/config.rs`, secret/runtime dependency implementations,
all overlays/backend auth/proxy code and older-version behavior remain unreviewed.
The native executable is absent. Parsing this synthetic TOML proves syntax and
expected example structure only, not deserialization, meaningful settings,
credential security, provider compatibility, TLS or authorization.
