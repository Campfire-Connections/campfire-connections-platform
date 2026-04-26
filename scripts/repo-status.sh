#!/usr/bin/env bash
set -euo pipefail

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

  branch="$(git -C "$repo" branch --show-current)"
  status="$(git -C "$repo" status --short)"

  printf '\n[%s] %s\n' "$repo" "${branch:-detached}"
  if [ -n "$status" ]; then
    printf '%s\n' "$status"
  else
    printf 'clean\n'
  fi
done
