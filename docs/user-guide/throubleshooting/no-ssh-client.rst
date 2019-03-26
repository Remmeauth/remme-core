No SSH client
=============

Windows
~~~~~~~

If while connecting to the server using ``ssh root@<ip-address>`` command you get the
``ssh is not recognized as an internal or external command...`` error message, it means you have no corresponding software
installed in the operating system.

.. image:: /img/user-guide/troubleshooting/windows-no-ssh-client.png
   :width: 100%
   :align: center
   :alt: No SSH client on Windows

Then open the search and type ``Manage optional features`` and choose it as the best match.

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
