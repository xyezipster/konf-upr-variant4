#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
if ./run.sh --vfs data/missing.json < /dev/null; then
    exit 1
fi
if ./run.sh --vfs data/invalid.json < /dev/null; then
    exit 1
fi
