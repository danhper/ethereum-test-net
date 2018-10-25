# Private network setup for Ethereum

Requires Docker and docker-compose.

## Setup

1. Generate a key for the `bootnode` with `make generate_boot_key`
2. Initialize the geth nodes with `make init_geth_nodes`
3. Run the cluster with `make run_cluster`
4. The IPC endpoints will be in the `data` directory so you can attach a console and play as with normal Eth nodes.

NOTE: depending on your Docker setup, you might need to run `chown` on the data directory to be able to access `geth.ipc`: `chown -R $(whoami) data`
