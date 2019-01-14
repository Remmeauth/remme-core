**************
Advanced guide
**************

Types of node running
=====================

On the first run, as any starter guide in this documentation follows, you need to initialize the genesis (first block)
block through ``./scripts/run.sh -g`` command, after that you haven't to do this and should run the node in default mode.

Also there are a bunch of flag, as ``-g`` you did, running script supports:

1. ``-g`` to run a node in genesis mode, so generate first block.
2. ``-b`` to run a node in background, so no output to the terminal window.
3. ``-u`` to start a node (default flag).
4. ``-d`` to stop a node if was run in background mode.
