#!/bin/bash

set -e

ROOT_DIR="$(dirname "$(cd "$(dirname "$0")" && pwd -P)")"
BOOTNODE_FILE="$ROOT_DIR/.bootnode.txt"

if [ ! -f "$BOOTNODE_FILE" ]; then
  . "$ROOT_DIR/scripts/get-bootnode.sh"
fi

BOOTNODE="$(cat "$BOOTNODE_FILE")"

cd "$ROOT_DIR" && BOOTNODE=$BOOTNODE docker-compose up $@
