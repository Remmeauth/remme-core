REMME Core
==========

|Jenkins| |Docker Stars| |Gitter|

REMME is a blockchain-based protocol used for issuing and management of public keys to resolve
issues related to cybersecurity, IoT connectivity, data integrity, digital copyright protection, transparency etc.

Remme core is built on Hyperledger Sawtooth platform, allowing to be flexible in language choice during the
development process.`Remme core exposes application programming interface based on RPC API.

Remme also supports `JS <https://github.com/Remmeauth/remme-client-js>`_ and `.NET <https://github.com/Remmeauth/remme-client-dotnet>`_
programming libraries that wraps its application programming interface, that’s why you to easily embed protocol in your project.

🔖 Documentation
----------------

🔖 `Architecture overview <https://youtu.be/fw3591g0hiQ>`_

🔖 `Docs & tutorials <https://docs.remme.io/>`_

🔖 `REMME use case for IoT
<https://blog.aira.life/blockchain-as-refinery-for-industrial-iot-data-873b320a6ff0>`_

🔖 `Blog <https://medium.com/remme>`_ & `talks <https://gitter.im/REMME-Tech>`_

How to build on REMME Core
--------------------------

1. REMChain is one of the components of our solution and a basic layer of our
   distributed Public Key Infrastructure — PKI(d) protocol. In a nutshell, it’s
   a multi-purpose blockchain that acts as a distributed storage for a
   certificate’s hash, state (valid or revoked), public key and expiration date.
2. Based on your needs, define what kind of information (e.g. multi-signature)
   REMME digital certificate will contain.
3. Choose how to integrate REMME:

.. list-table::
   :header-rows: 1

   * - Library
     - Repository
     - Version
   * - REMME JS SDK
     - `remme-client-js <https://github.com/Remmeauth/remme-client-js>`_
     - |npm|
   * - REMME .NET SDK
     - `remme-client-dotnet <https://github.com/Remmeauth/remme-client-dotnet>`_
     - |nuget|

4. Use REMME Testnet to check your ideas.
5. Discuss your integration concept in `REMME tech community
   <https://gitter.im/REMME-Tech>`_ or call for help if you need it.

API endpoints for public testnet
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We are striving to simplify interaction with the REMchain by providing a common
RPC and WebSocket architecture and formatting. There are several endpoints
provided for managing the node and reading its state.

In order to start interacting with RPC API with an interface, you may need to
start the node locally and access the generated `RPC-API documentation
<https://docs.remme.io/remme-core/docs/rpc-api.html>`_.

- https://node-genesis-testnet.remme.io
- https://node-1-testnet.remme.io
- https://node-2-testnet.remme.io
- https://node-3-testnet.remme.io
- https://node-4-testnet.remme.io

Getting started with your own node
----------------------------------

The node was tested on Linux and macOS. Running on Windows may require
significant modification of startup scripts.

Currently it is not possible to connect your own node to the test network. All
nodes you will run will work on your own network.

Prerequisites
~~~~~~~~~~~~~

- `Docker Compose <https://docs.docker.com/compose/install/>`_ (17.09.0+)
- Docker (compatible with your Docker Compose)

For an end-user
~~~~~~~~~~~~~~~

#. Download the latest release from
   `Releases <https://github.com/Remmeauth/remme-core/releases>`_ section
   (``<version_number>-release.zip``). Unpack it.
#. Start node: Open a terminal inside the unpacked folder and run
   ``./run.sh``.
#. You can now use our RPC API. By default it is started on
   http://localhost:8080. The API port can be changed in
   ``config/network-config.env`` file.

On the first run you will need to initialize the genesis block. To make
that just run ``./run.sh -g``. This will generate a new key pair and
genesis block.

Flags available for ``run.sh`` are:

- ``scripts/run.sh`` features a single entrypoint to run a project with the
   following flags:
  
  - ``-g`` to run a node in genesis mode
  - ``-b`` to run a node in background
  - ``-u`` to start a node (default flag)
  - ``-d`` to stop a node

For developers & contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Clone this repository to your machine:
``git clone https://github.com/Remmeauth/remme-core.git``

When you have this repository cloned go the project directory and run

#. ``make build_dev`` (``make build`` for more compact but slower builds)
#. ``make run_genesis`` or ``make run`` if you are working on an existing chain.

**NOTE:** on further runs you might want to run ``make run`` to persist the
transaction created before. If you want to start with a clean chain, use ``make
run_genesis`` again.

You can run ``make test`` to run automated tests.

Building documentation
----------------------

Prerequesites for building the documentation are ``sphinx`` and
``sphinx_rtd_theme``. You can build the documentation with ``make docs``
command.

License
-------

REMME software and documentation are licensed under `Apache License Version 2.0
<LICENCE>`_.

.. |Docker Stars| image:: https://img.shields.io/docker/stars/remme/remme-core.svg
   :target: https://hub.docker.com/r/remme/remme-core/
.. |Gitter| image:: https://badges.gitter.im/owner/repo.png
   :target: https://gitter.im/REMME-Tech
.. |npm| image:: https://img.shields.io/npm/v/remme.svg
   :target: https://www.npmjs.com/package/remme
.. |nuget| image:: https://img.shields.io/nuget/v/REMME.Auth.Client.svg
   :target: https://www.nuget.org/packages/REMME.Auth.Client/
.. |Jenkins| image:: https://jenkins.remme.io/buildStatus/icon?job=remme-core/dev
   :target: https://jenkins.remme.io/view/1.GitHub_Integration/job/remme-core/job/dev/
