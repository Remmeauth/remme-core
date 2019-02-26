**************
Advanced guide
**************

Types of node running
=====================

As stated in our guides, during the first run, you need to initialize the genesis (first block on the blockchain)
block with a command ``make run_genesis_bg`` that have run your node in the background mode (no application output to the terminal window).

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


Domain name for node
====================

GoDaddy
-------

Visit the |registration_link| to create your own account on ``GoDaddy``.

.. |registration_link| raw:: html

   <a href="https://sso.godaddy.com/?app=account" target="_blank">registration link</a>

.. image:: /img/user-guide/dns/godaddy/create-account.png
   :width: 100%
   :align: center
   :alt: Create GoDaddy account

Open your inbox, select the confirmation letter from ``GoDaddy`` and click on the button ``Verify Email Now``.

.. image:: /img/user-guide/dns/godaddy/verify-account-via-inbox.png
   :width: 100%
   :align: center
   :alt: Create GoDaddy account

Click on |your_godaddy_products| that will open your ``GoDaddy`` products, where you can start buying a domain for the node.
Enter preferred domain name (i.e. ``the-coolest-masternode``) and click on the search icon.

.. image:: /img/user-guide/dns/godaddy/enter-domain-name.png
   :width: 100%
   :align: center
   :alt: Enter preferred domain name

After entering the domain name you will be redirected to the page that shows if your preferred domain name is free.
If the domain name isn't free, choose the similar one which ``GoDaddy`` will suggest for you. When you finish choosing the
right domain name, press ``Add to Cart`` and ``Continue to Cart``.

.. image:: /img/user-guide/dns/godaddy/add-domain-to-cart.png
   :width: 100%
   :align: center
   :alt: Add domain to cart

You may want to hide information about you with the following feature. Please, visit |full_domain_privacy_and_protection| before making the decision.
Otherwise, check the ``No Thanks`` checkbox.

.. |full_domain_privacy_and_protection| raw:: html

   <a href="https://www.godaddy.com/domains/full-domain-privacy-and-protection#privacy" target="_blank">according documentation</a>

.. image:: /img/user-guide/dns/godaddy/no-privacy-feature.png
   :width: 100%
   :align: center
   :alt: No privacy feature

Then leave the checkbox ``Start your website FREE`` empty. You also could create an e-mail address that matches your domain, but it will
charge an additional cost. E-mail address isn't required to setup the node.

.. image:: /img/user-guide/dns/godaddy/no-default-start-website.png
   :width: 100%
   :align: center
   :alt: Enter default website starting

Enter your billing details into the form to pay for the domain. Choose a preferred certificate validity.

.. image:: /img/user-guide/dns/godaddy/billing-information.png
   :width: 100%
   :align: center
   :alt: Enter billing information

Enter your credit/debit details into the form to pay for the domain.

.. image:: /img/user-guide/dns/godaddy/payment-information.png
   :width: 100%
   :align: center
   :alt: Enter payment information

Complete purchase with big green button ``Complete Purchase``.

.. image:: /img/user-guide/dns/godaddy/complete-purchase.png
   :width: 100%
   :align: center
   :alt: Complete purchase

Click on |your_godaddy_products| that will open your ``GoDaddy`` products, where you can start linking your domain name to the server.
Then click on button ``DNS``.

.. |your_godaddy_products| raw:: html

   <a href="https://account.godaddy.com/products/" target="_blank">this link</a>

.. image:: /img/user-guide/dns/godaddy/domain-dns-settings.png
   :width: 100%
   :align: center
   :alt: Domain DNS settings

Click on the ``pencil`` right away of the row where a type is ``A``, so the first row.

.. image:: /img/user-guide/dns/godaddy/edit-a-type.png
   :width: 100%
   :align: center
   :alt: Edit A type

Change ``Points to`` to the your server/instance/droplet ``IP address`` and click ``Save``.

.. image:: /img/user-guide/dns/godaddy/point-a-type-to-ip-address.png
   :width: 100%
   :align: center
   :alt: Point A type to the IP address

Wait a few minutes, this operation takes time. Then you can ensure your domain name is linked to the server.
First of all, send to request to the server by its ``IP-address``. Remember to change ``95.179.156.74`` to your server ``IP address``.

