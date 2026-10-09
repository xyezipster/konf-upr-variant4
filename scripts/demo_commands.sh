#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
./run.sh --vfs data/demo.json --log logs/stage4.json     --startup scripts/stage4.txt
./run.sh --vfs data/demo.json --log logs/stage5.json     --startup scripts/stage5.txt
