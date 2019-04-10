Admin panel
===========

Change password
---------------

Until the admin panel does not cover all node's user requirements, there is only an ability to change the admin panel's password
through terminal commands. Being logged in the server, set your secure password to the environment variable as
illustrated below (change ``73g909iogdy78];][[;,o290hb`` to your password).

.. code-block:: console

   $ export NEW_ADMIN_PANEL_PASSWORD='73g909iogdy78];][[;,o290hb'

Then apply the changes with the following command:

.. code-block:: console

   $ sudo make stop && \
         sudo -i sed -i "s@ADMIN_PASSWORD=remme@ADMIN_PASSWORD=$NEW_ADMIN_PANEL_PASSWORD@" /home/remme-core-$REMME_CORE_RELEASE/config/admin.env && \
         unset NEW_ADMIN_PANEL_PASSWORD && \
         sudo make run_bg_user

For now, you can log in to the admin panel with the new password.
