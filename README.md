# Private network setup for Ethereum

Requires Docker and docker-compose.

## Setup

1. Setup the installation using `make setup`. This will create a key for the bootnode, initialize geth nodes and copy the content of the instrumentation build directory to the host machine. You may be prompted for `sudo` if you do not have the permission to write in Docker directory (see note below)
2. Run the cluster with `make run_cluster`
3. The IPC endpoints will be in the `data` directory so you can attach a console and play as with normal Eth nodes.

NOTE: depending on your Docker setup, you might need to run `chown` on the data directory to be able to access `geth.ipc`: `sudo chown -R $(whoami) data`
