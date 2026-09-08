# core/obj

Empty on purpose.

Storage shapes that are not any one domain's — an outbox row, a processed-message
record for deduplicating redeliveries, a lease.

The first of these will arrive with the first queue consumer, because
at-least-once delivery means a consumer has to remember what it has already seen.
