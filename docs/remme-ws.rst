REMME Core: Websocket
=====================

========
Overview
========

An application can subscribe to receive batches update via a web socket, provided by the WS component. For example, a single-page JavaScript application may open a web socket connection and subscribe to a particular batch, using the incoming events to re-render portions of the display.


====================
Opening a Web Socket
====================

The application developer must first open a web socket. This is accomplished by using standard means. In the case of in-browser JavaScript:

.. code-block:: javascript

    var ws = new WebSocket('ws:localhost:8080/ws')

****************************
Subscribing to Batch Changes
****************************

For retrieving an actual info about batches, it could be subscribed to this event. WS server will monitor all state changes for this batch and send event notification.

Example:

.. code-block:: javascript

      ws.send(JSON.stringify({
        type: 'request',
        action: 'subscribe',
        entity: 'batch_state',
        id: '1',
        parameters: {
            batch_ids: ['e96a5c43d9cabce9dab946ae81b0b2a02f93dd05280129aa92c42826ba137d5558576ca60d6624e25259572edfc00318f98947b8bfd7f57a78862910d06edace']
        }
      }));

On message:

.. code-block:: javascript

        {"type":"response","status":"subscribed","id":"1"}

********************************
Unsubscribing from Batch Changes
********************************

Removing the subscription of provided batches, WS server won't monitor their statuses after. Example:

.. code-block:: javascript

      ws.send(JSON.stringify({
        type: 'request',
        action: 'unsubscribe',
        entity: 'batch_state',
        id: '1',
        parameters: {
            batch_ids: ['e96a5c43d9cabce9dab946ae81b0b2a02f93dd05280129aa92c42826ba137d5558576ca60d6624e25259572edfc00318f98947b8bfd7f57a78862910d06edace']
        }
      }));

On message:

.. code-block:: javascript

        {"type":"response","status":"unsubscribed","id":"1"}


******
Events
******

Once subscribed, events will be received via the web socket’s onmessage handler. The event data is a JSON string, which looks like the following:

.. code-block:: javascript

        {
            "type":"message",
            "id":"1",
            "data":{
                "batch_statuses":{
                    "batch_id":"e96a5c43d9cabce9dab946ae81b0b2a02f93dd05280129aa92c42826ba137d5558576ca60d6624e25259572edfc00318f98947b8bfd7f57a78862910d06edace",
                    "status":"UNKNOWN",
                    "invalid_transactions":[

                    ]
                }
            }
        }

Fields description:

`batch_id`
    An id of a batch, which has an actual update

`status`
    Current status of a batch (https://github.com/hyperledger/sawtooth-core/blob/80f084f02960d59bcb220f3e99aad07cf1470588/protos/client_batch_submit.proto)

`invalid_transactions`
    List of invalid transactions occurred during validator procedure.


*****************
Available actions
*****************

`subscribe`
    Make a subscription of an entity

`unsubscribe`
    Make an unsubscription of an entity


******************
Available entities
******************

`batch_state`
    For retrieve/update of the batch


*****************
Response statuses
*****************

`subscribed`
    The subscription was succeed

`unsubscribed`
    The unsubscription was succeed

`malformed_json`
    Invalid JSON structure

`missing_action`
    Missing action key in the WS request message

`invalid_action`
    No such action defined in the protocol

`missing_id`
    Id missed in WS request message

`missing_parameters`
    Params missed in WS request message

`invalid_parameters`
    Parameters validation failed on WS server

`invalid_entity`
    Entity validation failed on WS server

`missing_entity`
    No such entity defined in the protocol

`missing_type`
    No such type defined in the protocol

`no_validator`
    Validator connection failed

`batch_response`
    Retrieved batch response