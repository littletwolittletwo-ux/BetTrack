#!/usr/bin/env bash
set -euo pipefail
echo "== Installing test deps =="
pip install -q -r requirements-test.txt
echo "== Running tests =="
pytest -q || { echo 'Tests failed'; exit 1; }
echo "== All tests passed ✅ =="