Types of node running
=====================

As stated in our guides, during the first run, you need to initialize the genesis block (first block on the blockchain)
with a command ``make run_genesis_bg`` that have run your node in background mode (no output to the terminal window).

There is also a bunch of commands, similar to those you performed with ``make run_genesis_bg``:

1. ``make stop`` to stop the node.
2. ``make run_genesis`` to run a node in genesis mode, not in the background.
3. ``make run`` to start a node if you’re not starting it for the first time; first time start should be a genesis.
4. ``make run_bg`` the same as the command above, but to run the node in background mode.

To perform them, please login to your server first. Then use the following command.

.. code-block:: console

   $ cd /home/remme-core-$REMME_CORE_RELEASE

Now you can execute the command from the list above. You need to add ``sudo`` at the start of the command.

.. code-block:: console

   $ sudo make stop

After executing the command your should wait it is completely executed (green ``done``). The you can execute the next one.

.. image:: /img/user-guide/troubleshooting/commands-response.png
   :width: 100%
   :align: center
   :alt: Command is completely executed
