************
Introduction
************

Overview
========

``Remme`` is a blockchain-based protocol used for issuing and management of public keys to resolve issues
related to cybersecurity, IoT connectivity, data integrity, digital copyright protection, transparency etc.

``Remme core`` is built on Hyperledger Sawtooth platform, allowing to be flexible in language choice during the
development process. ``Remme core`` exposes application programming interface based on :doc:`/rpc-api`.

``Remme`` also supports |js_client_library| and |dotnet_client_library| programming libraries that wraps its application programming interface,
that’s why you to easily embed protocol in your project.

.. |js_client_library| raw:: html

   <a href="https://github.com/Remmeauth/remme-client-js" target="_blank">JavaScript</a>

.. |dotnet_client_library| raw:: html

   <a href="https://github.com/Remmeauth/remme-client-dotnet" target="_blank">.NET</a>

Public tesnet nodes list
========================

We are striving to simplify interaction with the ``REMchain`` by providing a common ``RPC`` and ``WebSocket``
architecture and formatting. There are several endpoints provided for managing the node and reading its state.

Below the list of available nodes to communicate with are presented:

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

Technical requirements
======================

1. ``Docker`` (18.0.0+) and ``Docker Compose`` (17.09.0+).
2. Unix system such as ``MacOS``, ``Linux`` for :doc:`/user-guide/local` and :doc:`/user-guide/cloud`, with ``Windows`` :doc:`/user-guide/cloud` is possible only.
3. At least 2GB hard drive storage available.
4. At least 1GB RAM.
5. Machine’s time settings are up to date.

References
==========

Also the following references you may be interested in:

1. Architecture overview — |architecture_overview|
2. Documentation and tutorials. — |documentation_and_tutorials|
3. Use case for IoT — |use_cases_for_iot|
4. Blog on the Medium — |blog_on_the_medium|
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
