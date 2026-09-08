#!/usr/bin/env bash
# Everything that has to be true of the schema, in the order it is worth knowing.
#
# Lints, checks formatting, regenerates, and then fails if regenerating changed
# anything — which means contracts/gen was committed from a different schema
# than contracts/proto now holds. Run this in CI, and before a release.
source "$(dirname "${BASH_SOURCE[0]}")/_shared.sh"
require_docker

echo "--- lint ---"
idl_compose_run lint

echo "--- format ---"
idl_compose_run format-check

echo "--- generate ---"
idl_compose_run generate

echo "--- contracts/gen is in step with contracts/proto ---"
if ! command -v git >/dev/null 2>&1 || [ ! -d "$REPO_ROOT/.git" ]; then
    echo "not a git checkout, so drift cannot be judged; skipped"
    exit 0
fi

# --porcelain rather than `git diff`, so a newly generated file that has never
# been added still counts as drift.
drift="$(git -C "$REPO_ROOT" status --porcelain -- idl/contracts/gen)"
if [ -n "$drift" ]; then
    echo "contracts/gen does not match contracts/proto. Regenerated files differ:" >&2
    echo "$drift" >&2
    echo >&2
    echo "Commit the regenerated output:  git add idl/contracts/gen" >&2
    exit 1
fi
echo "contracts/gen is up to date"
