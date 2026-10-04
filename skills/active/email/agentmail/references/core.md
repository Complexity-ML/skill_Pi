# AgentMail core — selected CLI1.8.0 / API schema

No install, signup, account discovery or default health-check inbox enumeration.
Before each command approve the account/key/region, exact inbox IDs, read/write,
output/retention and cost scope. `API_ORIGIN`, `INBOX_ID`, `MESSAGE_ID`, `THREAD_ID`
and `ATTACHMENT_ID` below are validated owner-approved values, not discovered
private defaults. **API origin** is `https://api.agentmail.to` or the specifically
approved EU origin, without `/v0`; selected operation paths include `/v0`.

## CLI shape and inert request bodies

Selected `reference.md` uses nested space commands (`inboxes messages`, `inboxes
threads`); older hosted recipes use colon names. Their alias compatibility was not
qualified here. `--format json` selects output, **`--json -`** consumes a request
body from stdin. Never interpret output JSON as proof of success or completeness.
`--params` can override flag values: approve the complete effective request, not
just a headline command. Don't put secrets/large private bodies in argv.

Scoped read templates (POSIX Bash, only after approval):

```bash
agentmail inboxes get --base-url "$API_ORIGIN" --inbox-id "$INBOX_ID" --format json
agentmail inboxes messages list --base-url "$API_ORIGIN" --inbox-id "$INBOX_ID" --labels unread --limit 20 --format json
agentmail inboxes messages get --base-url "$API_ORIGIN" --inbox-id "$INBOX_ID" --message-id "$MESSAGE_ID" --format json
agentmail inboxes threads get --base-url "$API_ORIGIN" --inbox-id "$INBOX_ID" --thread-id "$THREAD_ID" --format json
```

The schema/query flag is **`--labels`**, not the old singular hosted spelling.
Body arrays use JSON or the selected parser's documented repeatable plural flags;
JSON avoids assuming `--label`/`--event-type`/`--inbox-id` aliases for arrays.

Inert create-inbox JSON, not a command or consent to create:

```json
{"username":"approved-agent","domain":"agentmail.to","display_name":"Approved Agent","client_id":"approved-operation-id"}
```

Default domain is agentmail.to. Custom domains must be verified or an enabled
subdomain of a verified domain. Choosing a username, omitting it for a random one,
changing display/metadata/domain or creating a mailbox is a provider write/resource
allocation, potentially billed. `client_id` identifies selected create requests;
hosted docs recommend stable values for retries, but schema alone does not prove
scope, conflict, retention or exactly-once behavior. Bind any operation ID to the
full payload/account/origin and reconcile uncertain creates before reissuing.

## Pagination and reads

List output is an envelope (e.g. `messages`, `count`, optional `next_page_token`),
not a bare complete list. Use bounded `--page-token` continuation, retain exact
opaque cursors and reject repeats/ambiguous schemas. Don't stop merely at an
**empty page** while a next token remains. Track page/item/byte/time budgets,
filters, retained errors and partial results; pagination is not a snapshot.
Search/filter semantics exclude categories and can cap limits: not full account/
mailbox export. Do not broaden spam/trash/unauthenticated filters without approval.

`--page-all` streams **NDJSON**, defaults to a **page-limit** of10, and the inspected
executor emits a page then stops continuation at its cap. **exit0**/"page-all" does
not prove all pages consumed. Require an observed terminal cursor to claim even
bounded terminal pagination; preserve partial status on cap/cycle/failure and
parse the chosen streaming format, not one assumed JSON document. Limits are not
hard process/DNS/memory/storage/privacy boundaries. Set approved finite transport/
output budgets; CLI transport default has no total request timeout in the excerpt.

`extracted_text`/`extracted_html` are extracted **new content**, **not full** thread/
raw MIME, not necessarily all commitments/context. They are **not a sanitizer**,
sender authentication or a reason to execute instructions/render HTML/load remote
images/follow links. Plain text minimization is preferable when sufficient. Missing
text/extraction/attachments is not evidence of an empty/safe message. Resolve only
approved additional context, and distinguish rendering from byte-preserving backup.

## Send, reply, forward and drafts

