*****
Vultr
*****

**Vultr**, founded in 2014, is on a mission to empower developers and businesses by simplifying the deployment of
infrastructure via its advanced cloud platform. **Vultr** is strategically located in 16 datacenters around the globe
and provides frictionless provisioning of public cloud, storage and single-tenant bare metal.

Step 1: sign up
===============

Visit `registration link <https://www.vultr.com/register/>`_ to create your own account on ``Vultr``.

.. image:: /img/user-guide/cloud/vultr/sign-up-form.png
   :width: 100%
   :align: center
   :alt: Sign up form

Open your e-mail box, find the confirmation letter from ``Vultr`` and click on the link.

.. image:: /img/user-guide/cloud/vultr/confirm-e-mail-link.png
   :width: 100%
   :align: center
   :alt: Confirm e-mail ling

Fill up the form with credit/debit card details to pay for cloud services. You also have several payment options such
as ``PayPal``, ``Bitcoin``, etc.

.. image:: /img/user-guide/cloud/vultr/credit-card-form.png
   :width: 100%
   :align: center
   :alt: Credit or debit card details

Step 2: first server
=====================

After adding the payment method you will be redirected to the service creation page.

Choose any location you want, it does not matter. A node will be connected to nearest other nodes in the region.

.. image:: /img/user-guide/cloud/vultr/server-location.png
   :width: 100%
   :align: center
   :alt: Server location

Specify server type ``Ubuntu 16.04 x64``, consider it as an operating system, and choose the size of memory and
processor power for ``$20 per month``.

.. image:: /img/user-guide/cloud/vultr/server-type-and-size.png
   :width: 100%
   :align: center
   :alt: Server type and size

Also, we recommend to enable backups to revert the server if you will occasionally do something wrong. So, in the additional
feature list, check a checkbox ``Enable Auto Backups`` to enable the server backups.

Go below, specify the name of the server to which we will connect (i.e. ``remme-core-testnet-node``) and press ``Deploy Now``.

.. image:: /img/user-guide/cloud/vultr/server-hostname-and-start.png
   :width: 100%
   :align: center
   :alt: Server hostname and start

Wait for your server to be ready as illustrated on the image below.

.. image:: /img/user-guide/cloud/vultr/server-is-ready.png
   :width: 100%
   :align: center
   :alt: Server is ready

Step 3: login to server
=======================

Check server details by clicking on it. There will be ``IP-address``, ``username``, and ``password`` which are used for login to the server.

.. image:: /img/user-guide/cloud/vultr/server-details.png
   :width: 100%
   :align: center
   :alt: Server details

Open a terminal on your PC. Visit :doc:`/user-guide/troubleshooting` section to find instructions how to do it.

The image below, illustrated how to connect to the server - type ``ssh root@95.179.156.74``. Do the same, but
instead of ``95.179.156.74``, put your ``IP-address`` from the server details.

Then type ``yes``, to continue the connection.

When you see the output line ``root@95.179.156.74's password:``, just copy and paste the password.
Mind, when you do it, password doesn't appear, even stars or bullets don't appear as wait for the login to the
account on operating system. So paste and press ``Enter``.

.. image:: /img/user-guide/cloud/vultr/login-to-the-server.png
   :width: 100%
   :align: center
   :alt: Login to the droplet server

Step 4: start the project
=========================

Visit ``Remme-core`` `releases list <https://github.com/Remmeauth/remme-core/releases>`_  to choose the right version
based on the changelog of each option.

.. image:: /img/releases_list_on_github.png
   :width: 100%
   :align: center
   :alt: Github page with Remme core releases

Then change the value of ``REMME_CORE_RELEASE`` below. Though, we would recommend the latest version of the project that
already specified in the command below.

Copy the command above and paste to the terminal.

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

If during the installation same window as illustrated below appears, just press ``Enter``.

.. image:: /img/user-guide/cloud/digital-ocean/installation-possible-window.png
   :width: 100%
   :align: center
   :alt: Proof core is up

When you see the same output as illustrated below, it means the node is ready to accept requests.

.. image:: /img/user-guide/cloud/digital-ocean/proof-core-is-up.png
   :width: 100%
   :align: center
   :alt: Proof core is up

To check if your node did a correct setup, open a brand new terminal window and send getting node configurations keys request.

.. code-block:: console

   $ export NODE_IP_ADDRESS=95.179.156.74
   $ curl -X POST http://$NODE_IP_ADDRESS:8080 -H 'Content-Type: application/json' -d \
         '{"jsonrpc":"2.0","id":"11","method":"get_node_config","params":{}}' | python -m json.tool

Response should looks similar.

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

1. Secure your account with two-factor authentication that adds an extra layer of security to your account. To log in, you'll
need to provide a code along with your username and password.

.. image:: /img/user-guide/cloud/vultr/2-fa-authentication.png
   :width: 100%
   :align: center
   :alt: 2FA authentication

2. Setup desirable backups settings.

.. image:: /img/user-guide/cloud/vultr/server-backups.png
   :width: 100%
   :align: center
   :alt: Server type and size

3. Take a look at the server's monitoring at the ``User graph`` menu section. There are graphs which illustrate performance metrics.

.. image:: /img/user-guide/cloud/vultr/server-monitoring.png
   :width: 100%
   :align: center
   :alt: Server type and size

4. Visit our :doc:`/user-guide/advanced-guide` for more details on user experience.
5. Communication with the node is available through :doc:`/apis/rpc` API, so check it out.
