NODES=geth_node1 geth_node2 aleth_node1 aleth_node2
DATA_DIR = $(HOME)/.eth-docker-data
DATA_DIRS=$(addprefix $(DATA_DIR)/,$(NODES))
NODE ?= geth_node1
OTHER_NODE ?= aleth_node1
BOOTNODE_PATH ?= bootnode/bootnode

all: run

$(BOOTNODE_PATH):
	@cd bootnode && ./get-tools.sh

setup: create_instrumentation_build_dir generate_boot_key init_geth_nodes

init_geth_nodes:
	@BOOTNODE=dummy DATA_DIR=$(DATA_DIR) docker-compose run geth_node1 init /etc/geth-config.json
	@BOOTNODE=dummy DATA_DIR=$(DATA_DIR) docker-compose run geth_node2 init /etc/geth-config.json

create_instrumentation_build_dir:
	@DATA_DIR=$(DATA_DIR) ./scripts/create-instrumentation-build-dir.sh

generate_boot_key: $(BOOTNODE_PATH)
	@BOOTNODE=dummy DATA_DIR=$(DATA_DIR) docker-compose run bootnode --genkey=/root/.ethereum/boot.key

output_block_info:
	@geth attach --datadir $(DATA_DIR)/$(NODE)/ --exec "console.log(JSON.stringify(eth.getBlock('latest')))" | head -n1 > tmp/$(NODE).json

compare_blocks:
	@bash -c 'diff <(jq -S . tmp/$(NODE).json) <(jq -S . tmp/$(OTHER_NODE).json) || true'

compute_aleth_coverage:
	@BOOTNODE=dummy DATA_DIR=$(DATA_DIR) docker-compose run --entrypoint lcov instrumented_aleth_node1 --directory /aleth/build/ --capture --output-file /aleth/build/aleth-cov.info --rc lcov_branch_coverage=1
	@BOOTNODE=dummy DATA_DIR=$(DATA_DIR) docker-compose run --entrypoint genhtml instrumented_aleth_node1 -o build/aleth-cov-report build/aleth-cov.info --branch-coverage
	@echo "HTML report saved in $(DATA_DIR)/instrumented_aleth_node1/build/aleth-cov-report"

clean_nodes_data:
	@rm -rf $(DATA_DIRS)

clean_coverage:
	@find $(DATA_DIR)/instrumented_aleth_node1 -name "*.gcov" -delete
	@find $(DATA_DIR)/instrumented_aleth_node1 -name "*.gcda" -delete
	@rm -rf $(DATA_DIR)/instrumented_aleth_node1/build/aleth-cov-report
	@rm -rf $(DATA_DIR)/instrumented_aleth_node1/build/aleth-cov.info

clean:
	@BOOTNODE=dummy DATA_DIR=$(DATA_DIR) docker-compose down
	@rm -rf $(DATA_DIR)
	@rm -f .bootnode.txt
	@rm -rf tmp/*

run_cluster:
	@DATA_DIR=$(DATA_DIR) ./scripts/run-cluster.sh
