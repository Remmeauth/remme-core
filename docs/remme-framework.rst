REMME Core: Framework
=====================

*************
Serialization
*************

When it comes to describing business entities and deterministically serialize our models, we use `Protobuf <https://github.com/google/protobuf>`_ - a language-neutral, platform-neutral, extensible mechanism for serializing structured data.

Transactions supplied to Transaction Processor(TP) have its own **payload** and are universally structured within REMME protocol as follows:

.. code-block:: java

    protos/transaction.proto

    message TransactionPayload {
        uint32 method = 1;
        bytes data = 2;
    }

Each **family** defines its own transaction types by using "Method" structure as such:

.. code-block:: java

    message TokenMethod {
        enum Method {
            TRANSFER = 0;
            GENESIS = 1;
        }
    }

.. note::

    It is important that enum is nested and contents are upper-cased.

.. note::

    REMME developer may generate protobuf python files by calling :code:`make build_protobuf`

=================
Naming convention
=================

There are 2 types of models that are primarily used in any blockchain protocol:

1. Transaction data.

2. Storage data

It is agreed to use "**Payload**" suffix for logical separation of **Transaction data** type.

********
Handlers
********

==============
Initialization
==============

It is very important to predefine FAMILY_NAME and a FAMILY_VERSIONS as such:

.. code-block:: python

    FAMILY_NAME = 'token'
    FAMILY_VERSIONS = ['0.1'] // helps to keep track of handler updates accross the network

and pass them to parent class :code:`basic_handler.py` as such:

.. code-block:: python

    def __init__(self):
        super().__init__(FAMILY_NAME, FAMILY_VERSIONS)

============
Architecture
============

From architecture description, you may have witnessed handler's possible actions.
However, we decided to limit developer and enforce functional philosophy in order to write high-quality transaction processors.

As a result, we provide you with an encapsulated :code:`basic_handler.py` that one inherits for own purposes of building a custom handler.

The key way to enable relevant transaction type processing is to provide a custom handler with a :code:`get_state_processor` method:

.. code-block:: python

    def get_state_processor(self):
        return {
            TokenMethod.TRANSFER: {
                'pb_class': TransferPayload,
                'processor': self._transfer
            }
        }

:code:`pb_class` - specifies a type of transaction payload.

:code:`processor` - function containing business logic on how to **verify** and **process** a new transaction.

=================
Address Formation
=================


.. note::

    Remember that address must be a **70** hex character long string represention.

There are few helper functions used in **handler** and **client** apps to form an address depending on namespace design you choose:

1. Given a 64 hex characters long suffix, we would like to append it to the prefix defined by our **family of addresses**:

.. code-block:: python

    def make_address(self, appendix):
        address = self._prefix + appendix
        if not is_address(address):
            raise InternalError('{} is not a valid address'.format(address))
        return address
2. Before we pass the suffix, we are likely to encode it from unique peace of data of an arbitrary size using hashing algorithm and pasing first 64 characters of the result:

.. code-block:: python

    def make_address_from_data(self, data):
        appendix = hashlib.sha512(data.encode('utf-8')).hexdigest()[:64]
        return self.make_address(appendix)

They can be found in :code:`basic_handler.py` - parent class of our custom handlers and are used across the project.

.. warning::

    It is important to have **1-1** unique mapping, otherwise, address **collision** may occur.

==================
Processor Function
==================

.. code-block:: python

    def _processor_function(self, context, signer_pubkey, deserialised_payload):
        if not is_valid(deserialised_payload):
            raise InvalidTransaction('Invalid transaction.')

        address1 = self.make_address_from_data(signer_pubkey)
        address2 = self.make_address(deserialised_payload.address_data)

        proto_model1 = get_data(context, ProtoModel, address1)
        proto_model2 = get_data(context, ProtoModel, address2)

        ...

        return {
            address1: proto_model1,
            address2: proto_model2,
        }


