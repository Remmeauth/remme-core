REMME Client
=================

========
Overview
========

The main purpose of our client is to encapsulate low-level code and as the result to minimise worries of our contributors.

The client connects to Sawtooth-provided "**rest-api**" container which does all the communication with the **journal** (validator container)



There are few primary methods :code:`basic_client.py` consists of:

- :code:`make_address` and :code:`make_address_from_data` (from **handler**)
- :code:`send_transaction(self, method, data_pb, addresses_input_output)`
- :code:`get_value(self, key)`


=============
Custom client
=============

We encourage developers building Dapps on top of REMME protocol to create their own client to provide rest-api interface for their application.

For testing purposes and code reusability, we recommend to construct :code:`@classmethod`  functions that help validate fields and form proto objects for transaction payloads as such:

.. code-block:: python

    @classmethod
    def get_transfer_payload(self, address_to, value):
        if not is_valid(address_to) or not is_valid(value):
            raise Exception("Error")

        transfer = TransferPayload()
        transfer.address_to = address_to
        transfer.value = value

        return transfer

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





