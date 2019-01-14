**************
Advanced guide
**************

Types of node running
=====================

As stated in our guides, during the first run, you need to initialize the genesis (first block on the blockchain)
block with a command ``./scripts/run.sh -g``. Next runs should be run with ``-d`` flag.

Also there is a bunch of flag, as ``-g`` you did, running script supports:

1. ``-g`` to run a node in genesis mode, so generate first block.
2. ``-b`` to run a node in background, so no output to the terminal window.
3. ``-u`` to start a node (default flag).
4. ``-d`` to stop a node if was run in background mode.
