# AgentMail signup — separate account and credential action

A missing key is **not permission** to sign up, send an OTP or rotate credentials.
Ask for exact account ownership, chosen organization/username/region/human address,
terms/cost/visibility, output channel and credential-storage scope. There is no automatic
signup, email discovery, human-inbox access, console login, OTP retrieval, test send
or verification retry. An inbox owned by an agent does not authorize third-party
account/OTP flows.

## Selected CLI1.8.0 surface

`agentmail agent sign-up` / `POST /v0/agent/sign-up` accepts JSON or selected
body-field flags. `username` is required; **human_email is optional** in the current
schema. Omitting it creates a receive-only organization with no human OTP until a
human is attached. That does not make anonymous accounts/credential creation
implicitly approved. Omitted-human repeated signup creates another organization,
not key recovery; the original inbox username remains with the lost organization.

Inert request example, not a command to execute through Pi:

```json
{"username":"approved-agent","human_email":"owner@example.invalid","source":"agentmail-cli"}
```

`source` identifies the client; `referrer` is optional attribution. Preserve truthful,
owner-approved attribution; don't claim Hermes is the active client. Hosted docs
recommend carrying a full referral URL, but query strings can expose credentials,
OTP, personal/internal data or tracking parameters. Do not forward them without
specific consent; omit optional referrer or use an approved minimal value, rather
than inventing/leaking attribution.

## Returned secret and destructive retry

Response contains organization/inbox IDs and **api_key**, which **cannot be retrieved**
again via this signup response. It must go directly into an approved private secret
store/channel, not chat/tool stdout/logs/history or a committed plaintext file.
`--format json` prints structured secrets; it is not redaction. `--output` is for
binary responses, not a secure JSON-key capture mechanism. No approved credential
publisher is implemented by this skill; stop if secret output cannot be protected.

Repeating signup with the same human email **rotates** the API key and **invalidates**
the old one. "Idempotent" in the provider description is not a harmless/recovery/
exactly-once promise. Do not retry signup after a lost response or missing key
without explicit rotation/revocation approval and reconciliation of existing state.

## Human attachment and verification

- Current `agent attach-human` attaches/replaces a human on an unverified org and
  sends an OTP. Same-human retries are documented not to rotate the key; they
  still send/reuse an OTP and have state effects, so require exact approval.
  A different human replaces ownership contact, with documented replacement caps.
- `agent verify` consumes an explicitly supplied human **6-digit OTP**. Do not read
  private mail/accounts to retrieve it or print/pass secrets in argv/tool output.
  Use an already qualified approved secret-input channel; no bypass is provided.
- Selected reference: OTP expires after **24 hours**, maximum **10 attempts**.
  Same-human attach can obtain an expired OTP without rotating the key; while
  valid, it keeps the current OTP and attempt count. Do not burn attempts/loop,
  re-signup as recovery, guess OTPs or broaden/login a human account on failure.
- Reference describes limited unverified permissions, eventual cached-limit delay
  after attachment and free-plan entitlements after verification. Hosted values
  (one inbox/10 sends per day/restricted recipient) are plan/version-dependent,
  not authorization, entitlement or guaranteed currently free service.

## Verification versus sending

Check the explicitly approved result/status/IDs; listing all inboxes is private
provider access, not a generic key/installation check. A separately approved send
is not required to verify setup. Read-back/OTP accepted/API success does not prove
mail delivery, human receipt, sender identity or signup/terms consent.

Sources: pinned CLI reference signup/attach/verify sections and selected OpenAPI
schemas; hosted signup guide. No actual signup, secret storage/rotation/recovery,
OTP, email delivery, ownership contact, console/API account action or plan/runtime
qualification occurred. Human address/terms/provider approval must remain current.
