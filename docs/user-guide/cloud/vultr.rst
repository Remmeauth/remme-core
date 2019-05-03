*****
Vultr
*****

**Vultr**, founded in 2014, is on a mission to empower developers and businesses by simplifying the deployment of
infrastructure via its advanced cloud platform. **Vultr** is strategically located in 16 datacenters around the globe
and provides frictionless provisioning of public cloud, storage and single-tenant bare metal.

Step 1: sign up
===============

Visit the |registration_link| to create your own account on ``Vultr``.

.. |registration_link| raw:: html

   <a href="https://www.vultr.com/register/" target="_blank">registration link</a>

.. image:: /img/user-guide/cloud/vultr/sign-up-form.png
   :width: 100%
   :align: center
   :alt: Sign up form

Open your inbox, select the confirmation letter from ``Vultr`` and click on the link.

.. image:: /img/user-guide/cloud/vultr/confirm-e-mail-link.png
   :width: 100%
   :align: center
   :alt: Confirm e-mail ling

Enter your credit/debit card details into the form to pay for cloud services. You also have several payment options such
as ``PayPal`` and ``Bitcoin``.

.. image:: /img/user-guide/cloud/vultr/credit-card-form.png
   :width: 100%
   :align: center
   :alt: Credit or debit card details

Step 2: first server
=====================

After adding the payment method you will be redirected to the service creation page.

Choose any location you want - it does not matter. A node will be connected to the nearest other nodes in the region.

.. image:: /img/user-guide/cloud/vultr/server-location.png
   :width: 100%
   :align: center
   :alt: Server location

Specify server type ``Ubuntu 16.04 x64``, which should be regarded as an operating system, and choose the size of memory and
processor power for ``$20 per month``.

.. image:: /img/user-guide/cloud/vultr/server-type-and-size.png
   :width: 100%
   :align: center
   :alt: Server type and size

We also recommend enabling backups to revert the server in case you occasionally do something wrong. In the additional
feature list, tick the checkbox ``Enable Auto Backups`` to activate server backups.

Then generate your personal ``SSH key`` and add it to the server. Visit the :ref:`SshKeysThroubleshooting` troubleshooting
section to find instructions how to generate it.

An example of your ``SSH key`` and how to add it to the droplet is illustrated in the image below.

.. image:: /img/user-guide/cloud/vultr/server-ssh-key-adding.png
   :width: 100%
   :align: center
   :alt: Droplet SSH key adding

Remember to click on the created ``SSH key`` to activate it. Below, specify the name of the server you wish to connect
to (e.g. ``remme-core-testnet-node``) and press ``Deploy Now``.

.. image:: /img/user-guide/cloud/vultr/server-hostname-and-start.png
   :width: 100%
   :align: center
   :alt: Server hostname and start

Wait for your server to be ready as illustrated on the image below.

.. image:: /img/user-guide/cloud/vultr/server-is-ready.png
   :width: 100%
   :align: center
   :alt: Server is ready

.. _LoginToTheVultrServer:

Step 3: login to server
=======================

Open a terminal on your PC. Visit the :ref:`OpenTerminalThroubleshooting` troubleshooting section to find instructions how to do this.

Type the following command to login to the droplet. Remember to change ``157.230.146.230`` to your server ``IP address``.

.. code-block:: console

   $ ssh root@157.230.146.230

Then you will see the following text, type ``yes``.

.. code-block:: console

   The authenticity of host '157.230.146.230 (157.230.146.230)' can't be established.
   ECDSA key fingerprint is SHA256:uFq7qmVwA2Pb/voHO5ulxX3j0Yvb6zPY+4pDZBQSpuM.
   Are you sure you want to continue connecting (yes/no)?

After that you will be required to enter the password from the ``SSH key``. Note that when you do so, the password
doesn't appear – even stars or bullets shouldn’t appear as you wait to login to the account on the operating system.
Type in the password and press ``Enter``.

.. code-block:: console

   Warning: Permanently added '157.230.146.230' (ECDSA) to the list of known hosts.
   Enter passphrase for key '/Users/dmytrostriletskyi/.ssh/id_rsa':

When you see the following lie or similar it means you are successfully logged in:

.. code-block:: console

   Welcome to Ubuntu 16.04.5 LTS (GNU/Linux 4.4.0-142-generic x86_64)

     * Documentation:  https://help.ubuntu.com
     * Management:     https://landscape.canonical.com
     * Support:        https://ubuntu.com/advantage

   root@remme-core-testnet-node:~#

