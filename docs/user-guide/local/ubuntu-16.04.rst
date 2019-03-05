************
Ubuntu 16.04
************

**Ubuntu**  is a free and open-source ``Linux`` distribution based on ``Debian``. ``Ubuntu`` is released in three
official editions: ``Ubuntu Desktop`` for personal computers, ``Ubuntu Server`` for servers and the cloud, and
``Ubuntu Core`` for IoT devices and robots. New releases of ``Ubuntu`` occur every six months,
while long-term support releases occur every two years.

Step 1: install and start node
==============================

Open a terminal on your PC. Visit the :doc:`/user-guide/troubleshooting` section to find instructions.

Copy commands below and paste it into the terminal. You can change the value of ``REMME_CORE_RELEASE`` below, just take
a look at our `release list <https://github.com/Remmeauth/remme-core/releases>`_. We would recommend the latest version of
the project that already specified in the command below.

.. code-block:: console

   $ export REMME_CORE_RELEASE=0.7.0-alpha
   $ sudo apt-get install apt-transport-https ca-certificates curl software-properties-common make -y && \
         cd /home/ && curl -L https://github.com/Remmeauth/remme-core/archive/v$REMME_CORE_RELEASE.tar.gz | sudo tar zx && \
         cd remme-core-$REMME_CORE_RELEASE && \
         sudo apt update && sudo apt upgrade -y && \
         curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - && \
         sudo apt update && \
         sudo apt install docker.io -y && \
         sudo curl -o /usr/local/bin/docker-compose -L "https://github.com/docker/compose/releases/download/1.23.2/docker-compose-$(uname -s)-$(uname -m)" && \
         sudo chmod +x /usr/local/bin/docker-compose && \
         sudo make run_genesis_bg

.. image:: /img/user-guide/local/ubuntu/installation-command.png
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

Step 2: ensure the node is working
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
           "node_public_key": "028e7e9b060d7c407e428676299ced9afef4ce782995294d8ea01fd0f08cec9765"
       }
   }

The flow is illustrated below.

.. image:: /img/user-guide/local/proof-node-works.png
   :width: 100%
   :align: center
   :alt: Proof core is working

What's next?
============

1. Visit our :doc:`/user-guide/advanced-guide` for more details on user experience.
2. Communication with the node is available through :doc:`/apis/rpc` API, so check it out.

