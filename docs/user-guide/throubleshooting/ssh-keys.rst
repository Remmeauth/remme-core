.. _SshKeysThroubleshooting:

SSH keys
========

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

To create ``SSH keys``, use the following terminal command. Remember to change ``your-email@example.com`` with your email.

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

   $ cat ~/.ssh/id_rsa.pub
   cat: /Users/dmytrostriletskyi/.ssh/id_rsa: No such file or directory

If you see ``No such file or directory.`` or a similar output it means you do not have the ``SSH keys``.
If you have gotten the following output it means you already have ``SSH keys``, so just copy and paste it where required.

.. code-block:: console

   $ cat ~/.ssh/id_rsa.pub
   ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCt0Or7UEedfyEo4wgaSVI0oHh26Bt88BNiEYwf8I1KnUYoyckGH0shmabMFFGW3MjYrpMJR6lm9L5+
   JCf5ENSzPy2w69MidC8jKYlzFeFnKqQ9rNJ/2hXHXKrs24+7wicy5Mab96HpEXbFvIilvXyGBUdqarmUElg/lHCNTCJVGfAgjPjfjO6iI8MQhkSEPzHO
   0owIRI1fHejnlNWEiL7X4Yb3Q/vQAz43ydc2fvGkSoKQJ8KuUPD56vKnbuMxB9NsDMss5KKj4q2YkO24H0Vs3xuEmHc0pcDfoAw9RPlr+3t2pzlyvGVT
   SRZ+l5Yjm2oJZlc3uSjVPg3tIsAmedXy4a9pahKq9i6BQBWe8oXJdoRsg/Nn8dtXUIVhGLud9PLNeFmVa1M/uMGJmR8zhuG/c3m5EBUZRKe0vOqQh9dk
   Br0spp/KuzPX1C6ljhrQbFdFXoUQIocF/YMiZ+E/zA3qBjR4Le57CsMdiY6YylXAZOMTMMZUZSyONr9BmlRt3pEgYKnkRpnhg0Jx/GdC8SiZ+Mpx4RM5
   /tbt3chmjIlYfm6TDfWTeQhCA2gXsjrx9Fi8zrwzk1WEFLT+nRigL/2Lh+ruB9E6Rg5E4cpj1NCxJ/gGlLlLRFYkJwLtrAZhat+AWqmAtdXWYvCVSw6K
   u9o7K2gcE9RlQrg6HS6KSUON1w== dmytro.striletskyi@gmail.com

To create ``SSH keys``, use the following terminal command. Remember to change ``your-email@example.com`` to your email.

.. code-block:: console

   $ ssh-keygen -t rsa -C "your-email@example.com"

You will then see the following text — just press ``Enter``.

.. code-block:: console

   Generation public/private rsa key pair.
   Enter file in which to save to key (/Users/dmytrostriletskyi/.ssh/id_rsa):

Then you will be required to create the password for your ``SSH keys``. Mind that when you do this the password
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
