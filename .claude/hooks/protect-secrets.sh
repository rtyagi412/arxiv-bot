#!/usr/bin/env bash
# PreToolUse: block direct Claude file-tool writes to commonly sensitive files.
# This is a guardrail, NOT a full secret scanner or Git commit protection.
set -euo pipefail

payload="$(cat)"
# Extract "file_path" with pure bash (no jq dependency). Windows paths arrive
# JSON-escaped (C:\\Users\\...); the separator normalization below handles that.
path=""
if [[ "$payload" =~ \"file_path\"[[:space:]]*:[[:space:]]*\"(([^\"\\]|\\.)*)\" ]]; then
  path="${BASH_REMATCH[1]}"
fi
[[ -n "$path" ]] || exit 0
path="${path//\\//}"
base="${path##*/}"

case "$base" in
  .env.example|.env.sample|.env.template) exit 0 ;;
  .env|.env.*|*.pem|*.key|*.p12|*.pfx|id_rsa|id_ed25519|credentials.json|service-account.json)
    echo "Refusing to write a likely sensitive file: $path. Use an untracked local secrets mechanism or a safe example file." >&2
    exit 2
    ;;
esac
