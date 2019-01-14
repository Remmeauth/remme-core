*************
Digital Ocean
*************

**Digital Ocean** — cloud services that help to deploy and scale applications that run simultaneously on multiple
computers. Digital Ocean optimized configuration process saves time when running and scaling distributed
applications, AI & ML workloads, hosted services, client websites, or CI/CD environments.

Step 1: sign up
===============

Visit `registration link <https://cloud.digitalocean.com/registrations/new>`_ to create your own account on ``Digital Ocean``.

If you login through another services such as ``Google``, some steps below couldn't be suitable for you.

.. image:: /img/user-guide/cloud/digital-ocean/sign-up-form.png
   :width: 100%
   :align: center
   :alt: Sign up form

After entering initial credentials you will get the pop-up to verify the account.

.. image:: /img/user-guide/cloud/digital-ocean/confirm-e-mail-mention.png
   :width: 100%
   :align: center
   :alt: Confirm e-mail pop-up

Open your e-mail box, find the confirmation letter from Digital Ocean and click on the link.

.. image:: /img/user-guide/cloud/digital-ocean/confirm-e-mail-link.png
   :width: 100%
   :align: center
   :alt: Confirm e-mail link

Fill up the form with credit\debit card details to pay for cloud services. You also have the option of using ``PayPal`` account.

.. image:: /img/user-guide/cloud/digital-ocean/credit-card-form.png
   :width: 100%
   :align: center
   :alt: Credit or debit card details

Step 2: first project
=====================

On ``Digital Ocean``, create a project with multiple cloud services that you may use. For our purposes, we will rent only one
server, but anyway the project creation even for a single server is a necessary option.

Name it ``Remme-core`` and choose category named ``Service or API``.

.. image:: /img/user-guide/cloud/digital-ocean/create-first-project-head.png
   :width: 100%
   :align: center
   :alt: First project head details

Press ``Start`` button to finish the project creation.

.. image:: /img/user-guide/cloud/digital-ocean/create-first-project-bottom.png
   :width: 100%
   :align: center
   :alt: First project bottom details

Step 3: first droplet
=====================

Droplets are a scalable compute platform with add-on storage, security, and monitoring capabilities to easily run production applications.
Long story short, consider droplets as single server that will host ``Remme-core`` project.

Create it with green button at the right-top corner of the screen.

.. image:: /img/user-guide/cloud/digital-ocean/create-droplet.png
   :width: 100%
   :align: center
   :alt: Create droplet

Specify image ``Ubuntu 18.10 x64``, consider it as operating system, and choose the size of memory and processor power for ``$5 per month``.

.. image:: /img/user-guide/cloud/digital-ocean/droplet-image-and-size.png
   :width: 100%
   :align: center
   :alt: Specify droplet image and size

Go below, specify the name of the server to which we will connect (i.e. ``remme-core-testnet-node``) and press ``Start``.

.. image:: /img/user-guide/cloud/digital-ocean/droplet-hostname-and-start.png
   :width: 100%
   :align: center
   :alt: Specify droplet hostname and press start

Wait for your droplet to be ready as illustrated on the image below.

.. image:: /img/user-guide/cloud/digital-ocean/droplet-is-ready.png
   :width: 100%
   :align: center
   :alt: Droplet is ready

Check e-mail box to find a letter from ``Digital Ocean`` with details about your droplet.
``IP-address``, ``username`` and ``password`` are used for login to droplet.

.. image:: /img/user-guide/cloud/digital-ocean/droplet-information-e-mail.png
   :width: 100%
   :align: center
   :alt: Droplet information

Step 4: login to droplet
========================

Open a terminal on your PC. Visit :doc:`/user-guide/troubleshooting` section to find instructions how to do it.

The image below, illustrated how to connect to the droplet - type ``ssh root@157.230.146.230``. Do the same, but
instead of ``157.230.146.230``, put your ``IP-address`` from the e-mail.

Then type ``yes``, to continue the connection.

When you see the output line ``root@157.230.146.230's password:``, just copy and paste the password.
Mind, when you do it, password doesn't appear, even stars or bullets don't appear as wait for the login to the
account on operating system. So paste and press ``Enter``.

After that you will be required to change password for security reasons. At first, type current password to proof you
are authorized to change the password, then type a new password and repeat it. We recommend that you should
create long and strong passwords.

.. image:: /img/user-guide/cloud/digital-ocean/login-to-droplet-server.png
   :width: 100%
   :align: center
   :alt: Login to the droplet server

Step 5: start the project
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

   $ export NODE_IP_ADDRESS=157.230.146.230
   $ curl -X POST http://$NODE_IP_ADDRESS:8080 -H 'Content-Type: application/json' -d \
         '{"jsonrpc":"2.0","id":"11","method":"get_node_config","params":{}}' | python -m json.tool

Response should look similar.

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
