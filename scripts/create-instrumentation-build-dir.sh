#!/bin/bash

set -e

export BOOTNODE=dummy

docker-compose config --services | grep -q instrumented_aleth_node1 || exit 0

sed -i -r -e 's|^(\s+)(- ./docker-data/instrumented_aleth_node1/build:/aleth/build)|\1# \2|' docker-compose.yml

docker-compose up -d instrumented_aleth_node1

container_id="$(docker-compose ps -q instrumented_aleth_node1)"

if ! mkdir -p ./docker-data/build > /dev/null 2>&1; then
  sudo chown -R "$(id -un):$(id -gn)" ./docker-data
fi

docker cp "$container_id:/aleth/build" ./docker-data/instrumented_aleth_node1/build

sed -i -r -e 's|^(\s+)# (- ./docker-data/instrumented_aleth_node1/build:/aleth/build)|\1\2|' docker-compose.yml

docker-compose down
