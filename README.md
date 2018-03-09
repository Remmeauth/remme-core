# REMME Core

[![CircleCI](https://img.shields.io/circleci/project/github/Remmeauth/remme-core.svg)](https://circleci.com/gh/Remmeauth/remme-core)
[![Docker Stars](https://img.shields.io/docker/stars/remme/remme-core.svg)](https://hub.docker.com/r/remme/remme-core/)

**This is an alpha version! It is not suitable for any use in production and is intended to demonstrate capabilities of Hyperledger Sawtooth in the scope of REMME.**

## How to run

You will need Docker and Docker Compose installed on your machine.

### For an end-user

1. Download the latest release from [Releases](https://github.com/Remmeauth/remme-core/releases) section (`<version_number>-release.zip`). Unpack it.
1. Start node: Open a terminal inside the unpacked folder and run `./run.sh`.
1. Enter interactive shell: Open a new terminal window and run `./shell.sh`.

On the first run you will need to initialize the genesis block. To make that just run `./genesis.sh`. This will generate a new key pair and genesis block.

### For developers & contributors

Clone this repository to your machine: `git clone https://github.com/Remmeauth/remme-core.git`

When you have this repository cloned go the project directory run the following commands:

- `make build_docker`
- `make run_dev`

After all the packages are started up run `make shell` in a separate terminal to enter the interactive console.

You can try `rem-token` and `rem-crt` commands to run operations related to token and certificates respectively.

You can also run `make test` to run automated tests.
