REMME Core
==========

|CircleCI| |Docker Stars|

How to run a node
-----------------

The node was tested on Linux and macOS. Running on Windows may require
significant modification of startup scripts.

Currently it is not possible to connect your own node to the test network. All
nodes you will run will work on your own network.

You will need Docker and Docker Compose installed on your machine.

For an end-user
~~~~~~~~~~~~~~~

#. Download the latest release from `Releases`_ section
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
  - ``-l`` to perform all of the above operations on log.io

For developers & contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Clone this repository to your machine:
``git clone https://github.com/Remmeauth/remme-core.git``

When you have this repository cloned go the project directory and run

#. ``make build_dev`` (``make build`` for more compact but slower builds)
#. ``make run_genesis`` or ``make run`` if you are working on an existing chain.

Detailed instructions are available in `BUILD.md <BUILD.md>`_

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

.. _Releases: https://github.com/Remmeauth/remme-core/releases

.. |CircleCI| image:: https://img.shields.io/circleci/project/github/Remmeauth/remme-core.svg
   :target: https://circleci.com/gh/Remmeauth/remme-core
.. |Docker Stars| image:: https://img.shields.io/docker/stars/remme/remme-core.svg
   :target: https://hub.docker.com/r/remme/remme-core/
