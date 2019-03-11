***************
Troubleshooting
***************

Troubleshooting is a form of problem solving, often applied to repair failed products or processes on a machine or a system.
Troubleshooting is needed to identify the symptoms. Determining the most likely cause allows to eliminate the potential
causes of a problem.

Command line notation
=====================

Throughout the documentation, we’ll show some commands used in the terminal. Lines that you should enter in a terminal all start with ``$``.
You don’t need to type in the ``$`` character, it indicates the start of each command. Lines that don’t start with ``$`` typically show
the output of the previous command.

The typical command line interface looks like this. There two separated commands, so you should enter it one by one.

.. code-block:: console

   $ export REMME_CORE_RELEASE=0.7.0-alpha
   $ sudo make run_bg

Nodes network
=============

As of now, it’ is impossible to connect your own node to the test network. All nodes that you run will work on your own network.

Open terminal
=============

Windows 8
~~~~~~~~~

Swipe up to show the ``Apps screen``. You can accomplish the same thing with a mouse by clicking on the down arrow
icon at the bottom of the screen. Prior to the ``Windows 8.1`` update, the ``Apps screen`` can be accessed from the
``Start screen`` by swiping up from the bottom of the screen, or right-clicking anywhere, and then choosing ``All apps``.

Now that you're on the Apps screen, swipe or scroll to the right and locate the ``Windows System`` section heading.

Under ``Windows System``, tap or click ``Command Prompt``. A new ``Command Prompt`` window will open on the ``Desktop``.

.. image:: /img/user-guide/troubleshooting/open-terminal/windows/windows-8-apps-screen.gif
   :width: 100%
   :align: center
   :alt: Open terminal with Apps screen

Windows 10
~~~~~~~~~~

Select the ``Start button``. Type ``cmd``. Click or tap ``Command Prompt`` from the list.

.. image:: /img/user-guide/troubleshooting/open-terminal/windows/windows-10-search.png
   :width: 100%
   :align: center
   :alt: Open terminal with search

Ubuntu 16.04
~~~~~~~~~~~~

Probably one of the easiest and fastest ways to open a terminal on ``Ubuntu 16.04`` is by using a keyboard shortcut ``CTRL+ALT+T``.

The second easiest way is to open your command line terminal by right-clicking the desktop screen and selecting ``Open Terminal`` from the presented drop-down menu.

.. image:: /img/user-guide/troubleshooting/open-terminal/ubuntu-16.04/right-click.png
   :width: 100%
   :align: center
   :alt: Open terminal with right clock

Probably, the most obvious way to open a terminal on ``Ubuntu 16.04`` is to navigate to dash and search for a terminal.

.. image:: /img/user-guide/troubleshooting/open-terminal/ubuntu-16.04/dash-search.png
   :width: 100%
   :align: center
   :alt: Open terminal with dash search

Ubuntu 18.04
~~~~~~~~~~~~

The simplest way to open a terminal window on ``Ubuntu 18.04`` is to use the shortcut ``CTRL+ALT+T``.

Click on ``Activities`` on the left top corner. Type ``terminal`` in search line. Once the terminal icon appears simply left-click on it to open it on ``Ubuntu``.

.. image:: /img/user-guide/troubleshooting/open-terminal/ubuntu-18.04/activities.png
   :width: 100%
   :align: center
   :alt: Open terminal with Activities

Another easy way to open ``Terminal`` on ``Ubuntu 18.04`` is to right click on the desktop and choose ``Open Terminal`` from the menu.

.. image:: /img/user-guide/troubleshooting/open-terminal/ubuntu-18.04/right-click.png
   :width: 100%
   :align: center
   :alt: Open terminal with right click

MacOS
~~~~~

To open a terminal on the MacOS, on the desktop go to ``Finder`` → ``Go`` → ``Utilities``.

.. image:: /img/user-guide/troubleshooting/open-terminal/mac-os/finder-utilities.png
   :width: 100%
   :align: center
   :alt: Finder utilities button

Find the application called ``Terminal``.

