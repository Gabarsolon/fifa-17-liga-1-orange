#!/usr/bin/env bash
# Imports the given team keys one after another into the cumulative test project and copies a snapshot after each one.
# Usage: scripts/import_remaining.sh poli_iasi voluntari ...   (run from the repo root; needs FIFA17_DIR)
set -u
cd "$(dirname "$0")/.."
for key in "$@"; do
  echo "=== $key $(date +%H:%M:%S)"
  if PYTHONIOENCODING=utf-8 python scripts/import_team.py "$key" 2>&1 | grep -v "progress:\|^\[.*PM\]\|^> \|dotenv" | tail -n 25; then :; fi
  if [ "${PIPESTATUS[0]}" = "0" ]; then
    cp Liga1Orange.test.fbproject "Liga1Orange.$key.test.fbproject" && echo "snapshot Liga1Orange.$key.test.fbproject"
  else
    echo "FAILED $key"; break
  fi
done
echo "ALL DONE $(date +%H:%M:%S)"