.. code-block:: console

   $ export NODE_IP_ADDRESS=95.179.156.74
   $ curl -X POST http://$NODE_IP_ADDRESS:8080 -H 'Content-Type: application/json' -d \
         '{"jsonrpc":"2.0","id":"11","method":"get_node_config","params":{}}' | python -m json.tool


Change the value of ``NODE_IP_ADDRESS`` to your domain name with extension (i.e. ``the-coolest-masternode.xyz``) and send the
same request which should response similar to the previous one:

.. code-block:: console

   $ export NODE_IP_ADDRESS=the-coolest-masternode.xyz
   $ curl -X POST http://$NODE_IP_ADDRESS:8080 -H 'Content-Type: application/json' -d \
         '{"jsonrpc":"2.0","id":"11","method":"get_node_config","params":{}}' | python -m json.tool

The flow is illustrated below.

.. image:: /img/user-guide/dns/godaddy/proof-domain-name-works.png
   :width: 100%
   :align: center
   :alt: Proof domain name works

SSL certificate for node
========================

**SSL Certificates** are small data files that digitally bind a cryptographic key to an organization's details.
When installed on a web server, it activates the padlock and the https protocol and allows secure connections from a
web server to a browser.

Let's Encrypt
-------------

**Let's Encrypt** is a non-profit certificate authority that provides ``X.509 certificates`` for ``Transport Layer Security`` (TLS) encryption at no charge.

First of all, login to the server as you already did before during installation the node. Remember to change ``157.230.146.230`` to your server ``IP address``:

.. code-block:: console

   $ ssh root@157.230.146.230

The flow is illustrated below.

.. image:: /img/user-guide/advanced-guide/ssh-login-to-the-server.png
   :width: 100%
   :align: center
   :alt: SSH login to the server

Then create a new environment variable with your ``domain name`` as illustrated below.

.. code-block:: console

   $ export DOMAIN=the-coolest-masternode.xyz

Then create a new environment variable with your ``e-mail`` to receive notifications from ``Let's Encrypt``:

.. code-block:: console

   $ export EMAIL=dmytro.striletskyi@gmail.com

Copy commands below and paste it into the terminal, it will create ``SSL certificate`` and up the web-server to serve ``https`` connections.

.. code-block:: console

   $ sudo apt install software-properties-common -y && \
         sudo add-apt-repository ppa:certbot/certbot -y && \
         sudo apt update && \
         sudo apt install certbot nginx python-certbot-nginx -y && \
         sudo certbot run --nginx -d $DOMAIN --non-interactive --agree-tos -m $EMAIL && \
         curl https://gist.githubusercontent.com/dmytrostriletskyi/cce03d2aca0e2eaae3b8555eff252c0b/raw/74b9d1e33d30c35cbe3f51c8521143807b51880b/nginx.conf > /etc/nginx/nginx.conf && \
         sed -i "s@websitenamewithdomain@$DOMAIN@" /etc/nginx/nginx.conf && \
         sudo systemctl restart nginx && \
         echo "* * * * * $USER /usr/bin/certbot renew" >> /etc/crontab

To check if your node has completed a correct ``SSL certificate`` setup, open a brand new terminal window on the local machine
and send a ``https`` request to get node configurations. Change value of ``NODE_IP_ADDRESS`` to your domain name with
extension (i.e. ``the-coolest-masternode.xyz``).

.. code-block:: console

   $ export NODE_IP_ADDRESS=the-coolest-masternode.xyz
   $ curl -X POST https://$NODE_IP_ADDRESS -H 'Content-Type: application/json' -d \
         '{"jsonrpc":"2.0","id":"11","method":"get_node_config","params":{}}' | python -m json.tool

The flow is illustrated below.

.. image:: /img/user-guide/ca/comodo/proof-node-works-https.png
   :width: 100%
   :align: center
   :alt: Proof node works over HTTPS

Comodo
------

Visit the |comodo_ssl_store| to buy a ``SSL certificate``. Choose ``PositiveSSL (DV)`` and press ``ADD TO CART``.

