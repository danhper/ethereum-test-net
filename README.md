# Private network setup for Ethereum

Requires Docker and docker-compose.

## Setup

1. Boot the `bootnode` with `docker-compose up bootnode`
2. Find the address of the bootnode (something looking like eth://somelongstring@ip:port) and replace the relevant parts of `docker-compose.yml` with the address
3. Initialize the geth nodes with `make init_geth_nodes`
4. Run the cluster with `docker-compose up`
5. The IPC endpoints will be in the `data` directory so you can attach a console and play as with normal Eth nodes.
