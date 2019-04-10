Node private key
================

Until the admin panel does not cover all node's user requirements, there is an ability to fetch the node's private key
manually to execute different operations such as an ``Atomic Swap``. Being logged in the server, use the following commands.

.. code-block:: console

   $ sudo cat /var/lib/docker/volumes/remme_validator_keys/_data/validator.priv

Then the last command will show you the private key and you can copy it. The result is illustrated below.

.. image:: /img/user-guide/advanced-guide/node-private-key.png
   :width: 100%
   :align: center
   :alt: Get node private key

Do not share it for the security reasons.
