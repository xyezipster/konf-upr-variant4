#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
./run.sh --startup scripts/stage2.txt --log logs/config.json
./run.sh --vfs data/demo.json --startup scripts/stage2.txt
