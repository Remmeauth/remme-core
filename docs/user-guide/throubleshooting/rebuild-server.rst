Rebuild server
==============

Rebuilding a server allows you to keep the operational system (image), ``SSH keys`` and ``IP-address``. The rest everything
such as folders with node source code will be gone. Everything else such as folders with node source code will be gone.
So you don’t need to create a server from scratch, just rebuild it. When you connect to the rebuilt server for the first
time, you’ll get ``SSH key`` warning.

To avoid it, use the following terminal command on ``Ubuntu & Mac OS``:

.. code-block:: console

   $ rm ~/.ssh/known_hosts

On ``Windows`` use the following:

.. code-block:: console

   $ del %userprofile%\.ssh\known_hosts

Amazon Web Services
~~~~~~~~~~~~~~~~~~~

On ``AWS`` there's no way to rebuild your instance once you’ve already created it. But you can create an image from the instance
you have created for future rebuilds. Consider the image as a clone of the instance at a particular stage (before node
installation, after node installation, etc.).

Create a brand new instance using the following reference — :ref:`LaunchAWSInstance`. Follow the guides on how to create
and apply a snapshot of the instance — :ref:`CreateAWSSnapshot`, :ref:`ApplyAWSSnapshot`. But instead of making a snapshot
of the instance with the installed node, make a snapshot of the newly created instance. So you will now have the image of
the clear instance.

After, you can start from :ref:`LoginToTheAwsInstance`.

Digital Ocean
~~~~~~~~~~~~~

Open the page that shows all your droplets. Find the droplet that hosts your node (it could be named ``remme-core-testnet-node``).
Press the burger menu icon and choose the ``Destroy`` option.

.. image:: /img/user-guide/troubleshooting/rebuild-server/digital-ocean/destroy-droplet-button.png
   :width: 100%
   :align: center
   :alt: Destroy a droplet button

Afterward, go to the bottom of the page to the ``Rebuild Droplet`` section. Choose the image ``Ubuntu 16.04.6 x64``.

.. image:: /img/user-guide/troubleshooting/rebuild-server/digital-ocean/choose-image.png
   :width: 100%
   :align: center
   :alt: Choose an image for the droplet

Press the ``Rebuild`` button.

.. image:: /img/user-guide/troubleshooting/rebuild-server/digital-ocean/rebuild-button.png
   :width: 100%
   :align: center
   :alt: Rebuild a droplet

After pressing the rebuild button you will get a pop-up to confirm the rebuild.

.. image:: /img/user-guide/troubleshooting/rebuild-server/digital-ocean/confirm-rebuild-droplet.png
   :width: 100%
   :align: center
   :alt: Confirm rebuild a droplet

Now you can start from :ref:`LoginToTheDigitalOceanDroplet`.

Vultr
~~~~~

Open the page that shows all your servers. Find the server that hosts your node (it could be named ``remme-core-testnet-node``).
Press the burger menu icon and choose the ``Server Reinstall`` option.

.. image:: /img/user-guide/troubleshooting/rebuild-server/vultr/reinstall-server-button.png
   :width: 100%
   :align: center
   :alt: Destroy a server button

Afterward, you will get a pop-up to confirm the reinstallation. Tick the checkbox ``Yes, reinstall this server`` and press
``Reinstall Server``.

.. image:: /img/user-guide/troubleshooting/rebuild-server/vultr/confirm-reinstall-server.png
   :width: 100%
   :align: center
   :alt: Confirm reinstall a server

Now you can start from :ref:`LoginToTheVultrServer`.
