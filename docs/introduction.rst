************
Introduction
************

Overview
========

``Remme`` is a blockchain-based protocol used for issuing and management of public keys to resolve issues
related to cybersecurity, IoT connectivity, data integrity, digital copyright protection, transparency etc.

``Remme core`` is built on Hyperledger Sawtooth platform, allowing to be flexible in language choice during the
development process. ``Remme core`` exposes application programming interface based on :doc:`/apis/rpc` and
:doc:`/apis/ws` API.

How to build on REMME Core
==========================

``Remme`` supports the following programming libraries that wrap its application programming interface, so that you could
easily embed the protocol in your project.

.. list-table::
   :header-rows: 1

   * - Library
     - Repository
     - Version
   * - Javascript SDK
     - `remme-client-js <https://github.com/Remmeauth/remme-client-js>`_
     - |npm|
   * - .NET SDK
     - `remme-client-dotnet <https://github.com/Remmeauth/remme-client-dotnet>`_
     - |nuget|
   * - Java SDK
     - `remme-client-java <https://github.com/Remmeauth/remme-client-dotnet>`_
     - |maven|

You could discuss your integration concept in the `technical community in Gitter <https://gitter.im/REMME-Tech>`_.

.. |npm| image:: https://img.shields.io/npm/v/remme.svg
   :target: https://www.npmjs.com/package/remme

.. |nuget| image:: https://img.shields.io/nuget/v/REMME.Auth.Client.svg
   :target: https://www.nuget.org/packages/REMME.Auth.Client/

.. |maven| image:: https://img.shields.io/maven-central/v/io.remme.java/remme-java-lib.svg
   :target: https://mvnrepository.com/artifact/io.remme.java/remme-java-lib

Public testnet nodes list
=========================

To simplify the interaction with the ``REMchain`` we provide a common ``RPC`` and ``WebSocket``
architecture and formatting. There are several endpoints provided for managing the node and reading its state.

Here the nodes available for communication:

1. |node_genesis|
2. |node_1|
3. |node_2|
4. |node_3|
5. |node_4|

.. |node_genesis| raw:: html

   <a href="https://node-genesis-testnet.remme.io" target="_blank">https://node-genesis-testnet.remme.io</a>

.. |node_1| raw:: html

   <a href="https://node-1-testnet.remme.io" target="_blank">https://node-1-testnet.remme.io</a>

.. |node_2| raw:: html

   <a href="https://node-2-testnet.remme.io" target="_blank">https://node-2-testnet.remme.io</a>

.. |node_3| raw:: html

   <a href="https://node-3-testnet.remme.io" target="_blank">https://node-3-testnet.remme.io</a>

.. |node_4| raw:: html

   <a href="https://node-4-testnet.remme.io" target="_blank">https://node-4-testnet.remme.io</a>

It is okay if you see ``This site can’t be reached``, node just doesn't have an interface.

References
==========

Also check out the following project-related pages:

1. Architecture overview — |architecture_overview|
2. Documentation and tutorials — |documentation_and_tutorials|
3. Use case for IoT — |use_cases_for_iot|
4. Blog on Medium — |blog_on_the_medium|
5. Gitter channel — |gitter_channel|

.. |architecture_overview| raw:: html

   <a href="https://youtu.be/fw3591g0hiQ" target="_blank">https://youtu.be/fw3591g0hiQ</a>

.. |documentation_and_tutorials| raw:: html

   <a href="https://docs.remme.io" target="_blank">https://docs.remme.io</a>

.. |use_cases_for_iot| raw:: html

   <a href="https://blog.aira.life/blockchain-as-refinery-for-industrial-iot-data-873b320a6ff0" target="_blank">https://blog.aira.life/blockchain-as-refinery-for-industrial-iot-data-873b320a6ff0</a>

.. |blog_on_the_medium| raw:: html

   <a href="https://medium.com/remme" target="_blank">https://medium.com/remme</a>

.. |gitter_channel| raw:: html

   <a href="https://gitter.im/REMME-Tech" target="_blank">https://gitter.im/REMME-Tech</a>
