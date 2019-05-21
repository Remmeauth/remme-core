Upgrade the node
================

This section describes how to upgrade the node to latest version. After upgrade you are required to redo login
to the server if you want to execute commands farther.

From 0.10.0-alpha to 0.11.0-alpha
---------------------------------

To upgrade from the version ``0.10.0-alpha`` to the version ``0.11.0-alpha``, use the following command on the server:

.. code-block:: console

   $ curl https://gist.githubusercontent.com/dmytrostriletskyi/7407898a9737d5808716ea3b0f3d6f75/raw/a4e16a99efa95ead90b7c6052b30925f11c89941/upgrade-node-from-0.10.0a-to-0.11.0a.sh > ~/upgrade-node-from-0.10.0a-to-0.11.0a.sh && \
         chmod +x ~/upgrade-node-from-0.10.0a-to-0.11.0a.sh && \
         ~/./upgrade-node-from-0.10.0a-to-0.11.0a.sh 0.10.0-alpha 0.11.0-alpha $NODE_IP_ADDRESS

From 0.9.1-alpha to 0.10.0-alpha
--------------------------------

To upgrade from the version ``0.9.1-alpha`` to the version ``0.10.0-alpha``, use the following command on the server:

.. code-block:: console

   $ curl https://gist.githubusercontent.com/dmytrostriletskyi/ddb0d8fc16512523f4942a2d60b57c63/raw/63de05cc7f68801bb6887fc07463422810276a10/upgrade-node.sh > ~/upgrade-node.sh && \
         chmod +x ~/upgrade-node.sh && \
         ~/./upgrade-node.sh 0.9.1-alpha 0.10.0-alpha

From 0.9.0-alpha to 0.9.1-alpha
-------------------------------

To upgrade from the version ``0.9.0-alpha`` to the version ``0.9.1-alpha``, use the following command on the server:

.. code-block:: console

   $ curl https://gist.githubusercontent.com/dmytrostriletskyi/ddb0d8fc16512523f4942a2d60b57c63/raw/63de05cc7f68801bb6887fc07463422810276a10/upgrade-node.sh > ~/upgrade-node.sh && \
         chmod +x ~/upgrade-node.sh && \
         ~/./upgrade-node.sh 0.9.0-alpha 0.9.1-alpha

From 0.8.1-alpha to 0.9.0-alpha
-------------------------------

To upgrade from the version ``0.8.1-alpha`` to the version ``0.9.0-alpha``, use the following command on the server:

.. code-block:: console

   $ curl https://gist.githubusercontent.com/dmytrostriletskyi/ddb0d8fc16512523f4942a2d60b57c63/raw/63de05cc7f68801bb6887fc07463422810276a10/upgrade-node.sh > ~/upgrade-node.sh && \
         chmod +x ~/upgrade-node.sh && \
         ~/./upgrade-node.sh 0.8.1-alpha 0.9.0-alpha
