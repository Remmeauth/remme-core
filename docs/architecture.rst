Node Architecture
=================

Each node consists of 2 main logical components:

- `Journal <https://sawtooth.hyperledger.org/docs/core/releases/latest/architecture/journal.html>`_ - responsible for consensus mechanism, storage and networking.

- Transaction Processor - business logic on how to process a new transaction.

(we have agreed within a team to refer to "Journal" container as a "Validator")

.. figure:: img/journal_organization.svg

   This image by `Intel Corporation <https://www.intel.com/>`_ is licenced under
   `CC BY 4.0 <https://creativecommons.org/licenses/by/4.0/>`_

We will not elaborate on "Journal" construct, you can read more from `the official site <https://sawtooth.hyperledger.org/docs/core/releases/latest/architecture/journal.html>`_.

************
Global State
************

Before we dive into **Transaction Processor**'s description, we need to keep in mind how our blockchain stores and ensures consistency of our data across many nodes.

The following primitive data storage system is used based on **Radix Merkle Tree**:


*Address* => *Data*

==========================
Radix Addresses
==========================

One can find a detailed description of **Radix Merkle Tree** from `the official website <https://sawtooth.hyperledger.org/docs/core/releases/latest/architecture/global_state.html#merkle-hashes>`_
or `Wikipedia <https://en.wikipedia.org/wiki/Merkle_tree>`_

We are more interested in how one forms an **address** (a hex-encoded **70** character string representing 35 bytes).

.. figure:: img/state_address_format.svg
   This image by `Intel Corporation <https://www.intel.com/>`_ is licenced under
   `CC BY 4.0 <https://creativecommons.org/licenses/by/4.0/>`_

In order to uniquely define the parts of the tree where information is stored, a namespace prefix is suggested which consists of 3 bytes (**6** hex characters). The remaining 32 bytes (**64** hex characters) are encoded based on the specifications of the designer of the namespace.

A namespace prefix defines a **family** (which is described in **handler**) that helps process relevant transactions provided **address reference** to a given **family address**.
It is worth to note that **family** may have **many** prefixes.

.. warning:: When it comes to serialisation and deserialisation, make sure to use **deterministic** approach to storing data across the network. At REMME we use **protobuf** which is described later.

**************************
Transaction Processor (TP)
**************************

TP may consist of several **Transaction Handlers** which contain business logic on how to process a certain **family** of a transactions.

We have inherited and encapsulated **TransactionHandler** logic with a shared class basic_handler.py for developer's convenience.
