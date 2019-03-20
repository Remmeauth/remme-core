************
Ubuntu 18.04
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
         echo "REMME_CORE_RELEASE=$REMME_CORE_RELEASE" >> ~/.bashrc && \
         cd /home/ && curl -L https://github.com/Remmeauth/remme-core/archive/v$REMME_CORE_RELEASE.tar.gz | sudo tar zx && \
         cd remme-core-$REMME_CORE_RELEASE && \
         sudo apt update && sudo apt upgrade -y && \
         curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - && \
         sudo apt update && sudo apt install docker.io -y && \
         curl https://raw.githubusercontent.com/Remmeauth/remme-core/master/docs/user-guide/templates/node-nginx.conf > nginx.conf && \
         sudo curl -o /usr/local/bin/docker-compose -L "https://github.com/docker/compose/releases/download/1.23.2/docker-compose-$(uname -s)-$(uname -m)" && \
         sudo chmod +x /usr/local/bin/docker-compose && \
         curl -L https://github.com/Remmeauth/remme-mon-stack/archive/v1.0.1.tar.gz | sudo tar zx && \
         sed -i '/GF_SERVER_ROOT_URL/d' remme-mon-stack-1.0.1/docker-compose.yml && \
         sudo docker-compose -f remme-mon-stack-1.0.1/docker-compose.yml up -d && \
         sudo docker run --name nginx -p 80:80 -d -v /home/remme-core-$REMME_CORE_RELEASE/nginx.conf:/etc/nginx/nginx.conf --network="host" nginx && \
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

To check if your node has completed a correct setup, use the following commands, being in the same terminal window.

.. code-block:: console

   $ curl -X POST http://127.0.0.1:8080 -H 'Content-Type: application/json' -d \
         '{"jsonrpc":"2.0","id":"11","method":"get_node_config","params":{}}' | python3 -m json.tool

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

Step 3: monitoring
==================

Another option to check if your node has completed a correct setup is the monitoring. While starting the node, the monitoring also
has been installed and started. **Completing this step is required**.

Monitoring is a process of tracking application performance to detect and prevent issues that could happen with your application
on a particular server. For the monitoring, we will use ``Grafana``. |grafana| is an open source, feature-rich metrics dashboard
and graph editor.

.. |grafana| raw:: html

   <a href="https://grafana.com/" target="_blank">Grafana</a>

Paste ``127.0.0.1:3000`` into the browser address bar. Then you will see initial ``Grafana`` page with authentication.
Enter ``admin`` to the ``User`` and ``Password`` fields.

.. image:: /img/user-guide/advanced-guide/monitoring/login-local.png
   :width: 100%
   :align: center
   :alt: Login to the Grafana

After entering the initial credentials you will reach the main page. Click on ``Main Dashboard`` to open monitoring graphs for
your node. If you do not see the ``Main Dashboard`` button, visit the :doc:`/user-guide/troubleshooting` section to
find instructions how solve it.

.. image:: /img/user-guide/advanced-guide/monitoring/main-dashboard.png
   :width: 100%
   :align: center
   :alt: Go to the Grafana main dashboard button

Here you will find information about uptime, CPU cores and their load, memory and its load, storage and its load. Also,
information about containers (components of the node) is presented on the right side of the page. Information
about container includes numbers on how much CPU each uses, and so on.

.. image:: /img/user-guide/advanced-guide/monitoring/dashboard.png
   :width: 100%
   :align: center
   :alt: Grafana dashboard

You should then personalize your your credentials. Go to the profile page.

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

1. Visit our :doc:`/user-guide/advanced-guide` for more details on user experience.
2. Communication with the node is available through :doc:`/apis/rpc` API, so check it out.

