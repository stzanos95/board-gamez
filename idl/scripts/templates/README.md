# templates

The packaging files that ship beside the generated code, before their values are
filled in.

```
pyproject.toml.template   rendered to contracts/gen/python/pyproject.toml
package.json.template     rendered to contracts/gen/typescript/package.json
```

`generate.sh` renders these on every run, so the packaging is as regenerable as
the code it wraps and no file under `contracts/gen` is ever hand-edited.

`envsubst` does the substitution — `${NAME}` and nothing else, no control flow.
It is named explicitly at each call site, so a `$` that is not one of the listed
variables survives untouched.

The versions are read rather than written down. The protobuf floor comes out of
the header protoc stamps into its own output, and the `@bufbuild/protobuf`
version is the plugin version the image was built with. Bumping a pin in
`docker/Dockerfile` therefore moves the packaging with it, and there is no second
place to remember.
