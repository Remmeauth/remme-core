Types of node running
=====================

Use the following commands to manage your node:

1. ``make stop`` to stop the running node.
2. ``make run`` to start a node not in the background mode.
3. ``make run_bg`` to start a node in the background mode.

Background mode means that after executing a command you won't get any output (node's log) in the terminal and when you
exit from the server, the node will continue working. If you do not run the node in the background mode, when you exit
the server, the node will be stopped.

To perform the commands, please log in to your server first. Then use the following command.

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
