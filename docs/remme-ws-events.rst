*******************
Events Subscription
*******************

Overview
========

For a client app in order to be notified when the transaction occurs on the network is to be subscribed to it using WebSocket event services we provide.
There are two layers that an emitting event goes through before being delivered to a client side:

* transaction processor - that emits transaction data upon consensus's confirmation
* websocket service - middleware that subscribes to the node and formats event data upon retrieval.

.. note::
 `REMME Javascript client <https://github.com/Remmeauth/remme-client-js>`_ encapsulates some low-level interaction for ones convenience.

Adding a new event
==================

Before registering the event withing a transaction processor, one needs to create it's name as such at `remme/ws/constants.py`:

.. code-block:: python

 @unique
 class Events(Enum):
    ...
    SWAP_INIT = 'atomic-swap-init'
    ...

Afterwards, to opt-in transaction processor method, it is enough to add a line in existing `get_state_processor`.

.. code-block:: python

 from remme.ws.basic import EMIT_EVENT
 from remme.ws.constants import Events

 ...

 class CustomHandler(BasicHandler):

    ...

    def get_state_processor(self):
         return {
             AtomicSwapMethod.INIT: {
             'pb_class': AtomicSwapInitPayload,
             'processor': self._swap_init,
             EMIT_EVENT: Events.SWAP_INIT.value <=== add this line
         }

Events socket subscription
==========================

Connecting to node
------------------
Client may connect to a node using `ws://localhost:8080/ws/events` gateway.

Subscribe to events
-------------------

To start receiving new events, we need to send a message where we provide the list of transaction processors to subscribe to as we defined from above using `EMIT_EVENT`.

Here is an example of the message:

.. code-block:: json

 {
    "action": "subscribe",
    "data": {
        "entity": "events",
        "events": ["atomic-swap-init","account-transfer"] // list of events to subscribe to.
     }
 }

Unsubscribe from events
-----------------------

One can only unsubscribe from all events at once at this point, as such:

.. code-block:: json

 {
    "action": "unsubscribe",
    "data": {
        "entity": "events"
     }
 }

Possible actions
----------------

.. list-table::
   :widths: 8, 50
   :header-rows: 1

   * - Action
     - Description
   * - subscribe
     - Subscribes to the specified type of messages and list of events. Requires `entity` and `events` provided.
   * - unsubscribe
     - Unsubscribes from all events at once.

Registered events
-----------------

.. list-table::
   :widths: 8, 50
   :header-rows: 1

   * - Key
     - Value
   * - SWAP_INIT
     - atomic-swap-init
   * - SWAP_CLOSE
     - atomic-swap-close
   * - SWAP_APPROVE
     - atomic-swap-approve
   * - SWAP_EXPIRE
     - atomic-swap-expire
   * - SWAP_SET_SECRET_LOCK
     - atomic-swap-set-secret-lock
   * - ACCOUNT_TRANSFER
     - account-transfer

Event Catch Up
--------------

In order to receive event meesages starting from historical block, the block id needs to be provided as such:

.. code-block:: json

 {
    "action": "subscribe",
    "data": {
        "entity": "events",
        "events": ["atomic-swap-init","account-transfer"],
        "last_known_block_id": "..." // <== add this field
     }
 }

.. note::

 After providing historical events it will keep client subscribed for the latest ones.

Responses
---------

The successful response provides the following format:

.. code-block:: json

 {
    "type": "status",
    "data": {
        "status": 10
    }
 }

Possible types are:

.. list-table::
   :widths: 8, 50
   :header-rows: 1

   * - Type
     - Description
   * - status
     - Informs of a successful execution of the request and the status indicates your connection state.
   * - error
     - Indicates that something went wrong where status points out what the error is.


Status codes
------------

.. list-table::
   :widths: 4, 16, 60
   :header-rows: 1

   * - Code
     - Title
     -
   * - 10
     - SUBSCRIBED
     -
   * - 11
     - UNSUBSCRIBED
     -
   * - 100
     - MALFORMED_JSON
     -
   * - 101
     - MISSING_ACTION
     -
   * - 102
     - INVALID_ACTION
     -
   * - 103
     - MISSING_ID
     -
   * - 104
     - MISSING_PARAMETERS
     -
   * - 105
     - INVALID_PARAMS
     -
   * - 106
     - INVALID_ENTITY
     -
   * - 107
     - MISSING_ENTITY
     -
   * - 108
     - MESSAGE_ID_EXISTS
     -
   * - 109
     - MISSING_TYPE
     -
   * - 110
     - NO_VALIDATOR
     -
   * - 111
     - MISSING_DATA
     -
   * - 112
     - WRONG_EVENT_TYPE
     -
   * - 113
     - ALREADY_SUBSCRIBED
     -
   * - 114
     - EVENTS_NOT_PROVIDED
     -
   * - 115
     - LAST_KNOWN_BLOCK_ID_NOT_PROVIDED
     -
   * - 116
     - UNKNOWN_BLOCK
     -
   * - 200
     - BATCH_RESPONSE
     -

Event Message Contents
----------------------
Every event has a universal format that may be altered by middleware event processing layer.
The main content for th event is taken from the satte change that a transaction caused, hence providing all information one may be interested regarding the transaction and its entities.
The format provided looks as following:

.. code-block:: json

 {
    "type": "message",
    "data": {
        "events": [
            {
                "type": "account-transfer",
                "transaction_id": "2f28ee5136dc0f9704e97b2d7bc8a1e7f845c14615555f920e175f04c061c9e950bd95f53232486f3dd36b1604353fb320c8b417e80178357dc05cbfde3d9502",
                "data":[
                    {
                        "address": "1120072651235da4c144f85e7c06820312c46e5c83e64e7e0273d5891e196ebd4c3b97",
                        "type": "Account",
                        "balance":"999999999900",
                        "pub_keys":[]
                    },
                    {
                        "address": "112007fd86a7c8b642c9695f461b956405837ac12af1e282beec1777c8e55c5e03a767",
                        "type":"Account",
                        "balance":"100",
                        "pub_keys":[]
                    }
                ]
            }
        ],
        "block_num": 1,
        "block_id": "4477af7f6bc2c078e2ccbc97610e6b98ab21401ecbd2e8927f8289ce3b655e00466cbeafcb1f496f5ace473936ff2bc06de061a04b456547463ddc48fd0dcac7"
    }
 }

.. note::

 The format transferred from the transaction processor is universal and any custom formatting may be added specified in `remme/ws/events.py` at `process_event(type, attributes)`.h