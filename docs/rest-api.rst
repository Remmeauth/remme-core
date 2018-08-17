REMME Core: REST-API
====================

========
Overview
========
We are striving to simplify interaction with the REMchain by providing a common REST and WebSocket architecture and formatting. There are several endpoints provided for managing the node and reading its state.

In order to start interacting with rest api with an interface, you may need to `start the node locally <https://github.com/Remmeauth/remme-core>`_ and access the `generated REST-API documentation <https://sawtooth.hyperledger.org/docs/core/releases/latest/introduction.html#private-networks-with-the-sawtooth-permissioning-features>`_.

REST-API consists of several sections:

 `Default <http://localhost:8080/api/v1/ui/#/default>`_ section - responsible for generic endpoints available to interact with a chain.

 `Node Management <http://localhost:8080/api/v1/ui/#/Node_management>`_ section - responsible for managing public keys within the node.

 `Token Operations <http://localhost:8080/api/v1/ui/#/Node_management>`_ section - allows one to retrieve information regarding account and transfer tokens.

 `Public Key Infrastructure <http://localhost:8080/api/v1/ui/#/Node_management>`_ section - Unlike node management tools, it allows storing public key information on-chain.

 `X.509 <http://localhost:8080/api/v1/ui/#/Node_management>`_ section - Allows storing certificate information.

**Example Request**

*GET /block-info*

Description: Gets the list of blocks within the blockchain storage.

Arguments:

* start (query) - return the list starting from the given number.
* limit (query) - return a certain number of blocks

200:

.. code-block:: json

  {
    "blocks": [
      {
        "block_num": 0,
        "header_signature": "string",
        "previous_header_signature": "string",
        "signer_public_key": "string",
        "timestamp": 0
      }
    ]
  }

500:
Error processing this request

.. code-block:: json

  {
    "error": "string"
  }