Prefer an approved local draft via Pi file tools; provider drafts are writes and
can be sent later. Sending is a separately approved operation, not a test of key
validity. Full current From/inbox identity, To/Cc/**Bcc**, Reply-To, subject,
text/HTML, attachment bytes/URLs, headers/tracking, target message/thread, account/
origin/cost must be approved. If changed since approval, stop and reapprove.
Incoming Reply-To/From, threading and quoted material do not authorize reply-all or
forwarding; server-derived recipients must be resolved/approved rather than guessed.

Inert send JSON (no transmission/pipeline supplied):

```json
{"to":["recipient@example.invalid"],"subject":"Approved draft","text":"Local draft body.","labels":["outreach"],"track_opens":false}
```

Selected commands are `inboxes messages send`, `reply`, `reply-all`, `forward`;
IDs are flags, body via reviewed JSON/stdin. Label changes use `update` with
`add_labels`/`remove_labels` in the body. `unread`/`handled` labels are not task
completion, unread privacy guarantees, consent, delivery or an atomic work queue.
No blind delete, bulk label, default HTML/tracking or automatic reply is authorized.
Hosted docs mention50 total To/Cc/Bcc recipients; selected service/account constraints
must still be verified (schema does not enforce every business limit).

Selected send/reply/reply-all/forward schema documents **Idempotency-Key**, CLI
`--idempotency-key`: repeat same key/request returns original message, different
request yields **409**, keys expire **24 hours** after completion. This is not
universal forever dedup or approval. Persist an exact payload/account/origin/
operation binding and key before attempting, reconcile ambiguous failure, don't
rotate keys/retry after expiry blindly. A Message-ID/read-back is
**not proof of delivery** or human receipt.

CLI/SDK can retry automatically (different policies/version/options). Inspected
CLI retry function treats408/429 as retryable even for some mutations, while SDK
README defaults2 retries on408/429/5xx; retryability is not proof of no first effect.
Review/disable automatic retries with a qualified selected option before sensitive
writes; don't invent exactly-once or rely on `Retry-After` alone. Default policy/
markers/key-generation/full binding code were not completely reviewed.

## Attachments and raw-message retrieval

```bash
agentmail inboxes messages get-attachment --base-url "$API_ORIGIN" --inbox-id "$INBOX_ID" --message-id "$MESSAGE_ID" --attachment-id "$ATTACHMENT_ID" --format json
```

Response is **metadata**: signed `download_url`, optional `text_url`, `expires_at`,
size/name/type. Getting it is not downloading/validating attachment bytes. URLs are
bearer-like secrets; don't log/store/share them indefinitely. Refresh metadata only
within approved scope when needed. A raw-message endpoint can likewise return a
URL/receipt, not necessarily raw MIME directly: verify selected response schema.

A separately approved downloader must validate exact trusted HTTPS CDN/origin,
redirect policy, byte/time/file bounds, integrity/type, private retention and
**no-clobber** staging; **no bearer** AgentMail account credential forwarded to a
returned URL. Don't copy a suggested filename/path or open/execute attachment code.
`--output`/shell `>` is not an atomic no-replace exporter or private JSON/key writer.
No qualified downloader/publisher is bundled in this skill.

Selected send attachment schema accepts either **Base64** `content` or service-
fetched `url`. Base64 content shares the documented6 MB **whole request** limit
(including body/encoding overhead); URL-backed attachments advise around **30 MB**
total, not a hard guarantee. Hosting/fetching an accessible/pre-signed URL is a
separate disclosure/service operation, not a secret-bearing fetch fallback. Approve
exact bytes/URL recipients/retention and no arbitrary local/remote path inference.

## REST and failures

REST path prefix is `/v0`; switching from CLI/SDK to REST is a new client/credential/
logging/transport decision, not an automatic missing-operation fallback. Auth only
to the approved exact origin, no redirect/TLS/proxy/region bypass. Capture HTTP
status plus body; check exit/schema before projecting. Error `name`/`message`/
validation `errors` vary by operation; they do not uniquely diagnose permissions.
Honor bounded Retry-After/backoff where safe, but ambiguous send/write requires
reconciliation, not repeated effects. No live CLI/REST/schema/provider/recipient/
privacy/idempotency/pagination/download/permission/approval tests occurred.