.. image:: /img/user-guide/troubleshooting/open-terminal/mac-os/find-terminal-app.png
   :width: 100%
   :align: center
   :alt: Find terminal application

Double-click it to get the same result.

.. image:: /img/user-guide/troubleshooting/open-terminal/mac-os/terminal-window.png
   :width: 100%
   :align: center
   :alt: Terminal window screen

During the installation you may be required to open two terminal windows, so in terminal application go to ``Shell`` → ``New Window`` → ``New Window with Profile``.

.. image:: /img/user-guide/troubleshooting/open-terminal/mac-os/open-yet-one-window-button.png
   :width: 100%
   :align: center
   :alt: Open yer one terminal window button

And you will get the same result.

.. image:: /img/user-guide/troubleshooting/open-terminal/mac-os/two-terminal-windows.png
   :width: 100%
   :align: center
   :alt: Two terminal windows screen

Install Docker
==============

Mac OS
~~~~~~

Visit |page_to_download_docker| to download ``Docker`` from the official website. Downloading requires an account registration.

.. |page_to_download_docker| raw:: html

   <a href="https://hub.docker.com/editions/community/docker-ce-desktop-mac" target="_blank">this page</a>

.. image:: /img/user-guide/troubleshooting/install-docker/mac-os/download-docker.png
   :width: 100%
   :align: center
   :alt: Download Docker

After an installation, double-click ``Docker.dmg`` to open the installer, then drag ``Moby the whale`` to the ``Applications`` folder.

.. image:: /img/user-guide/troubleshooting/install-docker/mac-os/drag-and-drop.png
   :width: 100%
   :align: center
   :alt: Drag Docker application icon to Apps

Double-click ``Docker`` in the ``Applications`` folder to start ``Docker``. In the example below, the ``Applications folder`` is in ``grid`` view mode.

.. image:: /img/user-guide/troubleshooting/install-docker/mac-os/docker-app-icon.png
   :width: 100%
   :align: center
   :alt: Find Docker application icon in Apps

You are prompted to authorize ``Docker`` with your system password after you launch it. Privileged access is needed to
install networking components and links to the Docker apps.

The whale in the top status bar indicates that ``Docker`` is running, and accessible from a terminal.

.. image:: /img/user-guide/troubleshooting/install-docker/mac-os/whale-in-menu-bar.png
   :width: 100%
   :align: center
   :alt: Find Docker legend, whale, in the menu bar

If the installation is done, you will see the message with the next steps and a link to the documentation. You don’t need
to log in to the popup for further ``Remme-core`` usage. Click the whale (whale menu) in the status bar to dismiss this popup.

.. image:: /img/user-guide/troubleshooting/install-docker/mac-os/docker-is-installed.png
   :width: 100%
   :align: center
   :alt: Image says docker is installed on PC

Visit |official_install_docker_on_mac_tutorial| for more detailed experience with ``Docker``.

.. |official_install_docker_on_mac_tutorial| raw:: html

   <a href="https://docs.docker.com/docker-for-mac/install/" target="_blank">official install Docker on Mac OS tutorial</a>

SSH key
=======

``Secure Shell (SSH)`` is a cryptographic network protocol for operating network services securely over an unsecured network.
Typical applications include remote command line login and remote command execution, but any network service can be secured with ``SSH``.

Visit |what_are_ssh_keys_reference| for more details on using ``SSH``.

.. |what_are_ssh_keys_reference| raw:: html

   <a href="https://jumpcloud.com/blog/what-are-ssh-keys/" target="_blank">this page</a>

Windows
~~~~~~~

You should check for existing ``SSH keys`` on your local computer using the following terminal command.

.. code-block:: console

   $ cd %userprofile%/.ssh
   The system cannot find the path specified.

The flow is illustrated below.

.. image:: /img/user-guide/troubleshooting/ssh-key/windows/ssh-key-does-not-exist.png
   :width: 100%
   :align: center
   :alt: SSH key does not exist on Windows

If you see ``The system cannot find the path specified.`` or a similar output it means you do not have ``SSH keys``.
If you haven't gotten any output it means you already have ``SSH keys``, in which case go to the text that describes
how to get your ``SSH keys``.

