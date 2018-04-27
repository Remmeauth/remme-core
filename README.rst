REMME Core
==========

|CircleCI| |Docker Stars|

**This is an alpha version! It is not suitable for any use in production
and is intended to demonstrate capabilities of Hyperledger Sawtooth in
the scope of REMME.**

How to run
----------

You will need Docker and Docker Compose installed on your machine.

For an end-user
~~~~~~~~~~~~~~~

1. Download the latest release from `Releases`_ section
   (``<version_number>-release.zip``). Unpack it.
2. Start node: Open a terminal inside the unpacked folder and run
   ``./run.sh``.
3. You can now use our REST API. By default it is started on http://localhost:8080. Fancy Swagger UI
   with documentation is available on http://localhost:8080/api/v1/ui. The API port can be changed in
   `.env` file.

On the first run you will need to initialize the genesis block. To make
that just run ``./genesis.sh``. This will generate a new key pair and
genesis block.

For developers & contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Clone this repository to your machine:
``git clone https://github.com/Remmeauth/remme-core.git``

When you have this repository cloned go the project directory run the
following commands:

-  ``make build_docker``
-  ``make run_dev``

You can run ``make test`` to run automated tests.

License
-------

REMME software and documentation are licensed under `Apache License Version 2.0 <LICENCE>`_.

.. _Releases: https://github.com/Remmeauth/remme-core/releases

.. |CircleCI| image:: https://img.shields.io/circleci/project/github/Remmeauth/remme-core.svg
   :target: https://circleci.com/gh/Remmeauth/remme-core
.. |Docker Stars| image:: https://img.shields.io/docker/stars/remme/remme-core.svg
   :target: https://hub.docker.com/r/remme/remme-core/
