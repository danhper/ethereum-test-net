NODES=geth_node1 geth_node2 aleth_node1 aleth_node2
DATA_DIRS=$(addprefix data/,$(NODES))
NODE ?= geth_node1
OTHER_NODE ?= aleth_node1

init_geth_nodes:
	@docker-compose run geth_node1 init /etc/geth-config.json
	@docker-compose run geth_node2 init /etc/geth-config.json

output_block_info:
	@geth attach --datadir data/$(NODE)/ --exec "console.log(JSON.stringify(eth.getBlock('latest')))" | head -n1 > tmp/$(NODE).json

compare_blocks:
	@bash -c 'diff <(jq -S . tmp/$(NODE).json) <(jq -S . tmp/$(OTHER_NODE).json) || true'

clean_nodes_data:
	@rm -rf $(DATA_DIRS)
