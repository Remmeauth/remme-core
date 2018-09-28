REMME Core: RPC-API
====================

========
Overview
========
We are striving to simplify interaction with the REMchain by providing a common RPC and WebSocket architecture and formatting. There are several endpoints provided for managing the node and reading its state.

In order to start interacting with rpc api with an interface, you may need to `start the node locally <https://github.com/Remmeauth/remme-core>`_ and access the `generated RPC-API documentation <https://sawtooth.hyperledger.org/docs/core/releases/latest/introduction.html#private-networks-with-the-sawtooth-permissioning-features>`_.

RPC-API consists of several modules:

* `pkc` (public key certificate) module responsible for interaction with node and public keys
* `transaction` module implements communication through raw transactions for store and processing afterward on the chain
* `block_info` module related to fetching information about current block and histories
* `account` module shows address balance on REM-chain and list of public keys stored for the account address
* `network` provides info about peers and node sync
* `atomic_swap` show atomic swap info
* `state` shows entries for the current blockchain state


All communications with rpc api are going through `/ POST` or `WS` connection.

**Example of method RPC**


  *POST / Method `get_balance`*

  .. code-block:: json

    curl -X POST -H "Content-Type: application/json" --data '{"method":"get_balance","params":{"public_key": "026f65b58af77f04e964440adab165a4c4d9d8e99072d457254ebb0187facb0543"},"id":1,"jsonrpc":"2.0"}' http://127.0.0.1:8080

  .. code-block:: json

    {"jsonrpc": "2.0", "id": 1, "result": 1000000000000}
