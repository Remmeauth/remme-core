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
* `personal` allow to work with node configurations (private keys etc.)


All communications with rpc api are going through `/ POST` or `WS` connection.


======================
JSON RPC error codes
======================
Base JSON RPC errors taken from spec https://www.jsonrpc.org/specification, but also has own custom codes.

+------------+----------------------------------+------------------------------------------------------+
|    Code    | Possible Return message          | Description                                          |
+============+==================================+======================================================+
|   -32700   |   Parse error                    |   Invalid JSON was received by the server. An error  |
|            |                                  |   occurred on the server while parsing the JSON text |
+------------+----------------------------------+------------------------------------------------------+
|   -32600   |   Invalid Request                |   The JSON sent is not a valid Request object        |
+------------+----------------------------------+------------------------------------------------------+
|   -32601   |   Method not found               |   The method does not exist / is not available.      |
+------------+----------------------------------+------------------------------------------------------+
|   -32602   |   Invalid params                 |   Invalid method parameter(s)                        |
+------------+----------------------------------+------------------------------------------------------+
|   -32603   |   Internal error                 |   Internal JSON-RPC error                            |
+------------+----------------------------------+------------------------------------------------------+
|   -32001   |   Resource not found             |   Some resource by identifier not found on chain     |
+------------+----------------------------------+------------------------------------------------------+
|   -32002   |   Validator is not ready yet     |   Validator is not prepared for handling of requests |
+------------+----------------------------------+------------------------------------------------------+
|   -32003   |   Invalid or missing header      |   Wrong header for validator request                 |
+------------+----------------------------------+------------------------------------------------------+
|   -32004   |   Invalid or missing resource id |   Wrong id for some resource                         |
+------------+----------------------------------+------------------------------------------------------+
|   -32005   |   Invalid limit count            |   Wrong limit count for resource                     |
+------------+----------------------------------+------------------------------------------------------+


======================
JSON RPC API Reference
======================

| **send_raw_transaction**

| Submit a transaction to the node

*Parameters*

* data - base64 of serialized transaction protobuf

*Returns*

* the id of the batch the transaction was included into

| **get_node_config**

| Submit a transaction to the node

*Parameters*

* none

*Returns*

* node_public_key - the public key of a node
* storage_public_key - the public key for storage of tokens

| **get_batch_status**

| Get current batch status from the node

*Parameters*

* batch_id - the id of a batch to check

*Returns*

* status

| **get_block_number**

| Get latest block number

*Parameters*

* none

*Returns*

* the number of blocks present on this node

| **get_blocks**

| Get blocks from the node

*Parameters*

* start (default: 0) - the number of the block to start with

* limit (default: 0) - the number of the last block

*Returns*

`array of structures`

* block_number - the number of the block
* timestamp
* previous_header_signature
* signer_public_key
* header_signature

| **set_node_key**

| Set new private key for node sender

*Parameters*

* private_key - the private key this node should operate

*Returns*

* true | false

| **export_node_key**

| Show current private key of node

*Parameters*

* none

*Returns*

* private key

| **get_balance**

| Show balance for some public key

*Parameters*

* public_key_address - the address of a key on REMchain

*Returns*

* current amount of tokens on user's account

| **get_public_keys_list**

| Show list of public keys stored on an address

*Parameters*

* public_key_address - the address of a key on REMchain

*Returns*

* addresses of public keys on remchain

| **get_public_key_info**

| Show info of some public key

*Parameters*

* public_key_address - the address of a key on REMchain

*Returns*

* is_revoked
* owner_public_key
* valid_from
* valid_to
* is_valid
* entity_hash
* entity_hash_signature

| **get_atomic_swap_info**

| Show info of atomic swap request

*Parameters*

* swap_id

*Returns*

* state
* sender_address
* sender_address_non_local
* receiver_address
* amount
* email_address_encrypted_optional
* swap_id
* secret_lock
* secret_key
* created_at
* is_initiator

| **get_atomic_swap_public_key**

| Show public key for atomic swap

*Parameters*

* none

*Returns*

* A public key with which to enсrypt sensitive data during the swap. (e.g email address)

| **get_node_info**

| Show node info

*Parameters*

* none

*Returns*

* is_synced - status for node sync with actual blocks
* peer_count - count of connected peers

| **list_batches**

*Parameters*

* ids (array, optional)
* start (string, optional)
* limit (integer, optional)
* head (string, optional)
* reverse (string, optional)

*Returns*

https://sawtooth.hyperledger.org/docs/core/releases/latest/rest_api/endpoint_specs.html#get--batches

| **fetch_batch**

*Parameters*

* id (string)

*Returns*

https://sawtooth.hyperledger.org/docs/core/releases/latest/rest_api/endpoint_specs.html#get--batches-batch_id

| **list_transactions**

*Parameters*

* ids (array, optional)
* start (string, optional)
* limit (integer, optional)
* head (string, optional)
* reverse (string, optional)

*Returns*

https://sawtooth.hyperledger.org/docs/core/releases/latest/rest_api/endpoint_specs.html#get--transactions

| **fetch_transaction**

*Parameters*

* id (string)

*Returns*

https://sawtooth.hyperledger.org/docs/core/releases/latest/rest_api/endpoint_specs.html#get--transactions-transaction_id

| **list_blocks**

*Parameters*

* ids (array, optional)
* start (string, optional)
* limit (integer, optional)
* head (string, optional)
* reverse (string, optional)

*Returns*

https://sawtooth.hyperledger.org/docs/core/releases/latest/rest_api/endpoint_specs.html#get--blocks

| **fetch_block**

*Parameters*

* id (string)

*Returns*

https://sawtooth.hyperledger.org/docs/core/releases/latest/rest_api/endpoint_specs.html#get--blocks-block_id

| **list_state**

*Parameters*

* address (string, optional)
* start (string, optional)
* limit (integer, optional)
* head (string, optional)
* reverse (string, optional)

*Returns*

https://sawtooth.hyperledger.org/docs/core/releases/latest/rest_api/endpoint_specs.html#get--state

| **fetch_state**

*Parameters*

* address (string)
* head (string, optional)

*Returns*

https://sawtooth.hyperledger.org/docs/core/releases/latest/rest_api/endpoint_specs.html#get--state-address

| **list_receipts**

*Parameters*

* ids (array)

*Returns*

https://sawtooth.hyperledger.org/docs/core/releases/latest/rest_api/endpoint_specs.html#get--receipts

| **fetch_peers**

*Parameters*

* none

*Returns*

https://sawtooth.hyperledger.org/docs/core/releases/latest/rest_api/endpoint_specs.html#get--peers