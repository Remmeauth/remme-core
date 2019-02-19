**************
Advanced guide
**************

Types of node running
=====================

As stated in our guides, during the first run, you need to initialize the genesis (first block on the blockchain)
block with a command ``make run_genesis_bg`` that have run your node in the background mode (no output to the terminal window).

Also there is a bunch of commands, as ``make run_genesis_bg`` you did:

1. ``make stop`` to stop the node.
2. ``make run_genesis`` to run a node in genesis mode not in background.
3. ``make run`` to start a node if you start it not first time, first time start should be a genesis.
4. ``make run_bg`` the same as command above, but run the node in background mode.

Forbid root login
=================

If you prefer :doc:`/user-guide/cloud` then server security should be improved. Log in to the server though ``root user``
should be forbidden. If you use ``Amazon Web Services`` as a cloud service, you do not need to create a new user, it is already
created for you, you log in with name ``ubuntu``, not ``root``.

First of all, login to the server as you already did before during installation of the node:

.. code-block:: console

   $ ssh root@95.179.156.74

The flow is illustrated below.

.. image:: /img/user-guide/advanced-guide/ssh-login-to-the-server.png
   :width: 100%
   :align: center
   :alt: SSH login to the server

Then create a new environment variable with your new user name and add it to the system. You will be required to
create a password for the user, specify some details about the user (you can leave it blank by pressing ``Enter``) and make
command to grand your new user access to the server and permit root login on.

.. code-block:: console

   $ export USER_NAME=emma
   $ adduser $USER_NAME
   $ curl https://gist.githubusercontent.com/dmytrostriletskyi/08adaddeba05ee7efae5954559533453/raw/994cba5066018489f4786aefb3a150cdd8fe7096/sudoers > /etc/sudoers && \
         sed -i "s@username@$USER_NAME@" /etc/sudoers && \
         mkdir /home/$USER_NAME/.ssh && touch /home/$USER_NAME/.ssh/authorized_keys && cat ~/.ssh/authorized_keys > /home/$USER_NAME/.ssh/authorized_keys && \
         chmod 700 /home/$USER_NAME/.ssh && chmod 600 /home/$USER_NAME/.ssh/authorized_keys && \
         sudo chown -R $USER_NAME /home/$USER_NAME/.ssh/ && \
         sed -i '/^PermitRootLogin/s/yes/no/' /etc/ssh/sshd_config && \
         sudo service ssh restart

The expected result of the commands and responses is illustrated below.

.. image:: /img/user-guide/advanced-guide/add-new-server-user-flow.png
   :width: 100%
   :align: center
   :alt: Add new user flow

Then when you log in with ``root user``, you will be forbidden. Login with your new user name instead (as like ``ssh emma@95.179.156.74``).

.. image:: /img/user-guide/advanced-guide/forbid-root-login.png
   :width: 100%
   :align: center
   :alt: Forbid root login result


Two-factor authentication
=========================

If you prefer :doc:`/user-guide/cloud` then server security should be improved. You should add two-factor authentication
to your server. If you use ``Amazon Web Services`` as a cloud service, follow |google_authenticator_aws| instead of the following section.

.. |google_authenticator_aws| raw:: html

   <a href="https://aws.amazon.com/blogs/startups/securing-ssh-to-amazon-ec2-linux-hosts/" target="_blank">this guide</a>

First of all, install ``Google authenticator`` (|google_authenticator_app_android|, |google_authenticator_app_ios|) on your mobile phone.
Open application, click on ``Begin setup`` and be ready to scan ``QR-code`` with ``Scan barcode`` button.

.. |google_authenticator_app_android| raw:: html

   <a href="https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2&hl=en" target="_blank">Andriod</a>

.. |google_authenticator_app_ios| raw:: html

   <a href="https://itunes.apple.com/ru/app/google-authenticator/id388497605?mt=8" target="_blank">IOS</a>

Log in to the server as you already did before during installation the node:

.. code-block:: console

   $ ssh root@95.179.156.74

The flow is illustrated below.

.. image:: /img/user-guide/advanced-guide/ssh-login-to-the-server.png
   :width: 100%
   :align: center
   :alt: SSH login to the server

Then install and run ``Google authenticator``:

.. code-block:: console

   $ sudo apt-get update && sudo apt-get install libpam-google-authenticator -y && \
         google-authenticator

After installation you will be required to answer several questions:

1. ``Do you want authentication tokens to be time-based (y/n)`` ``y``
2. ``Do you want me to update your "~/.google_authenticator" file (y/n)`` ``y``
3. ``Do you want to disallow ... notice or even prevent man-in-the-middle attacks (y/n)`` ``y``
4. ``By default, tokens are good for 30 seconds and in ... do you want to do so (y/n)`` ``n``
5. ``If the computer that you are ... do you want to enable rate-limiting (y/n)`` ``y``

.. image:: /img/user-guide/advanced-guide/2fa-qr-code.png
   :width: 100%
   :align: center
   :alt: 2FA QR code

Along with questions, you will get ``QR-code``, ``secret key``, ``verification code`` and ``emergency scratch codes``. Please,
back text data to the secret place on your computer and make a photo or screenshot of ``QR-code`` to do not lose it.

.. image:: /img/user-guide/advanced-guide/2fa-credentials.png
   :width: 100%
   :align: center
   :alt: 2FA QR code

Open your mobile application, use scanning the barcode make the scan of the prompted ``QR-code``.

.. image:: /img/user-guide/advanced-guide/2fa-app-on-mobile.png
   :width: 100%
   :align: center
   :alt: 2FA mobile application

Then make the following command to finish the setup:

.. code-block:: console

    $ echo "auth required pam_google_authenticator.so nullok" >> /etc/pam.d/sshd && \
          sed -i '/^ChallengeResponseAuthentication/s/no/yes/' /etc/ssh/sshd_config && \
          echo "AuthenticationMethods publickey,password publickey,keyboard-interactive" >> /etc/ssh/sshd_config && \
          sed -i 's/@include common-auth/#@include common-auth/g' /etc/pam.d/sshd && \
          sudo systemctl restart sshd.service

As a result, if you will do the next login to the server you will be required to prompt verification code from the mobile application.

.. image:: /img/user-guide/advanced-guide/2fa-in-the-action.png
   :width: 100%
   :align: center
   :alt: 2FA QR code
