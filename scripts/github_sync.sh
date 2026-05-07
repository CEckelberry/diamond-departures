#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
	echo "[sync] not a git repo yet: $ROOT"
	echo "[sync] run: git init && git remote add origin <repo-url>"
	exit 0
fi

branch="$(git rev-parse --abbrev-ref HEAD)"
echo "[sync] branch=$branch"

git add -A
if ! git diff --cached --quiet; then
	git commit -m "checkpoint: agent progress $(date +%F-%H%M)"
else
	echo "[sync] no local changes to commit"
fi

git pull --rebase origin "$branch" || true
git push origin "$branch" || true

echo "[sync] done"
