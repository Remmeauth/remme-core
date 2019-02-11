**************
Advanced guide
**************

Types of node running
=====================

As stated in our guides, during the first run, you need to initialize the genesis (first block on the blockchain)
block with a command ``make run_genesis_bg`` that have run your node in the background mode (no output to the terminal window).

Also there is a bunch of commands, as ``make run_genesis_bg`` you did:

1. ``make stop`` to stop the node.
2. ``make run_genesis`` to run a node in genesis mode not in background.
3. ``make run`` to start a node if you start it not first time, first time start should be a genesis.
4. ``make run_bg`` the same as command above, but run the node in background mode.
