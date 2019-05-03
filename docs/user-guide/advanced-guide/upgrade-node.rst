Upgrade the node
================

This section describes how to upgrade the node to latest version. After upgrade you are required to redo login
to the server if you want to execute commands farther.

From 0.9.0-alpha to 0.9.1-alpha
-------------------------------

From upgrade from the version ``0.9.0-alpha`` to the version ``0.9.1-alpha``, use the following command on the server:

.. code-block:: console

   $ curl https://gist.githubusercontent.com/dmytrostriletskyi/ddb0d8fc16512523f4942a2d60b57c63/raw/63de05cc7f68801bb6887fc07463422810276a10/upgrade-node.sh > ~/upgrade-node.sh && \
         chmod +x ~/upgrade-node.sh && \
         ~/./upgrade-node.sh 0.9.0-alpha 0.9.1-alpha

From 0.8.1-alpha to 0.9.0-alpha
-------------------------------

From upgrade from the version ``0.8.1-alpha`` to the version ``0.9.0-alpha``, use the following command on the server:

.. code-block:: console

   $ curl https://gist.githubusercontent.com/dmytrostriletskyi/ddb0d8fc16512523f4942a2d60b57c63/raw/63de05cc7f68801bb6887fc07463422810276a10/upgrade-node.sh > ~/upgrade-node.sh && \
         chmod +x ~/upgrade-node.sh && \
         ~/./upgrade-node.sh 0.8.1-alpha 0.9.0-alpha
