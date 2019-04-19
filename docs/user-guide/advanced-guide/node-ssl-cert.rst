SSL certificate for node
========================

**SSL Certificates** are small data files that digitally bind a cryptographic key to an organization's details.
When installed on a web server, it activates the padlock and the https protocol and allows secure connections from a
web server to a browser.

Let's Encrypt
-------------

**Let's Encrypt** is a non-profit certificate authority that provides ``X.509 certificates`` for ``Transport Layer Security``
(TLS) encryption at no charge.

First of all, login to the server as you previously did during installation of the node. Remember to change ``157.230.146.230``
to your server's ``IP address``:

.. code-block:: console

   $ ssh root@157.230.146.230

The flow is illustrated below.

.. image:: /img/user-guide/advanced-guide/ssh-login-to-the-server.png
   :width: 100%
   :align: center
   :alt: SSH login to the server

Then create a new environment variable as illustrated below. Change ``the-coolest-masternode.xyz``
with your ``domain name``.

.. code-block:: console

   $ export DOMAIN=the-coolest-masternode.xyz

Then create a new environment variable with your ``email`` to receive notifications from ``Let's Encrypt``:

.. code-block:: console

   $ export EMAIL=dmytro.striletskyi@gmail.com

Copy the command below and paste into the terminal which will create an ``SSL certificate`` and order the web-server to serve ``https`` connections.

.. code-block:: console

    $ echo "DOMAIN=$DOMAIN" >> ~/.bashrc && \
         sudo apt install software-properties-common -y && \
         sudo add-apt-repository ppa:certbot/certbot -y && \
         sudo apt update && sudo apt install certbot python-certbot-nginx -y && \
         sudo -i sed -i "s@websitenamewithdomain@$DOMAIN@" /etc/nginx/nginx.conf && \
         sudo certbot run --nginx -d $DOMAIN --non-interactive --agree-tos -m $EMAIL && \
         curl https://gist.githubusercontent.com/dmytrostriletskyi/24a8125e609bba7e8d8f9b3e54d634ff/raw/6e9fa256fe07c99d1e15bc652bd328cb3447b046/letsencrypt-nginx.conf | sudo tee /etc/nginx/nginx.conf > /dev/null && \
         sudo -i sed -i "s@websitenamewithdomain@$DOMAIN@" /etc/nginx/nginx.conf && \
         sudo systemctl restart nginx && \
         echo "1 5 * * * $USER /usr/bin/certbot renew" | sudo tee -a /etc/crontab > /dev/null && \
         echo "5 5 * * * /usr/bin/systemctl reload nginx" | sudo tee -a /etc/crontab > /dev/null

To check if your node has completed a correct ``SSL certificate`` setup, use the following commands, being logged in your server.

.. code-block:: console

   $ curl -X POST https://$DOMAIN/rpc/ -H 'Content-Type: application/json' -d \
         '{"jsonrpc":"2.0","id":"11","method":"get_node_config","params":{}}' | python3 -m json.tool

The flow is illustrated below.

.. image:: /img/user-guide/ca/comodo/proof-node-works-https.png
   :width: 100%
   :align: center
   :alt: Proof node works over HTTPS

For now, you can reach your monitoring page with the following address — ``https://the-coolest-masternode.xyz``,
changing ``the-coolest-masternode.xyz`` to your domain name and extension.

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

Verify you have bought the correct ``SSL certificate`` and press ``PLACE ORDER``.

.. image:: /img/user-guide/ca/comodo/card-information.png
   :width: 100%
   :align: center
   :alt: Card information

Then press ``COMPLETE ORDER``.

.. image:: /img/user-guide/ca/comodo/complete-order.png
   :width: 100%
   :align: center
   :alt: Complete order

When your purchase has been processed, you can generate a certificate by pressing the  ``GENERATE CERT NOW`` button.

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

Then switch to the terminal. Log in to the server as you previously did during installation of the node:

.. code-block:: console

   $ ssh root@95.179.156.74

The flow is illustrated below.

.. image:: /img/user-guide/advanced-guide/ssh-login-to-the-server.png
   :width: 100%
   :align: center
   :alt: SSH login to the server

Generate ``OpenSSL`` keys for your server with the following command:

.. code-block:: console

    $ cd ~ && sudo openssl req -new -newkey rsa:2048 -nodes -keyout server.key -out server.csr

The only one you are required to enter is a domain name with an extension (i.e. ``the-coolest-masternode.xyz``) to the
fields named ``Common Name``. The flow is illustrated below.

.. image:: /img/user-guide/ca/comodo/generate-openssl-keys.png
   :width: 100%
   :align: center
   :alt: Generate OpenSSL keys

Print ``certificate signing request`` with the following command that is required for ``Comodo``.

.. code-block:: console

    $ cat server.csr

The flow is illustrated below.

.. image:: /img/user-guide/ca/comodo/cat-csr.png
   :width: 100%
   :align: center
   :alt: Cat CSR

