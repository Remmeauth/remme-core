************
Ubuntu 18.04
************

**Ubuntu** — free and open-source ``Linux`` distribution based on ``Debian``. ``Ubuntu`` is offered in three
official editions: ``Ubuntu Desktop`` for personal computers, ``Ubuntu Server`` for servers and the cloud, and
``Ubuntu Core`` for Internet of things devices and robots. New releases of ``Ubuntu`` occur every six months,
while long-term support (LTS) releases occur every two years.

Step 1: choose release version
==============================

Visit |remme_core_releases_list| to choose your favorite version and change the value of ``REMME_CORE_RELEASE`` below.
Actually, we recommend the latest version of the project specified in
the command below.

.. |remme_core_releases_list| raw:: html

   <a href="https://github.com/Remmeauth/remme-core/releases" target="_blank">Remme-core releases list</a>

Step 2: install, build and run the node
=======================================

Open a terminal on your personal computer. See :doc:`/user-guide/troubleshooting` section to know how. Then copy the command below and paste to the terminal.

.. code-block:: console

   $ export REMME_CORE_RELEASE=0.6.0-alpha && \
         sudo apt-get install apt-transport-https ca-certificates curl software-properties-common -y && \
         cd /home/ && curl -L https://github.com/Remmeauth/remme-core/archive/v$REMME_CORE_RELEASE.tar.gz | sudo tar zx && \
         cd remme-core-$REMME_CORE_RELEASE && \
         sudo apt update && sudo apt upgrade -y && \
         curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - && \
         sudo apt update && \
         sudo apt install docker.io -y && \
         sudo curl -o /usr/local/bin/docker-compose -L "https://github.com/docker/compose/releases/download/1.23.2/docker-compose-$(uname -s)-$(uname -m)" && \
         sudo chmod +x /usr/local/bin/docker-compose && \
         sudo ./scripts/run.sh -g

.. image:: /img/user-guide/cloud/digital-ocean/installation-command.png
   :width: 100%
   :align: center
   :alt: Proof core is up

The expected result of the command is illustrated below.

.. image:: /img/user-guide/cloud/digital-ocean/installation-output.png
   :width: 100%
   :align: center
   :alt: Installation output

If during installation you will the the same windows as illustrated below, just press ``Enter``.

.. image:: /img/user-guide/cloud/digital-ocean/installation-possible-window.png
   :width: 100%
   :align: center
   :alt: Proof core is up

When you will see the same output as illustrated below, that means node is ready to accept requests.

.. image:: /img/user-guide/cloud/digital-ocean/proof-core-is-up.png
   :width: 100%
   :align: center
   :alt: Proof core is up

Step 3: ensure node is working
==============================

To check if your node did setup correctly, open brand new terminal window and send getting node configurations keys request.

.. code-block:: console

   $ curl -X POST http://127.0.0.1:8080 -H 'Content-Type: application/json' -d \
         '{"jsonrpc":"2.0","id":"11","method":"get_node_config","params":{}}' | python -m json.tool

Response should be similar.

.. code-block:: console

   {
       "id": "11",
       "jsonrpc": "2.0",
       "result": {
           "node_public_key": "028e7e9b060d7c407e428676299ced9afef4ce782995294d8ea01fd0f08cec9765",
           "storage_public_key": "028e7e9b060d7c407e428676299ced9afef4ce782995294d8ea01fd0f08cec9765"
       }
   }

The flow is illustrated below.

.. image:: /img/user-guide/cloud/digital-ocean/proof-core-is-working.png
   :width: 100%
   :align: center
   :alt: Proof core is working

What next?
==========

1. Visit our :doc:`/user-guide/advanced-guide` to know more about user experience.
2. Communication with node is available through :doc:`/rpc-api`, so take a look.
