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

Open your inbox, select the confirmation email from ``GoDaddy`` and click on the button ``Verify Email Now``.

.. image:: /img/user-guide/dns/godaddy/verify-account-via-inbox.png
   :width: 100%
   :align: center
   :alt: Create GoDaddy account

Click on |your_godaddy_products| that will open your ``GoDaddy`` products, where you can buy a domain for the node.
Enter the preferred domain name (i.e. ``the-coolest-masternode``) and click on the search icon.

.. image:: /img/user-guide/dns/godaddy/enter-domain-name.png
   :width: 100%
   :align: center
   :alt: Enter preferred domain name

After entering the domain name, you will be redirected to the page that shows if your preferred domain name is free.
If the domain name isn't free, choose a similar one which ``GoDaddy`` will suggest for you. When you have finish
choosing the right domain name, press ``Add to Cart`` and ``Continue to Cart``.

.. image:: /img/user-guide/dns/godaddy/add-domain-to-cart.png
   :width: 100%
   :align: center
   :alt: Add domain to cart

You may want to hide your personal information with the following feature. Please visit the |full_domain_privacy_and_protection|
before making a decision. Otherwise, check the ``No Thanks`` checkbox.

.. |full_domain_privacy_and_protection| raw:: html

   <a href="https://www.godaddy.com/domains/full-domain-privacy-and-protection#privacy" target="_blank">according documentation</a>

.. image:: /img/user-guide/dns/godaddy/no-privacy-feature.png
   :width: 100%
   :align: center
   :alt: No privacy feature

Then leave the checkbox ``Start your website FREE`` empty. You could also create an email address that matches your domain,
but will be charged extra. An email address isn’t required to set up the node.

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

Complete the purchase with the big green button ``Complete Purchase``.

.. image:: /img/user-guide/dns/godaddy/complete-purchase.png
   :width: 100%
   :align: center
   :alt: Complete purchase

Click on |your_godaddy_products| that will open your ``GoDaddy`` products, where you can start linking your domain name to the server.
Then click on the button ``DNS``.

.. |your_godaddy_products| raw:: html

   <a href="https://account.godaddy.com/products/" target="_blank">this link</a>

.. image:: /img/user-guide/dns/godaddy/domain-dns-settings.png
   :width: 100%
   :align: center
   :alt: Domain DNS settings

Click on the ``pencil`` right away in the row where there is an ``A``, so in the first row.

.. image:: /img/user-guide/dns/godaddy/edit-a-type.png
   :width: 100%
   :align: center
   :alt: Edit A type

Change ``Points to`` to the your server/instance/droplet ``IP address`` and click ``Save``.

.. image:: /img/user-guide/dns/godaddy/point-a-type-to-ip-address.png
   :width: 100%
   :align: center
   :alt: Point A type to the IP address

Wait a few minutes, as this operation takes time. Then you can ensure your domain name is linked to the server.
First of all, check if your node still works, using the following commands. Remember to
change ``157.230.146.230`` to your server's ``IP address``.

.. code-block:: console

   $ export NODE_IP_ADDRESS=157.230.146.230
   $ curl -X POST http://$NODE_IP_ADDRESS:8080 -H 'Content-Type: application/json' -d \
         '{"jsonrpc":"2.0","id":"11","method":"get_node_config","params":{}}' | python3 -m json.tool

Then change the value of ``NODE_IP_ADDRESS`` to your domain name with an extension (i.e. ``the-coolest-masternode.xyz``)
and send execute the previous command again. A response should be similar to the previous one:

.. code-block:: console

   $ export NODE_IP_ADDRESS=the-coolest-masternode.xyz
   $ curl -X POST http://$NODE_IP_ADDRESS:8080 -H 'Content-Type: application/json' -d \
         '{"jsonrpc":"2.0","id":"11","method":"get_node_config","params":{}}' | python3 -m json.tool

The flow is illustrated below.

.. image:: /img/user-guide/dns/godaddy/proof-domain-name-works.png
   :width: 100%
   :align: center
   :alt: Proof domain name works

For now, you can reach your monitoring page with the following address — ``http://the-coolest-masternode.xyz/grafana/``,
changing ``the-coolest-masternode.xyz`` to your domain name and extension.
