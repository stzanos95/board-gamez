# third_party

Proto files this repository did not write, vendored so that generation needs no
network and no package registry.

```
google/api/http.proto         the HttpRule message
google/api/annotations.proto  the (google.api.http) method option
```

Both come from [googleapis](https://github.com/googleapis/googleapis) and are
Apache-2.0 licensed. They are here ahead of the services that will need them: a
method carries its HTTP binding as a `(google.api.http)` option, and those
options are what `protoc-gen-openapi` reads to produce paths rather than an
empty document. Nothing imports them yet — `contracts/proto/idl/chess/service`
is still empty.

It sits beside `contracts/` rather than inside it, because a contract is
something this repository offers and these files are only what the compiler
needs to read ours.

Nothing here is linted, formatted or generated from: `buf.yaml` ignores this
directory, and `entrypoint.sh` passes it to `protoc` as an include path only. It
is not ours to reformat, and generating it would put Google's types into
`contracts/gen` alongside our own.

`google/protobuf/*` is not vendored. Those are the well-known types, which
`protoc` and `buf` both carry inside themselves.
