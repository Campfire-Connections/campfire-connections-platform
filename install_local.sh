#!/usr/bin/env bash
set -euo pipefail
python -m pip install -r requirements.txt
for pkg in core organization facility faction course enrollment reports pages user; do
  python -m pip install --no-build-isolation -e "./$pkg"
done
