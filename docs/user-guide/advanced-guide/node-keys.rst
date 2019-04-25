Node keys
=========

Until the admin panel does not cover all node's user requirements, there is an ability to fetch the node's private and public keys
manually to execute different operations such as an ``Atomic Swap``. Being logged in the server, use the following command to fetch
node's private key.

.. code-block:: console

   $ sudo cat /var/lib/docker/volumes/remme_validator_keys/_data/validator.priv

The command will show you the private key and you can copy it. The result is illustrated below.

.. image:: /img/user-guide/advanced-guide/node-private-key.png
   :width: 100%
   :align: center
   :alt: Get node private key

Do not share it for the security reasons. To fetch the public key and its address, use thee following command:

.. code-block:: console

   $ curl -X POST http://$NODE_IP_ADDRESS/rpc/ -H 'Content-Type: application/json' -d \
         '{"jsonrpc":"2.0","id":"11","method":"get_node_config","params":{}}' | python3 -m json.tool

The response should look similar to this:

.. code-block:: console

   {
       "jsonrpc": "2.0",
       "id": "11",
       "result": {
           "node_public_key": "02b844a10124aae7713e18d80b1a7ae70fcbe73931dd933c821b354f872907f7f3",
           "node_address": "116829caa6f35dddfd62d067607426407c95bf8dbc37fa55bcf734366df2e97cac660b"
       }
   }
