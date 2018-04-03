REMME Core: Client
==================

========
Overview
========

The main purpose of our client is to encapsulate low-level code and as the result to minimise worries of our contributors.

The client connects to Sawtooth-provided "**rest-api**" container which does all the communication with the **journal** (validator container)



There are few primary methods :code:`basic_client.py` consists of:

- :code:`make_address` and :code:`make_address_from_data` (are provided and described in `handler section <./remme-framework.html#address-formation>`_)
- :code:`send_transaction(self, method, data_pb, addresses_input_output)` - responsible for sending transaction to **validator** (journal)
- :code:`get_value(self, key)` - retrieves value from the current synced journal storage.


=============
Custom client
=============

We encourage developers building Dapps on top of REMME protocol to create their own client in order to provide rest-api interface for their client application.

********************
Transaction Payloads
********************

For testing purposes and maximum code reusability, we recommend to construct :code:`@classmethod`  functions that help validate fields and form proto objects for transaction payloads as such:

.. code-block:: python

    @classmethod
    def get_transfer_payload(self, address_to, value):
        if not is_valid(address_to) or not is_valid(value):
            raise Exception("Error")

        transfer = TransferPayload()
        transfer.address_to = address_to
        transfer.value = value

        return transfer

*******************
Sending Transaction
*******************

:code:`_send_transaction(method,  protobuf_payload, addresses_input_output)` is designed to help client app in forming and sending transaction to a running validator (Journal).

:code:`method` - enum value specified per family transaction type.

:code:`protobuf_payload` - proto object that represents transaction payload.

:code:`addresses_input_output`:

In order to achieve the **parallel** execution architecture of our transactions, we would like to specify the **list of addresses** which your handlers will use to retrieve values from (:code:`inputs`) and save to (:code:`outputs`)  the state during the **transaction processing** step.

For simplicity of writing client code, we have decided to combine :code:`inputs` and :code:`outputs` into one list - :code:`addresses_input_output`, as we believe that Dapp developers are most likely to duplicate these lists as a result of their architecture.

*******
Example
*******
Example usage of :code:`send_transaction` and :code:`get_value`:

.. code-block:: python

    def transfer(self, address_to, value):
        addresses_input_output = [self.address_from, address_to]
        transfer = self.get_transfer_payload(address_to, value)

        status = self.send_transaction(TokenMethod.TRANSFER, transfer, addresses_input_output)
        return json.loads(status)

    def get_account(self, address):
        account = Account()
        account.ParseFromString(self.get_value(address))
        return account





