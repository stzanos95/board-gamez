# core/dto

What a message looks like in transit, whatever it happens to be carrying.

```
websocket.proto  WebsocketMessageEnvelope, WebsocketMessageHeader
queue.proto      QueueMessageEnvelope, QueueMessageHeader
```

Both transports carry frames that are bytes and nothing else — no identity, no
type, no routing — so both need an envelope: a header the transport reads, and a
payload it does not. The header carries what routing, logging and delivery need;
the payload is `google.protobuf.Any`, packed by the domain that produced it and
opened only by the domain that consumes it. A relay carries messages whose types
it was never compiled against, which is the entire point.

**One header per transport, never a shared one.** They rhyme; they are not the
same. A socket frame has a connection behind it and may be unsolicited in either
direction. A queue message outlives its sender, arrives more than once, and may
be replayed long after. Those facts imply different fields, and they arrive at
different times. A shared header would mean every field either applies to both or
is documented as ignored by one.

**The header addresses, the payload means.** Neither envelope carries a status.
An outcome — accepted, rejected, and why — is a payload type named by `type`, so
a consumer branches the same way on either transport.

`type` is a string, which is the one place this repository tolerates one. Core
cannot enumerate the message types of domains it must not import — the same
constraint that makes the payload opaque. The obligation moves outward: each
domain owns the constants for its own types, and nothing in core validates them.