To create ``SSH keys``, use the following terminal command. Remember to change ``your-email@example.com`` with your e-mail.

.. code-block:: console

   $ ssh-keygen -t rsa -C "your-email@example.com"

Then you will see the following text — just press ``Enter``.

.. code-block:: console

   Generation public/private rsa key pair.
   Enter file in which to save to key (C:\User\user\.ssh\id_rsa):

Then you will be required to create the password for your ``SSH keys``. Note that when you do so, the password
doesn't appear – even stars or bullets shouldn’t appear as you wait to log in to the account on the operating system.
Type in the password and press ``Enter``.

.. code-block:: console

   Enter passphrase (empty for no passphrase):
   Enter same passphrase again:

The following text means you have successfully created the ``SSH keys``.

.. code-block:: console

   Your identification has been saved in C:\User\user\.ssh\id_rsa.
   Your public key has been saved in C:\User\user\.ssh\id_rsa.pub.
   The key fingerprint is:
   SHA256:VyenJasdadYDwUo/b0oK3dsfgsdRIJftVU your-email@example.com
   The key's randomart image is:
    +---[RSA 2048]----+
    |       ..*E=+    |
    |      o =o*o     |
    | .   . + .+B+ o  |
    |. . o .  .o===   |
    | . +   .S.oo.o   |
    |  . + . +.o o    |
    |   o = . + .     |
    |    = o +   .    |
    |   . . o ..o.    |
    +----[SHA256]-----+

The whole interaction will look similar to the picture below.

.. image:: /img/user-guide/troubleshooting/ssh-key/windows/ssh-key-generation.png
   :width: 100%
   :align: center
   :alt: SSH-key key generation on Widnows

Now you need to look out your ``SSH public key``. We will use the ``clip`` tool. When you use this tool in the terminal,
it copies the body of the file (in our case the body of the public key) to the clipboard. The clipboard is the buffer
you can use to paste the copied text from by pressing the ``Ctrl + v`` key combination.

Copy the body of the public key using the following terminal commands (no output afterward):

.. code-block:: console

   $ cd %userprofile%/.ssh
   $ clip < id_rsa.pub

The flow is illustrated below.

.. image:: /img/user-guide/troubleshooting/ssh-key/windows/copy-to-clip-ssh-key.png
   :width: 100%
   :align: center
   :alt: Copy SSH key to clip

Then open a brand new ``Word document``, click on the right mouse button and choose the ``Paste`` option
(or just press ``Ctrl + v`` key combination).

.. image:: /img/user-guide/troubleshooting/ssh-key/windows/paste-ssh-key-to-word-doc.png
   :width: 100%
   :align: center
   :alt: Paste SSH key to word docs

The result is illustrated below.

.. image:: /img/user-guide/troubleshooting/ssh-key/windows/pasted-ssh-key-to-word-doc.png
   :width: 100%
   :align: center
   :alt: Pasted SSH key to word docs

Now you can use the commands above to copy and paste your ``SSH public key``.

Ubuntu & Mac OS
~~~~~~~~~~~~~~~

You should check for existing ``SSH keys`` on your local computer using the following terminal command.

.. code-block:: console

   $ cat ~/.ssh/id_rsa
   cat: /Users/dmytrostriletskyi/.ssh/id_rsa: No such file or directory

If you see ``No such file or directory.`` or a similar output it means you do not have the ``SSH keys``.
If you have gotten the following output it means you already have ``SSH keys``, so just copy and paste it where required.

