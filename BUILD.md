# Build and run scripts manual

## Makefile targets

* `build` rebuilds all Docker images from scratch. Provides lighter images.
* `build_dev` only updates the source code when rebuilt. Provides much faster builds but images are
  about 3 times bigger. Recommended for development purposes.
* `clean` removes old Docker images.
* `run_genesis` starts a new node with a new genesis block and.
* `run_genesis_bg` does the same but the node is started in daemonized mode.
* `run` and `run_bg` are similar to the above but do not create a new genesis block.
* `stop` stops the node running in the background.
* `docs` builds HTML documentation.
* `release` builds release-ready Docker compose files and appropriate configuration files.

## Build scripts

All build scripts are in the `build` directory.

* `build.sh` builds all required Docker images. `-r` flag is intended for release builds (used in
  `make build`)
* `clean.sh` removes old Docker images.
* `release.sh` builds release-ready Docker compose files and appropriate configuration files.
* `build-docs.sh` builds HTML documentation.

## scripts/run.sh

The script that allows you to run a REMME node. Following flags are provided:

* `-g` to run a node in genesis mode (to be used with `-u`)
* `-b` to run a node in background (to be used with `-u`)
* `-u` to start a node (default flag)
* `-d` to stop a node