.. |comodo_ssl_store| raw:: html

   <a href="https://comodosslstore.com/" target="_blank">Comodo SSL store</a>

.. image:: /img/user-guide/ca/comodo/ssl-certificates-list.png
   :width: 100%
   :align: center
   :alt: SSL certificates list

Choose ``1 year`` and ``1 quantity``, other options to ``No``, then press ``ADD TO CART``.

.. image:: /img/user-guide/ca/comodo/shopping-cart.png
   :width: 100%
   :align: center
   :alt: Shopping cart

Enter your billing and card information, then press ``COMPLETE ORDER``.

.. image:: /img/user-guide/ca/comodo/billing-information.png
   :width: 100%
   :align: center
   :alt: Billing information

Verify you have bought a right ``SSL certificate`` and press ``PLACE ORDER``.

.. image:: /img/user-guide/ca/comodo/card-information.png
   :width: 100%
   :align: center
   :alt: Card information

Then press ``COMPLETE ORDER``.

.. image:: /img/user-guide/ca/comodo/complete-order.png
   :width: 100%
   :align: center
   :alt: Complete order

When your purchase has been processed, you can generate a certificate by ``GENERATE CERT NOW`` button.

.. image:: /img/user-guide/ca/comodo/generate-cert-now.png
   :width: 100%
   :align: center
   :alt: Generate certificate now

You will get additional certificate settings. Check ``New`` for an order type, ``No`` for the ``switching from another SSL brand`` option.

.. image:: /img/user-guide/ca/comodo/order-1-2.png
   :width: 100%
   :align: center
   :alt: Order 1-2

``HTTP File-based`` for an automated authentication option.

.. image:: /img/user-guide/ca/comodo/order-3.png
   :width: 100%
   :align: center
   :alt: Order 3

Then switch to the terminal. Log in to the server as you already did before during installation the node:

.. code-block:: console

   $ ssh root@95.179.156.74

The flow is illustrated below.

.. image:: /img/user-guide/advanced-guide/ssh-login-to-the-server.png
   :width: 100%
   :align: center
   :alt: SSH login to the server

Generate ``OpenSSL`` keys for your server with the following command:

.. code-block:: console

    $ openssl req -new -newkey rsa:2048 -nodes -keyout server.key -out server.csr

The only one you required to enter is a domain name with extension (i.e. ``the-coolest-masternode.xyz``) to the according
fields named ``Common Name``. The flow is illustrated below.

.. image:: /img/user-guide/ca/comodo/generate-openssl-keys.png
   :width: 100%
   :align: center
   :alt: Generate OpenSSL keys

Print ``certificate signing request`` with the according command that is required for ``Comodo``.

.. code-block:: console

    $ cat server.csr

The flow is illustrated below.

.. image:: /img/user-guide/ca/comodo/cat-csr.png
   :width: 100%
   :align: center
   :alt: Cat CSR

And input it to the corresponding form.

.. image:: /img/user-guide/ca/comodo/input-csr.png
   :width: 100%
   :align: center
   :alt: Input CSR

Leave choice ``No`` for a ``Free HackerGuargian PCI scanning`` and ``Free HackerProof Trust Mark``. Choose ``Other`` for
the ``Select Your Server`` field. Then press ``CONTINUE``

.. image:: /img/user-guide/ca/comodo/order-5-6-7.png
   :width: 100%
   :align: center
   :alt: Order 5-6-7

On the next page, use ``account details`` as the default option for ``site administrator``.

.. image:: /img/user-guide/ca/comodo/order-4.png
   :width: 100%
   :align: center
   :alt: Order 4

Use ``account details`` as the default option for ``technical contact`` option.

.. image:: /img/user-guide/ca/comodo/order-4.1.png
   :width: 100%
   :align: center
   :alt: Order 4.1

Read the agreement and mark the checkbox below after completion.

.. image:: /img/user-guide/ca/comodo/order-agreement.png
   :width: 100%
   :align: center
   :alt: Order agreement

Then press ``CONTINUE``.

.. image:: /img/user-guide/ca/comodo/finish-order.png
   :width: 100%
   :align: center
   :alt: Finish order

Download ``auth file``.

