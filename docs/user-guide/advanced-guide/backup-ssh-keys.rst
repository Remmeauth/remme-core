Backup ssh keys
===============

Windows
-------

Open the ``File Explorer`` and enter ``%userprofile%`` to the search bar.

.. image:: /img/user-guide/advanced-guide/backup-ssh/windows/user-profile.png
   :width: 100%
   :align: center
   :alt: Reach user profile directory

Find the folder named ``.ssh`` and click on it.

.. image:: /img/user-guide/advanced-guide/backup-ssh/windows/ssh-folder.png
   :width: 100%
   :align: center
   :alt: Reach SSH folder

There are public and private ``SSH keys`` (``id_rsa`` an ``id_rsa.pub``), that allow you to login to the server.

.. image:: /img/user-guide/advanced-guide/backup-ssh/windows/keys-files.png
   :width: 100%
   :align: center
   :alt: Reach SSH keys files

Save those files to secure place (i.e. USB flash drive). If you want to log in into the server from another computer,
you should create the same ``.ssh`` directory by the same path with those ``SSH keys`` inside.

Mac OS
------

Open the ``Finder``.

.. image:: /img/user-guide/advanced-guide/backup-ssh/mac/open-finder.png
   :width: 100%
   :align: center
   :alt: Reach finder

Press ``Go`` at the top bar and choose ``Go to Folder...`` option.

.. image:: /img/user-guide/advanced-guide/backup-ssh/mac/go-to-finder.png
   :width: 100%
   :align: center
   :alt: Reach go to feature

After, you will get the pop-up to enter the path you want to go. Enter the lambda symbol (``~``) there and press ``Go``.

.. image:: /img/user-guide/advanced-guide/backup-ssh/mac/go-to-finder-path.png
   :width: 100%
   :align: center
   :alt: Reach user folder by lambda

Then you will be redirected to your root directory.

.. image:: /img/user-guide/advanced-guide/backup-ssh/mac/user-folder.png
   :width: 100%
   :align: center
   :alt: Reach user folder in the finder

Then press ``Shift + Commad + .`` key combination to show hidden folder. Find the folder named ``.ssh`` and go to it.

.. image:: /img/user-guide/advanced-guide/backup-ssh/mac/ssh-folder.png
   :width: 100%
   :align: center
   :alt: Reach SSH folder

There are public and private ``SSH keys`` (``id_rsa`` an ``id_rsa.pub``), that allow you to log in to the server.

.. image:: /img/user-guide/advanced-guide/backup-ssh/mac/keys-files.png
   :width: 100%
   :align: center
   :alt: Reach SSH keys files

Save those files to secure place (i.e. USB flash drive). If you want to log in into the server from another computer,
you should create the same ``.ssh`` directory by the same path with those ``SSH keys`` inside.

Ubuntu
------

Open a terminal on your PC. Copy public and private keys to the desktop with the following command.

.. code-block:: console

   $ cp ~/.ssh/id_rsa ~/.ssh/id_rsa.pub ~/Desktop/

Then save those files to secure place (i.e. USB flash drive). After backup, these files should be deleted from the desktop for
the security reasons. If you want to log in into the server from another computer, follow commands in case your public and private
keys located on the desktop, being into the terminal on another computer.

.. code-block:: console

   $ mkdir ~/.ssh
   $ mv ~/Desktop/id_rsa ~/Desktop/id_rsa.pub ~/.ssh/
