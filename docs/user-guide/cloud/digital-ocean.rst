*************
Digital Ocean
*************

**Digital Ocean** — cloud services that help to deploy and scale applications that run simultaneously on multiple
computers. Digital Ocean optimized configuration process saves your team time when running and scaling distributed
applications, AI & machine learning workloads, hosted services, client websites, or CI/CD environments.

Step 1: sign up
===============

Visit `registration link <https://cloud.digitalocean.com/registrations/new>`_ to create your own account on ``Digital Ocean``.
Enter your e-mail address and password.

If you login through another services such as ``Google``, some step below couldn't be suitable for you.

.. image:: /img/user-guide/cloud/digital-ocean/sign-up-form.png
   :width: 100%
   :align: center
   :alt: Sign up form

After initial credentials you will get the pop-up to verify the account with e-mail.

.. image:: /img/user-guide/cloud/digital-ocean/confirm-e-mail-mention.png
   :width: 100%
   :align: center
   :alt: Confirm e-mail pop-up

Open e-mail box, find the confirmation letter for from ``Digital Ocean`` and click on link.

.. image:: /img/user-guide/cloud/digital-ocean/confirm-e-mail-link.png
   :width: 100%
   :align: center
   :alt: Confirm e-mail link

Then you will be required to fill up the form with credit or debit card details to pay for cloud services. You are able to use `PayPal` account also..

.. image:: /img/user-guide/cloud/digital-ocean/credit-card-form.png
   :width: 100%
   :align: center
   :alt: Credit or debit card details

Step 2: first project
=====================

On ``Digital Ocean`` you should create a project that will contains many cloud services you may use. For our purposes we will rent only one
server, but anyway project creation even for single is necessary option.

Name it ``Remme-core`` and choose appropriate category called ``Service or API``.

.. image:: /img/user-guide/cloud/digital-ocean/create-first-project-head.png
   :width: 100%
   :align: center
   :alt: First project head details

You need nothing more, so press button ``Start`` to finish project creation.

.. image:: /img/user-guide/cloud/digital-ocean/create-first-project-bottom.png
   :width: 100%
   :align: center
   :alt: First project bottom details

Step 3: first droplet
=====================

Droplets are a scalable compute platform with add-on storage, security, and monitoring capabilities to easily run production applications.
Make long story short, consider droplets as single server that will host ``Remme-core`` project.

Create it with green button at right-top corner of the screen.

.. image:: /img/user-guide/cloud/digital-ocean/create-droplet.png
   :width: 100%
   :align: center
   :alt: Create droplet

Specify image ``Ubuntu 18.10 x64``, consider it as operation system, and size of memory and processor power for ``$5 per month``.

.. image:: /img/user-guide/cloud/digital-ocean/droplet-image-and-size.png
   :width: 100%
   :align: center
   :alt: Specify droplet image and size

Go below, specify name of the server we will connect too (i.e. ``remme-core-testnet-node``) and press ``Start``.

.. image:: /img/user-guide/cloud/digital-ocean/droplet-hostname-and-start.png
   :width: 100%
   :align: center
   :alt: Specify droplet hostname and press start

Wait your droplet is ready as like on the screen below.

.. image:: /img/user-guide/cloud/digital-ocean/droplet-is-ready.png
   :width: 100%
   :align: center
   :alt: Droplet is ready

Visit e-mail box to find a letter from ``Digital Ocean`` with details about your droplet.
``IP-address``, ``username`` and ``password`` are used for login to droplet.

.. image:: /img/user-guide/cloud/digital-ocean/droplet-information-e-mail.png
   :width: 100%
   :align: center
   :alt: Droplet information

Step 4: login to droplet
========================

Open a terminal on your personal computer. See :doc:`/user-guide/troubleshooting` section to know how.

As you see on the screen below, to connect to the droplet, we type ``ssh root@157.230.146.230``. Do the same, but
instead of ``157.230.146.230``, put your ``IP-address`` from the e-mail.

Then surely type ``yes``, we are sure to continues connection.

Few seconds latter you will see ``root@157.230.146.230's password:`` output line, so just copy the password and paste it.
Mind, when you will do it, password won't appears, even start (``*``). So coolly paste and press ``Enter``.

After that you will be required yo change the password for the security reasons. First of all, type the know password again
to proof you are authorized to change password, the second point is to type new password and repeat it. Choose long and strong passwords.

.. image:: /img/user-guide/cloud/digital-ocean/login-to-droplet-server.png
   :width: 100%
   :align: center
   :alt: Login to the droplet server

Step 5: up the project
=======================

Visit ``Remme-core`` `releases list <https://github.com/Remmeauth/remme-core/releases>`_ to choose your favorite version and
change the value of ``REMME_CORE_RELEASE`` below. Actually, we recommend the latest version of the project specified in
the command below.

Copy the command above and paste to the terminal.

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

To check if your node did setup correctly, open brand new terminal window and send getting node configurations keys request.

.. code-block:: console

   $ export NODE_IP_ADDRESS=157.230.146.230
   $ curl -X POST http://$NODE_IP_ADDRESS:8080 -H 'Content-Type: application/json' -d \
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