.. image:: /img/user-guide/ca/comodo/download-auth-file.png
   :width: 100%
   :align: center
   :alt: Download auth file

And using brand new terminal window being on the local machine transfer the file to the server.

.. code-block:: console

    $ scp ~/Desktop/459F5867C44CDB4551D93938E8116D3E.txt root@157.230.226.218:/

Then open a terminal window with the server and copy and paste the command below. If you use ``Windows``, change word
``export`` to ``set`` and install (download an archive and open it) |curl_tool| to send a request the node in father steps.

.. code-block:: console

   $ sudo apt-get update && sudo apt-get install nginx -y && \
         cd / && COMODO_AUTH_FILE=$(ls *.txt) && COMODO_AUTH_FILE_NAME=${COMODO_AUTH_FILE%.*} && \
         mkdir /var/www/comodo/ && mv /$COMODO_AUTH_FILE_NAME.txt /var/www/comodo/ && \
         curl https://gist.githubusercontent.com/dmytrostriletskyi/d5e66f4969bf081fb906d714dfbfda6b/raw/161be759469b9b6fad6f72b9702b943056051ce9/nginx.conf > /etc/nginx/nginx.conf && \
         sed -i "s@comodohashfile@$COMODO_AUTH_FILE_NAME@" /etc/nginx/nginx.conf && \
         sudo systemctl restart nginx

The command above use the ``auth file`` to verify you are the owner of the server.
Visit |all_orders| page to find your certificate, then press on its ``ID``.

.. |all_orders| raw:: html

   <a href="https://comodosslstore.com/client/orders.aspx" target="_blank">all orders</a>

.. image:: /img/user-guide/ca/comodo/all-orders.png
   :width: 100%
   :align: center
   :alt: All orders

You will be redirected to the certificate details page. Then download it with the ``DOWNLOAD CERTIFICATE`` button, if
the button is not presented, just wait - ``Comodo`` requires a time to authenticate your server.

.. image:: /img/user-guide/ca/comodo/download-cert.png
   :width: 100%
   :align: center
   :alt: Download certificate

And using brand new terminal window being on the local machine transfer the file to the server.

.. code-block:: console

    $ scp ~/Desktop/210854864.zip root@157.230.226.218:/

Then open a terminal window with the server and copy and paste the commands below.

.. code-block:: console

   $ export DOMAIN=the-coolest-masternode.xyz
   $ sudo apt-get install unzip -y && \
         cd / && COMODO_CERT=$(ls *.zip) && cd ~ && unzip /$COMODO_CERT && \
         cd "CER - CRT Files" && cat ${DOMAIN%.*}_${DOMAIN##*.}.crt My_CA_Bundle.ca-bundle > ssl-bundle.crt && \
         cd .. && mv CER\ -\ CRT\ Files/ssl-bundle.crt . && \
         mkdir /etc/comodo/ && mv server.key ssl-bundle.crt /etc/comodo/ && \
         curl https://gist.githubusercontent.com/dmytrostriletskyi/fce9d6cd9f4529989dbc600b8d2e907b/raw/29bff62d2e1d935805d186707870ff0700e3dc85/nginx.conf > /etc/nginx/nginx.conf && \
         sed -i "s@websitenamewithdomain@$DOMAIN@" /etc/nginx/nginx.conf && \
         sudo systemctl restart nginx

To check if your node has completed a correct ``SSL certificate``  setup, open a brand new terminal window and send a ``https``
request to get node configurations. Change value of ``NODE_IP_ADDRESS`` to your domain name with extension (i.e. ``the-coolest-masternode.xyz``).

.. code-block:: console

   $ export NODE_IP_ADDRESS=the-coolest-masternode.xyz
   $ curl -X POST https://$NODE_IP_ADDRESS -H 'Content-Type: application/json' -d \
         '{"jsonrpc":"2.0","id":"11","method":"get_node_config","params":{}}' | python -m json.tool

The flow is illustrated below.

.. image:: /img/user-guide/ca/comodo/proof-node-works-https.png
   :width: 100%
   :align: center
   :alt: Proof node works over HTTPS

.. |curl_tool| raw:: html

   <a href="https://curl.haxx.se/download.html" target="_blank">tool named curl </a>
