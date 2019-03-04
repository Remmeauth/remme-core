Two-factor authentication
=========================

If you prefer to :doc:`/user-guide/cloud` then server security should be improved. You should add two-factor authentication
to your server. If you use ``Amazon Web Services`` as a cloud service, follow |google_authenticator_aws| instead of the following section.

.. |google_authenticator_aws| raw:: html

   <a href="https://aws.amazon.com/blogs/startups/securing-ssh-to-amazon-ec2-linux-hosts/" target="_blank">this guide</a>

First of all, install ``Google Authenticator`` (|google_authenticator_app_android|, |google_authenticator_app_ios|) on your mobile phone.
Open the application, click on ``Begin setup`` and be ready to scan the ``QR-code`` with the ``Scan barcode`` button.

.. |google_authenticator_app_android| raw:: html

   <a href="https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2&hl=en" target="_blank">Android</a>

.. |google_authenticator_app_ios| raw:: html

   <a href="https://itunes.apple.com/ru/app/google-authenticator/id388497605?mt=8" target="_blank">iOS</a>

Log in to the server as you previously did during installation of the node:

.. code-block:: console

   $ ssh root@95.179.156.74

The flow is illustrated below.

.. image:: /img/user-guide/advanced-guide/ssh-login-to-the-server.png
   :width: 100%
   :align: center
   :alt: SSH login to the server

Then install and run ``Google Authenticator``:

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

Along with the questions, you will get ``QR-code``, ``secret key``, ``verification code`` and ``emergency scratch codes``. Please,
back up the text data to the secret place on your computer and make a photo or screenshot of the ``QR-code`` so you don’t lose it.

.. image:: /img/user-guide/advanced-guide/2fa-credentials.png
   :width: 100%
   :align: center
   :alt: 2FA QR code

Open your mobile application, use a barcode scanner to scan the prompted  ``QR-code``.

.. image:: /img/user-guide/advanced-guide/2fa-app-on-mobile.png
   :width: 100%
   :align: center
   :alt: 2FA mobile application

Then make the following command to finish setup:

.. code-block:: console

    $ echo "auth required pam_google_authenticator.so nullok" >> /etc/pam.d/sshd && \
          sed -i '/^ChallengeResponseAuthentication/s/no/yes/' /etc/ssh/sshd_config && \
          echo "AuthenticationMethods publickey,password publickey,keyboard-interactive" >> /etc/ssh/sshd_config && \
          sed -i 's/@include common-auth/#@include common-auth/g' /etc/pam.d/sshd && \
          sudo systemctl restart sshd.service

As a result, when you next log in to the server you will be prompted for a verification code from the mobile application.

.. image:: /img/user-guide/advanced-guide/2fa-in-the-action.png
   :width: 100%
   :align: center
   :alt: 2FA QR code
