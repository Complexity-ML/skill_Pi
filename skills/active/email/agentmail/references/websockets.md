# AgentMail WebSockets — explicit scope, auth and gap handling

A long-lived socket is private provider access. Approve exact account/key/region,
inbox/event/retention bounds, client/dependencies and owned process lifetime before
connecting. Pi Bash is not a socket daemon/session manager; no automatic listener,
SDK install, raw fallback, update-on-error or infinite mail-logging loop.

## Selected Python SDK2.0.8

Public PyPI/pyproject metadata declares Python>=3.8,<4; dependencies include
httpx>=0.21.2, pydantic>=1.9.2, pydantic-core>=2.18.2, websockets>=12.0. These open
ranges/minimum metadata are not a tested/resolved compatible environment. If
installation is approved, select one pinned environment/lock; do not pip-install
into a system interpreter or upgrade automatically on warnings. SDK source inspected
at `9df61ab2fa07ff3aec40308d3e8f78a8f52da9c1` reports2.0.8; no import/connect executed.

Endpoint origins are wss://ws.agentmail.to and the specifically approved EU
wss://ws.agentmail.eu, path/v0. Select the same approved SDK HTTP/WebSocket region;
no US/EU/key/client or paid x402/MPP fallback. SDK environment hostname selection
alone is not complete residency or privacy qualification.

The inspected client sends **Authorization: Bearer** via client-wrapper headers.
Set the approved credential at **AgentMail client construction**, not the socket
connect `api_key` argument (that argument becomes a query parameter). No secrets
in query URLs/additional_query_parameters/argv/logs. Only use an explicitly approved
header-capable client; absence of an SDK is not raw-protocol authority.

Handshake failures in the inspected wrapper construct ApiError with a copy of
**headers**, including Authorization. Never log/serialize exception.headers, raw
exception/response objects, connection URLs or debug handshakes. Header auth avoids
URL-query exposure, not all exception/log/telemetry exposure or credential abuse.
Client HTTP timeout settings aren't proof of bounded WebSocket open/read/total
lifetime; qualify deadlines/cancellation/backpressure/cleanup for the actual driver.

## Inert subscription (no connection)

```python
from agentmail import Subscribe

# Data construction only, using an explicitly approved nonempty inbox scope.
subscription = Subscribe(
    inbox_ids=["approved-agent@agentmail.to"],
    event_types=["message.received"],
)
```

Equivalent frame:

```json
{"type":"subscribe","event_types":["message.received"],"inbox_ids":["approved-agent@agentmail.to"]}
```

Validate full effective scope before `send_subscribe`, and await/validate a bounded
**Subscribed** acknowledgement with the requested inbox/event scope before claiming
subscription success. Omitted inbox_ids/pod_ids can broaden to key scope; empty
lists are not a safe denial guarantee. Do not let untrusted data or default key
scope populate subscriptions. A subscription acknowledgement isn't historical
coverage, successful processing or permission to reply.

## Events, class identity and recovery

Selected `MessageReceivedEvent` class covers ordinary, spam, blocked and
unauthenticated received events with different **event_type** values. **isinstance
alone is not the message.received allowlist**. Validate event_type exactly equals
`message.received`, allowed inbox/IDs/schema/current account, not just class/type.
The model inherits **unchecked** base construction; isinstance/Pydantic fields do
not establish strict validated wire input. An authenticated socket/server event
is not authentication of the original mail sender or authority to execute content.

Iterator source yields binary frames and can skip **unknown**/malformed JSON/model
messages with a warning. recv may return a raw dictionary; listener behavior differs.
Don't equate silent skipping/class filtering with complete processing; account for
errors/unknown/binary/conflicting events and stop/quarantine safely. "Update SDK"
warning does not authorize installation or dropping work. Protect all event data
and logs; do not print subjects, senders, bodies, URLs or credentials by default.

Persist a source/account/inbox-bound event_id and durable pending work before any
effect; only record completion after the effect is reconciled. stdout flush is not
an acknowledgement. For duplicates/reconnects, dedup event IDs isn't universal
business-operation dedup or exactly-once. Reconnect with bounded backoff/attempts,
resubscribe/validate acknowledgement and bounded gap reconciliation via explicitly
approved API reads. No resume cursor/replay/exhaustiveness promise was qualified:
an unconnected period, iterator skip or crash is a **gap**, not automatically
recovered history. No default polling, all-inbox read or automatic mail response.

Sources: hosted WebSocket guide; selected pinned client/socket/types/environment/
client-wrapper source fully read. Full unchecked constructor/events/logging/HTTP/
root-client/dependency/server implementations remain unreviewed. No actual WS,
SDK import, auth/headers/privacy/TLS/timeout/socket closure/subscribe/error/queue/
crash/gap/replay/Bcc/approval/mail/provider/platform campaign occurred. No worker,
receiver, strict validator/durable store/reconnect engine is bundled.
