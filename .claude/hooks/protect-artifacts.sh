#!/usr/bin/env bash
# PreToolUse: prevent accidental edits to versioned SDLC artifacts.
# Intentional revisions: set CLAUDE_ALLOW_ARTIFACT_EDITS=1 for the Claude Code session.
set -euo pipefail

if [[ "${CLAUDE_ALLOW_ARTIFACT_EDITS:-}" == "1" ]]; then
  exit 0
fi

payload="$(cat)"
# Extract "file_path" with pure bash (no jq dependency). Windows paths arrive
# JSON-escaped (C:\\Users\\...); the separator normalization below handles that.
path=""
if [[ "$payload" =~ \"file_path\"[[:space:]]*:[[:space:]]*\"(([^\"\\]|\\.)*)\" ]]; then
  path="${BASH_REMATCH[1]}"
fi
[[ -n "$path" ]] || exit 0

# Normalize path separators and check only feature artifacts.
path="${path//\\//}"
if [[ "/$path" =~ /docs/features/[^/]+/(intent|spec|plan)\.md$ ]]; then
  echo "Protected SDLC artifact: $path. For an intentional reviewed revision, restart Claude Code with CLAUDE_ALLOW_ARTIFACT_EDITS=1; then commit the revision." >&2
  exit 2
fi
