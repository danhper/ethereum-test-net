#!/bin/bash

set -e

export BOOTNODE=dummy

sed -i -r -e 's|^(\s+)(- ./data/instrumented_aleth_node1/build:/aleth/build)|\1# \2|' docker-compose.yml

docker-compose up -d instrumented_aleth_node1

container_id="$(docker-compose ps -q instrumented_aleth_node1)"

if ! mkdir -p data/build > /dev/null 2>&1; then
  sudo chown -R "$(id -un):$(id -gn)" data
fi

docker cp "$container_id:/aleth/build" data/instrumented_aleth_node1/build

sed -i -r -e 's|^(\s+)# (- ./data/instrumented_aleth_node1/build:/aleth/build)|\1\2|' docker-compose.yml

docker-compose down