.. code-block:: console

   $ cat ~/.ssh/id_rsa
   ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCt0Or7UEedfyEo4wgaSVI0oHh26Bt88BNiEYwf8I1KnUYoyckGH0shmabMFFGW3MjYrpMJR6lm9L5+
   JCf5ENSzPy2w69MidC8jKYlzFeFnKqQ9rNJ/2hXHXKrs24+7wicy5Mab96HpEXbFvIilvXyGBUdqarmUElg/lHCNTCJVGfAgjPjfjO6iI8MQhkSEPzHO
   0owIRI1fHejnlNWEiL7X4Yb3Q/vQAz43ydc2fvGkSoKQJ8KuUPD56vKnbuMxB9NsDMss5KKj4q2YkO24H0Vs3xuEmHc0pcDfoAw9RPlr+3t2pzlyvGVT
   SRZ+l5Yjm2oJZlc3uSjVPg3tIsAmedXy4a9pahKq9i6BQBWe8oXJdoRsg/Nn8dtXUIVhGLud9PLNeFmVa1M/uMGJmR8zhuG/c3m5EBUZRKe0vOqQh9dk
   Br0spp/KuzPX1C6ljhrQbFdFXoUQIocF/YMiZ+E/zA3qBjR4Le57CsMdiY6YylXAZOMTMMZUZSyONr9BmlRt3pEgYKnkRpnhg0Jx/GdC8SiZ+Mpx4RM5
   /tbt3chmjIlYfm6TDfWTeQhCA2gXsjrx9Fi8zrwzk1WEFLT+nRigL/2Lh+ruB9E6Rg5E4cpj1NCxJ/gGlLlLRFYkJwLtrAZhat+AWqmAtdXWYvCVSw6K
   u9o7K2gcE9RlQrg6HS6KSUON1w== dmytro.striletskyi@gmail.com

To create ``SSH keys``, use the following terminal command. Remember to change ``your-email@example.com`` to your e-mail.

.. code-block:: console

   $ ssh-keygen -t rsa -C "your-email@example.com"

You will then see the following text — just press ``Enter``.

.. code-block:: console

   Generation public/private rsa key pair.
   Enter file in which to save to key (/Users/dmytrostriletskyi/.ssh/id_rsa):

Then you will be required to create the password for your ``SSH keys``. Mind that when you do it the password
doesn't appear – even stars or bullets shouldn’t appear as you wait to log in to the account on the operating system.
Type in the password and press ``Enter``.

.. code-block:: console

   Enter passphrase (empty for no passphrase):
   Enter same passphrase again:

The following text means you have successfully created the ``SSH keys``.

.. code-block:: console

   Your identification has been saved in /Users/dmytrostriletskyi/.ssh/id_rsa.
   Your public key has been saved in /Users/dmytrostriletskyi/.ssh/id_rsa.pub.
   The key fingerprint is:
   SHA256:VyenJasdadYDwUo/b0oK3dsfgsdRIJftVU your-email@example.com
   The key's randomart image is:
    +---[RSA 2048]----+
    |       ..*E=+    |
    |      o =o*o     |
    | .   . + .+B+ o  |
    |. . o .  .o===   |
    | . +   .S.oo.o   |
    |  . + . +.o o    |
    |   o = . + .     |
    |    = o +   .    |
    |   . . o ..o.    |
    +----[SHA256]-----+

The whole interaction will look similar to the picture below.

.. image:: /img/user-guide/troubleshooting/ssh-key/unix/ssh-key-generation.png
   :width: 100%
   :align: center
   :alt: SSH-key key generation

No SSH client
=============

Windows
~~~~~~~

If while connecting to the server using ``ssh root@<ip-address>`` command you get the
``ssh is not recognized as an internal or external command...`` error message, it means you have no corresponding software
in the operating system installed.

.. image:: /img/user-guide/troubleshooting/windows-no-ssh-client.png
   :width: 100%
   :align: center
   :alt: No SSH client on Windows

Then open the search and type ``Manage optional features`` and choose it in the best match.

.. image:: /img/user-guide/troubleshooting/windows-manage-option-features.png
   :width: 100%
   :align: center
   :alt: No SSH client on Windows

In the opened windows click on the ``Add a feature`` button.

.. image:: /img/user-guide/troubleshooting/windows-add-option-features.png
   :width: 100%
   :align: center
   :alt: No SSH client on Windows

Find the ``OpenSSH client`` and click on the button named ``Install``.

.. image:: /img/user-guide/troubleshooting/windows-install-ssh-client.png
   :width: 100%
   :align: center
   :alt: No SSH client on Windows

When the installation has been finished, try to connect to the server again.
