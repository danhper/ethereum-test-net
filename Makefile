NODES=geth_node1 geth_node2 aleth_node1 aleth_node2
DATA_DIRS=$(addprefix data/,$(NODES))
NODE ?= geth_node1
OTHER_NODE ?= aleth_node1

init_geth_nodes:
	@BOOTNODE=dummy docker-compose run geth_node1 init /etc/geth-config.json
	@BOOTNODE=dummy docker-compose run geth_node2 init /etc/geth-config.json

generate_boot_key:
	@BOOTNODE=dummy docker-compose run bootnode --genkey=/root/.ethereum/boot.key

output_block_info:
	@geth attach --datadir data/$(NODE)/ --exec "console.log(JSON.stringify(eth.getBlock('latest')))" | head -n1 > tmp/$(NODE).json

compare_blocks:
	@bash -c 'diff <(jq -S . tmp/$(NODE).json) <(jq -S . tmp/$(OTHER_NODE).json) || true'

clean_nodes_data:
	@rm -rf $(DATA_DIRS)

run_cluster:
	@test -f .bootnode.txt || ./scripts/get-bootnode.sh || { echo ".bootnode.txt not found" && exit 1; }
	@BOOTNODE=$(shell cat .bootnode.txt) docker-compose up
