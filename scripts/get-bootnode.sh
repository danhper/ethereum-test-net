#!/bin/bash

set -e

ROOT_DIR="$(dirname "$(cd "$(dirname "$0")" && pwd -P)")"

BOOTNODE=dummy docker-compose up -d bootnode
retry=3
bootnode=""
while [ $retry -gt 0 ] && [ -z "$bootnode" ]; do
    bootnode=$(docker-compose logs 2>/dev/null | sed -nr -e 's|.*?self=enode://(.+)|\1|p')
    retry=$((retry-1))
    sleep 1
done

BOOTNODE=dummy docker-compose down

if [ -z "$bootnode" ]; then
    echo "could not get bootnode"
    exit 1
fi

echo "$bootnode" > "$ROOT_DIR/.bootnode.txt"
