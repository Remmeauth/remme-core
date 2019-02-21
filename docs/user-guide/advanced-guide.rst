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

Click on |your_godaddy_products| that will open your ``GoDaddy`` products, where you can start buying domain for the node.
Enter preferred domain name (i.e. ``the-coolest-masternode``) and click on search icon.

.. image:: /img/user-guide/dns/godaddy/enter-domain-name.png
   :width: 100%
   :align: center
   :alt: Enter preferred domain name

After entering the domain name you will be redirected to the page that show if your preferred domain name is free.
If domain name isn't free, choose the similar one which ``GoDaddy`` will suggest for you. When you finish choosing right
domain name, press ``Add to Cart``.

.. image:: /img/user-guide/dns/godaddy/add-domain-to-cart.png
   :width: 100%
   :align: center
   :alt: Add domain to cart

Then leave the checkbox ``Start your website FREE`` empty. You also could create e-mail address that match your domain, but it will
charge additional cost. E-mail address isn't required for setup the node.

.. image:: /img/user-guide/dns/godaddy/no-default-start-website.png
   :width: 100%
   :align: center
   :alt: Enter default website starting

You may want to hide information about you with the following feature. Please, visit |full_domain_privacy_and_protection| before make the decision.

.. |full_domain_privacy_and_protection| raw:: html

   <a href="https://www.godaddy.com/domains/full-domain-privacy-and-protection#privacy" target="_blank">according documentation</a>

.. image:: /img/user-guide/dns/godaddy/no-privacy-feature.png
   :width: 100%
   :align: center
   :alt: No privacy feature

Enter your billing details into the form to pay for the domain.

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

Click on the ``pencil`` right away of the row when type is ``A``, so the first row.

.. image:: /img/user-guide/dns/godaddy/edit-a-type.png
   :width: 100%
   :align: center
   :alt: Edit A type

Change ``Points to`` to the your server/instance/droplet ``IP address`` and click ``Save``.

.. image:: /img/user-guide/dns/godaddy/point-a-type-to-ip-address.png
   :width: 100%
   :align: center
   :alt: Point A type to the IP address

Wait a few minutes, this operation take a time. Then you can ensure your domain name is linked to the server.
First of all, send to request to the server by its ``IP-address``. Remember to change ``95.179.156.74`` to your server ``IP address``.

.. code-block:: console

   $ export NODE_IP_ADDRESS=95.179.156.74
   $ curl -X POST http://$NODE_IP_ADDRESS:8080 -H 'Content-Type: application/json' -d \
         '{"jsonrpc":"2.0","id":"11","method":"get_node_config","params":{}}' | python -m json.tool


Change value of ``NODE_IP_ADDRESS`` to your domain name with extention (i.e. ``the-coolest-masternode.xyz``) and send the
same request which should response similar to the previous one:

.. code-block:: console

   $ export NODE_IP_ADDRESS=the-coolest-masternode.xyz
   $ curl -X POST http://$NODE_IP_ADDRESS:8080 -H 'Content-Type: application/json' -d \
         '{"jsonrpc":"2.0","id":"11

The flow is illustrated below.

.. image:: /img/user-guide/dns/godaddy/proof-domain-name-works.png
   :width: 100%
   :align: center
   :alt: Proof domain name works