The flow is illustrated below.

.. image:: /img/user-guide/cloud/vultr/login-to-the-server-ssh.png
   :width: 100%
   :align: center
   :alt: Droplet SSH key login

Step 4: start the project
=========================

Export environment variable with your server ``IP address`` with the following command. Remember to change
``157.230.146.230`` to your server's ``IP address``.

.. code-block:: console

   $ export NODE_IP_ADDRESS=157.230.146.230

Now, specify the release of the node you want to start. We would recommend the latest version of the project that already
specified in the command below. But you can change the value of ``REMME_CORE_RELEASE``, just take a look at our
`release list <https://github.com/Remmeauth/remme-core/releases>`_.

.. code-block:: console

   $ export REMME_CORE_RELEASE=0.9.1-alpha

After, copy and paste the following commands to the terminal which will install and start your node.

.. code-block:: console

   $ sudo apt-get install apt-transport-https ca-certificates curl software-properties-common make -y && \
         sudo sh -c "echo 'LC_ALL=en_US.UTF-8\nLANG=en_US.UTF-8' >> /etc/environment" && \
         echo "REMME_CORE_RELEASE=$REMME_CORE_RELEASE" >> ~/.bashrc && \
         echo "NODE_IP_ADDRESS=$NODE_IP_ADDRESS" >> ~/.bashrc && \
         cd /home/ && curl -L https://github.com/Remmeauth/remme-core/archive/v$REMME_CORE_RELEASE.tar.gz | sudo tar zx && \
         cd remme-core-$REMME_CORE_RELEASE && \
         sudo -i sed -i "s@80@3333@" /home/remme-core-$REMME_CORE_RELEASE/docker/compose/admin.yml && \
         sudo -i sed -i "s@127.0.0.1@$NODE_IP_ADDRESS@" /home/remme-core-$REMME_CORE_RELEASE/config/network-config.env && \
         sudo -i sed -i '/      - GF_USERS_ALLOW_SIGN_UP=false/a \      - GF_SERVER_ROOT_URL=%(protocol)s:\/\/%(domain)s:\/monitoring\/' /home/remme-core-$REMME_CORE_RELEASE/docker/compose/mon.yml && \
         sudo apt update && sudo apt upgrade -y && \
         curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add && \
         sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" && \
         sudo apt-get update && sudo apt-get install docker-ce -y && \
         sudo apt update && sudo apt install nginx -y && \
         curl https://gist.githubusercontent.com/dmytrostriletskyi/70dda8c594e60be1e089586f2ee8c0a0/raw/d453465e337cf5052a94b1d961f8a82c392ecf21/http-nginx.conf| sudo tee /etc/nginx/nginx.conf > /dev/null && \
         sudo curl -o /usr/local/bin/docker-compose -L "https://github.com/docker/compose/releases/download/1.23.2/docker-compose-$(uname -s)-$(uname -m)" && \
         sudo chmod +x /usr/local/bin/docker-compose && \
         curl https://gist.githubusercontent.com/dmytrostriletskyi/9f525241acfc46799c65d5f010c43b5f/raw/3147860240613e7e2eab5e288d48a975934a260a/up-node-after-server-restart.sh > ~/up-node-after-server-restart.sh && \
         chmod +x ~/up-node-after-server-restart.sh && \
         curl https://gist.githubusercontent.com/dmytrostriletskyi/ddb0d8fc16512523f4942a2d60b57c63/raw/63de05cc7f68801bb6887fc07463422810276a10/upgrade-node.sh > ~/upgrade-node.sh && \
         chmod +x ~/upgrade-node.sh && \
         echo "@reboot $USER ~/./up-node-after-server-restart.sh $REMME_CORE_RELEASE" | sudo tee -a /etc/crontab > /dev/null && \
         curl https://gist.githubusercontent.com/dmytrostriletskyi/8c07b752f8efd52d6f69feddd62e3af9/raw/438a72324fe8bfcaf9f56a4023eeaa1fa18ddb9a/seeds-list.txt | sudo tee config/seeds-list.txt > /dev/null && \
         sudo systemctl restart nginx && \
         sudo make run_bg_user

.. image:: /img/user-guide/cloud/digital-ocean/installation-command.png
   :width: 100%
   :align: center
   :alt: Terminal installation command example

The expected result of this command is illustrated below.

