#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
for vfs in data/minimal.json data/files.json data/deep.json; do
    ./run.sh --vfs "$vfs" --startup scripts/stage3.txt
 done
./run.sh --startup scripts/stage3.txt
