#!/usr/bin/env bash
# Root hygiene baseline: no whitespace damage, and the file the repo's
# layout depends on is present.
set -euo pipefail

git diff --check
test -f .gitattributes
