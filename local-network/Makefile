include .env

GETH_ARGS := --bootnodes "enode://$(BOOTNODE)" --networkid $(NETWORK_ID) \
			 --syncmode full --miner.threads 1 --datadir data/geth --port 30313

ALETH_ARGS := --peerset "required:$(BOOTNODE)" --network-id $(NETWORK_ID) \
			  --config ../config/aleth-config.json -t 1 --no-bootstrap --db-path data/aleth

bootnode:
	bootnode -nodekey boot.key

aleth:
	$(ALETH_PATH) $(ALETH_ARGS)

aleth_debug:
	gdb --args $(ALETH_PATH) $(ALETH_ARGS)

geth:
	go run $(GETH_CMD) $(GETH_ARGS)

geth_debug:
	dlv debug $(GETH_CMD) -- $(GETH_ARGS)
