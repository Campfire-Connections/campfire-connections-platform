#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -eq 0 ]; then
  printf 'usage: %s <command> [args...]\n' "$0" >&2
  exit 2
fi

repos=(
  "."
  "core"
  "course"
  "enrollment"
  "facility"
  "faction"
  "organization"
  "pages"
  "reports"
  "user"
)

for repo in "${repos[@]}"; do
  if [ ! -d "$repo/.git" ]; then
    continue
  fi

  printf '\n[%s] %s\n' "$repo" "$*"
  git -C "$repo" "$@"
done
