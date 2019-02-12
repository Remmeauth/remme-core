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

The typical command line interface looks like this.

.. code-block:: console

   $ export REMME_CORE_RELEASE=0.6.0-alpha
   $ ./scripts/run.sh -d

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
Typical applications include remote command-line login and remote command execution, but any network service can be secured with ``SSH``.

Visit |what_are_ssh_keys_reference| for more detailed experience with ``SSH``.

.. |what_are_ssh_keys_reference| raw:: html

   <a href="https://jumpcloud.com/blog/what-are-ssh-keys/" target="_blank">this page</a>

Windows
~~~~~~~

You should check for existing SSH keys on your local computer by the ``cd %userprofile%/.ssh`` terminal command.
If you see ``No such file or directory``, then there aren't any existing keys.

If you don't have an existing ``SSH key`` that you wish to use, log in to your local computer as an administrator,
type the terminal command ``ssh-keygen -t rsa -C "your-email@example.com``. Associating the key with your email address
helps you to identify the key later on. Just press ``Enter`` to accept the default location and file name. If the ``.ssh``
directory doesn't exist, the system creates one for you. Enter, and re-enter, a passphrase when prompted.

The whole interaction will look similar to the picture below.

.. image:: /img/user-guide/troubleshooting/ssh-key/windows/ssh-key-generation.png
   :width: 100%
   :align: center
   :alt: SSH-key key generation

To get the ``SSH public key`` use the following commands:

.. code-block:: console

   $ cd %userprofile%/.ssh
   $ clip < id_rsa.pub

The last command will copy it to your buffer, so you can to paste it anywhere.

Ubuntu & Mac OS
~~~~~~~~~~~~~~~

You should check for existing ``SSH keys`` on your local computer by the ``cat ~/.ssh/id_rsa.pub`` terminal command.

.. image:: /img/user-guide/troubleshooting/ssh-key/unix/no-ssh-key-output.png
   :width: 100%
   :align: center
   :alt: No SSH-key output

If you had a ``SSH key``, output would be as illustrated on the picture below:

.. image:: /img/user-guide/troubleshooting/ssh-key/unix/ssh-key-output.png
   :width: 100%
   :align: center
   :alt: SSH-key output

To generate a ``SSH key``, type the terminal command ``ssh-keygen -t rsa -C "your-email@example.com``. Associating the key with your
e-mail address helps you to identify the key later on. Just press ``Enter`` to accept the default location and file name.
If the ``.ssh`` directory doesn't exist, the system creates one for you. Enter, and re-enter, a passphrase when prompted.

The whole interaction will look similar to the picture below.

.. image:: /img/user-guide/troubleshooting/ssh-key/unix/ssh-key-generation.png
   :width: 100%
   :align: center
   :alt: SSH-key key generation
