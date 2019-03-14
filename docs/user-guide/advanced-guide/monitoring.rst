Monitoring
==========

Monitoring is a process of tracking application performance to detect and prevent issues that could happen with your application
on a particular server. For the monitoring, we will use ``Grafana``. |grafana|  is an open source, feature-rich metrics dashboard
and graph editor.

.. |grafana| raw:: html

   <a href="https://grafana.com/" target="_blank">Grafana</a>

First of all, login to the server as you previously did during installation of the node. Remember to change ``68.183.137.173``
to your server's ``IP address``.

.. code-block:: console

   $ ssh root@68.183.137.173

The flow is illustrated below.

.. image:: /img/user-guide/advanced-guide/ssh-login-to-the-server.png
   :width: 100%
   :align: center
   :alt: SSH login to the server

Copy the command below and paste it into the terminal.

.. code-block:: console

   $ cd /home/remme-core-$REMME_CORE_RELEASE && \
         curl -L https://github.com/Remmeauth/remme-mon-stack/archive/v1.0.0.tar.gz | sudo tar zx && \
         cd remme-mon-stack-1.0.0 && \
         docker-compose up -d

Copy the ``IP address`` and paste it into the browser address bar. Enter ``admin`` to the ``User`` and ``Password`` fields.

.. image:: /img/user-guide/advanced-guide/monitoring/login.png
   :width: 100%
   :align: center
   :alt: Login to the Grafana

After entering the initial credentials you will reach the main page. Click on ``Main Dashboard`` to open monitoring graphs for
your node.

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

To stop monitoring, use the ``docker-compose stop`` terminal command.
