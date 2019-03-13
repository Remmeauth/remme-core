Forbid root login
=================

If you prefer to :doc:`/user-guide/cloud` then server security should be improved. Login to the server though ``root user``
should be forbidden. If you use ``Amazon Web Services`` as a cloud service, you do not need to create a new user, it is already
created for you and you can log in with name ``ubuntu``, not ``root``.

First of all, login to the server as you previously did during installation of the node:

.. code-block:: console

   $ ssh root@95.179.156.74

The flow is illustrated below.

.. image:: /img/user-guide/advanced-guide/ssh-login-to-the-server.png
   :width: 100%
   :align: center
   :alt: SSH login to the server

Then create a new environment variable with your new user name and add it to the system. You will be required to
create a password for the user, specify some details about the user (you can leave this blank by pressing ``Enter``) and
enter a command to grant your new user access to the server and permit root login.

.. code-block:: console

   $ export USER_NAME=emma
   $ adduser $USER_NAME
   $ curl https://raw.githubusercontent.com/Remmeauth/remme-core/dev/docs/user-guide/templates/sudoers > /etc/sudoers && \
         echo "REMME_CORE_RELEASE=$REMME_CORE_RELEASE" >> /home/$USER_NAME/.bashrc && \
         sed -i "s@username@$USER_NAME@" /etc/sudoers && \
         mkdir /home/$USER_NAME/.ssh && touch /home/$USER_NAME/.ssh/authorized_keys && cat ~/.ssh/authorized_keys > /home/$USER_NAME/.ssh/authorized_keys && \
         chmod 700 /home/$USER_NAME/.ssh && chmod 600 /home/$USER_NAME/.ssh/authorized_keys && \
         sudo chown -R $USER_NAME /home/$USER_NAME/.ssh/ && \
         sed -i '/^PermitRootLogin/s/yes/no/' /etc/ssh/sshd_config && \
         sudo service ssh restart

The expected result of these commands and responses is illustrated below.

.. image:: /img/user-guide/advanced-guide/add-new-server-user-flow.png
   :width: 100%
   :align: center
   :alt: Add new user flow

Then, when you the to log in with ``root user``, you will be forbidden. Login with your new user name instead (like ``ssh emma@95.179.156.74``).

.. image:: /img/user-guide/advanced-guide/forbid-root-login.png
   :width: 100%
   :align: center
   :alt: Forbid root login result
