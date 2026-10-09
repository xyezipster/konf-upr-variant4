#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
./run.sh --startup scripts/missing.txt < /dev/null
./run.sh --startup scripts/stage2.txt --log logs/errors.json
