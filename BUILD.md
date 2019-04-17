# Build and run scripts manual

## Before building

Before going any further you have to build our custom `sawtooth-validator`
image. To build it:

* Download [this branch][1] of our fork of `sawtooth-core`.
* Build it with the command
  `docker-compose -f docker-compose-installed.yaml build validator`

## Makefile targets

* `build` rebuilds all Docker images from scratch. Provides lighter images.
* `build_dev` only updates the source code when rebuilt. Provides much faster
  builds but images are about 3 times bigger. Recommended for development
  purposes. **NOTE:** if you build with this target you must set the `DEV`
  environment variable for all runs (like `DEV=1 make run`).
* `clean` removes old Docker images.
* `run_genesis` starts a new node with a new genesis block and.
* `run_genesis_bg` does the same but the node is started in daemonized mode.
* `run` and `run_bg` are similar to the above but do not create a new genesis
  block.
* `run_user` and `run_user_bg` are intended for end users and also launch the
  monitoring service and the admin panel.
* `stop` stops the node running in the background.
* `release` builds release-ready Docker compose files and appropriate
  configuration files.

## scripts/run.sh

The script that allows you to run a REMME node. Following flags are provided:

* `-u` to start a node (default flag)
  * `-g` run a node in genesis mode
  * `-b` run a node in background
  * `-m` enable monitoring
  * `-p` enable admin panel
* `-d` to stop a node

[1]: https://github.com/Remmeauth/sawtooth-core/tree/1-1
