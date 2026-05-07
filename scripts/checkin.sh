#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

stamp="$(date +%F-%H%M%S)"
out="orchestration/checkins/${stamp}.md"

{
	echo "# Check-in ${stamp}"
	echo
	echo "## Task board snapshot"
	echo '```'
	cat orchestration/task-board.yaml
	echo '```'
	echo
	echo "## Git status"
	echo '```'
	if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
		git status --short --branch
	else
		echo "not a git repo"
	fi
	echo '```'
} >"$out"

echo "wrote $out"