And input it into the corresponding form.

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

And using a brand new terminal window on the local machine transfer the authentication file to the server. If you
use ``Windows``, you may need a bit different kind of the ``scp`` command, check |scp_on_windows| out. Remember to
change ``459F5867C44CDB4551D93938E8116D3E`` with your file name.

.. |scp_on_windows| raw:: html

   <a href="https://success.tanaza.com/s/article/How-to-use-SCP-command-on-Windows" target="_blank">this guide</a>

.. code-block:: console

    $ scp ~/Desktop/459F5867C44CDB4551D93938E8116D3E.txt root@157.230.226.218:~

If you use the ``AWS``, your command should be similar to the following one. Remember to change ``MyPC.pem`` to your
private key file and ``ec2-18-216-76-35.us-east-2.compute.amazonaws.com`` to your ``Public DNS``.

.. code-block:: console

   $ scp -i "MyPC.pem" ~/Desktop/FAA68D73B6534772BDAAADD9B7EFB596.txt ubuntu@ec2-18-216-76-35.us-east-2.compute.amazonaws.com:~

Then open a terminal window with the server and copy and paste the command below.

.. code-block:: console

   $ cd ~ && COMODO_AUTH_FILE=$(ls *.txt) && COMODO_AUTH_FILE_NAME=${COMODO_AUTH_FILE%.*} && \
         sudo mkdir /var/www/comodo/ && sudo mv ~/$COMODO_AUTH_FILE_NAME.txt /var/www/comodo/ && \
         curl https://raw.githubusercontent.com/Remmeauth/remme-core/dev/docs/user-guide/templates/comodo-auth-file-nginx.conf | sudo tee /etc/nginx/nginx.conf > /dev/null && \
         sudo -i sed -i "s@comodohashfile@$COMODO_AUTH_FILE_NAME@" /etc/nginx/nginx.conf && \
         sudo systemctl restart nginx

The command above uses the ``auth file`` to verify you are the owner of the server.
Visit |all_orders| page to find your certificate, then press on its ``ID``.

.. |all_orders| raw:: html

   <a href="https://comodosslstore.com/client/orders.aspx" target="_blank">all orders</a>

.. image:: /img/user-guide/ca/comodo/all-orders.png
   :width: 100%
   :align: center
   :alt: All orders

You will be redirected to the certificate details page. Then download it with the ``DOWNLOAD CERTIFICATE`` button. If
the button is not displayed, just wait - ``Comodo`` requires time to authenticate your server.

.. image:: /img/user-guide/ca/comodo/download-cert.png
   :width: 100%
   :align: center
   :alt: Download certificate

Using a brand new terminal window on the local machine transfer the file to the server.

.. code-block:: console

    $ scp ~/Desktop/210854864.zip root@157.230.226.218:~

Then open a terminal window with the server. Then create a new environment variable with your domain name as illustrated below.
Remember to change ``the-coolest-masternode.xyz`` with your ``domain name``.

.. code-block:: console

   $ export DOMAIN=the-coolest-masternode.xyz

Copy the command below and paste into the terminal which will create an ``SSL certificate`` and order the web-server to
serve ``https`` connections.

.. code-block:: console

   $ cd ~ && sudo apt-get install unzip -y && \
         COMODO_CERT=$(ls *.zip) && unzip $COMODO_CERT && \
         cd "CER - CRT Files" && cat ${DOMAIN%.*}_${DOMAIN##*.}.crt My_CA_Bundle.ca-bundle > ssl-bundle.crt && \
         cd .. && mv CER\ -\ CRT\ Files/ssl-bundle.crt . && \
         sudo mkdir /etc/comodo/ && sudo mv server.key ssl-bundle.crt /etc/comodo/ && \
         curl https://gist.githubusercontent.com/dmytrostriletskyi/a0b4c24e0b34788596ed3f6264282694/raw/35be13584c781037c775f2f082387515ad069815/comodo-nginx.conf | sudo tee /etc/nginx/nginx.conf > /dev/null && \
         sudo -i sed -i "s@websitenamewithdomain@$DOMAIN@" /etc/nginx/nginx.conf && \
         sudo systemctl restart nginx

To check if your node has completed a correct ``SSL certificate`` setup, use the following commands, being logged in your server.

.. code-block:: console

   $ curl -X POST https://$DOMAIN/rpc/ -H 'Content-Type: application/json' -d \
         '{"jsonrpc":"2.0","id":"11","method":"get_node_config","params":{}}' | python3 -m json.tool

The flow is illustrated below.

.. image:: /img/user-guide/ca/comodo/proof-node-works-https.png
   :width: 100%
   :align: center
   :alt: Proof node works over HTTPS

.. |curl_tool| raw:: html

   <a href="https://curl.haxx.se/download.html" target="_blank">tool named curl </a>

For now, you can reach your admin panel with the following address — ``https://the-coolest-masternode.xyz``,
changing ``the-coolest-masternode.xyz`` to your domain name and extension.
