# chess/service

Empty on purpose.

The RPCs, and the HTTP method and path each one answers on. A `service` block per
API, with `google.api.http` annotations on every method.

Those annotations are also what produces `contracts/gen/openapi`:
`protoc-gen-openapi` walks services, not messages, so until there is a service
here that document has no paths in it. The vendored `google/api` protos in
`idl/third_party` are already in place for when there is.

Requests and responses live in `chess/dto`, not here. This directory says what
can be called; `chess/dto` says what is sent.

Filled in when the API exists.
