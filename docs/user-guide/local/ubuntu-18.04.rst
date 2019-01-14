************
Ubuntu 18.04
************

**Ubuntu**  is a free and open-source ``Linux`` distribution based on ``Debian``. ``Ubuntu`` is released in three
official editions: ``Ubuntu Desktop`` for personal computers, ``Ubuntu Server`` for servers and the cloud, and
``Ubuntu Core`` for IoT devices and robots. New releases of ``Ubuntu`` occur every six months,
while long-term support releases occur every two years.

Step 1: choose release version
==============================

Visit ``Remme-core`` `releases list <https://github.com/Remmeauth/remme-core/releases>`_  to choose the right version
based on the changelog of each option.

.. image:: /img/releases_list_on_github.png
   :width: 100%
   :align: center
   :alt: Github page with Remme core releases

Then change the value of ``REMME_CORE_RELEASE`` below. Though, we would recommend the latest version of the project that
already specified in the command below.

.. |remme_core_releases_list| raw:: html

   <a href="https://github.com/Remmeauth/remme-core/releases" target="_blank">Remme-core releases list</a>

Step 2: install, build and run the node
=======================================

Open a terminal on your PC. Visit :doc:`/user-guide/troubleshooting` section to find instructions. Then copy the command below and paste to the terminal.

.. code-block:: console

   $ export REMME_CORE_RELEASE=0.6.0-alpha && \
         sudo apt-get install apt-transport-https ca-certificates curl software-properties-common make -y && \
         cd /home/ && curl -L https://github.com/Remmeauth/remme-core/archive/v$REMME_CORE_RELEASE.tar.gz | sudo tar zx && \
         cd remme-core-$REMME_CORE_RELEASE && \
         sudo apt update && sudo apt upgrade -y && \
         curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - && \
         sudo apt update && \
         sudo apt install docker.io -y && \
         sudo curl -o /usr/local/bin/docker-compose -L "https://github.com/docker/compose/releases/download/1.23.2/docker-compose-$(uname -s)-$(uname -m)" && \
         sudo chmod +x /usr/local/bin/docker-compose && \
         make run_genesis_bg

.. image:: /img/user-guide/cloud/digital-ocean/installation-command.png
   :width: 100%
   :align: center
   :alt: Proof core is up

The expected result of the command is illustrated below.

.. image:: /img/user-guide/cloud/digital-ocean/installation-output.png
   :width: 100%
   :align: center
   :alt: Installation output

If during the installation the same window as illustrated below appears, just press ``Enter``.

.. image:: /img/user-guide/cloud/digital-ocean/installation-possible-window.png
   :width: 100%
   :align: center
   :alt: Installation possible popup

When you see the same output as illustrated below, it means the node is ready to accept requests.

.. image:: /img/user-guide/cloud/digital-ocean/proof-core-is-up.png
   :width: 100%
   :align: center
   :alt: Proof core is up

Step 3: ensure the node is working
==================================

To check if your node did a correct set-up, open a brand new terminal window and send getting node configurations keys request.

.. code-block:: console

   $ curl -X POST http://127.0.0.1:8080 -H 'Content-Type: application/json' -d \
         '{"jsonrpc":"2.0","id":"11","method":"get_node_config","params":{}}' | python -m json.tool

The response should look as illustrated below.

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

What's next?
============

1. Visit our :doc:`/user-guide/advanced-guide` for more details on user experience.
2. Communication with the node is available through :doc:`/rpc-api`, so check it out.