.. image:: /img/user-guide/cloud/digital-ocean/installation-output.png
   :width: 100%
   :align: center
   :alt: Installation output

If during installation the same window as illustrated below appears, just press ``Enter``.

.. image:: /img/user-guide/cloud/digital-ocean/installation-possible-window.png
   :width: 100%
   :align: center
   :alt: Installation possible window

When you see the same output as illustrated below, it means the node is ready to accept requests.

.. image:: /img/user-guide/cloud/digital-ocean/proof-core-is-up.png
   :width: 100%
   :align: center
   :alt: Proof core is up

To check if your node has completed a correct setup, use the following command:

.. code-block:: console

   $ curl -X POST http://$NODE_IP_ADDRESS/rpc/ -H 'Content-Type: application/json' -d \
         '{"jsonrpc":"2.0","id":"11","method":"get_node_config","params":{}}' | python3 -m json.tool

The response should look similar to this:

.. code-block:: console

   {
       "jsonrpc": "2.0",
       "id": "11",
       "result": {
           "node_public_key": "02b844a10124aae7713e18d80b1a7ae70fcbe73931dd933c821b354f872907f7f3",
           "node_address": "116829caa6f35dddfd62d067607426407c95bf8dbc37fa55bcf734366df2e97cac660b"
       }
   }

The flow is illustrated below.

.. image:: /img/user-guide/cloud/digital-ocean/proof-core-is-working.png
   :width: 100%
   :align: center
   :alt: Proof core is working

Step 5: admin panel
===================

While starting the node, the admin panel has also been installed and started. Log into the admin panel. Copy your server's
``IP address``, paste it into the browser address bar press ``Enter``. Then you will see the initial admin panel page with
authentication. Enter ``remme`` to the password fields.

.. image:: /img/user-guide/admin-panel/login-page.png
   :width: 100%
   :align: center
   :alt: Admin panel login page

With the admin panel you can do the following operations:

1. Monitor balances and credentials of the node.
2. Transfer tokens from the node account to other accounts.
3. Become a masternode, close your masternode and so on.

.. image:: /img/user-guide/admin-panel/home-page.png
   :width: 100%
   :align: center
   :alt: Admin panel home page

Step 6: monitoring
==================

Another option to check if your node has completed a correct setup is through monitoring. While starting the node, the monitoring
has also been installed and started. **Completing this step is required**.

Monitoring is a process of tracking application performance to detect and prevent issues that could occur with your application
on a particular server. For the monitoring, we will use ``Grafana``. It is an open source, feature-rich metrics dashboard
and graph editor.

Being in the admin panel, click on the ``Monitoring`` tab.

.. image:: /img/user-guide/admin-panel/monitoring-tool.png
   :width: 100%
   :align: center
   :alt: Admin panel monitoring tab

Then you will see the initial ``Grafana`` page with authentication. Enter ``remme`` to the ``User`` and ``Password`` fields.

.. image:: /img/user-guide/advanced-guide/monitoring/login.png
   :width: 100%
   :align: center
   :alt: Login to the Grafana

Here you will find information about uptime, CPU cores and their load, memory and its load, storage and its load. Also,
information about containers (components of the node) is presented on the right side of the page. Information
about containers includes numbers on how much CPU each uses, and so on.

.. image:: /img/user-guide/advanced-guide/monitoring/dashboard.png
   :width: 100%
   :align: center
   :alt: Grafana dashboard

You should then personalize your credentials. Go to the profile page.

.. image:: /img/user-guide/advanced-guide/monitoring/go-to-profile.png
   :width: 100%
   :align: center
   :alt: Go to the Grafana profile button

Change the name, email and username. Also, the preferences can be changed to suit your user interface needs.

.. image:: /img/user-guide/advanced-guide/monitoring/profile-settings.png
   :width: 100%
   :align: center
   :alt: Grafana profile settings

Don't forget to change the default password to a new and secure one.

.. image:: /img/user-guide/advanced-guide/monitoring/change-password.png
   :width: 100%
   :align: center
   :alt: Change Grafana profile password

What's next?
============

1. Secure your account with two-factor authentication that adds an extra layer of security to your account. To log in, you'll
need to provide a code along with your username and password.

.. image:: /img/user-guide/cloud/vultr/2-fa-authentication.png
   :width: 100%
   :align: center
   :alt: 2FA authentication

2. Set up desirable backup settings.

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
