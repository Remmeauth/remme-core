********
Web Auth
********

Overview
========

One of the most prominent needs of any organisation and platform is to authenticate and authorize its members.

In order to help with affairs, REMME has built web auth demo of how a secure login systems works and how to implement it.

We've built a login mechanism with REMchain storage in mind to check against user certificate's hash and its validity.

We also added a 2nd factor option such as Google Authenticator in case of a certificate being stolen by the third party.

You may check out the live version at  `Web Auth Demo <https://webauth-testnet.remme.io/register>`_

************************
How to use Web Auth Demo
************************

Generate keystore file
======================

1. Before proceeding to demo, one needs to generate a keystore file, which has the following form:

.. code-block:: json

 {
  "publicKey":"0205af8af2b75bbab7197bee761329ea9294c65e2d127c66344d5c629b3f8aa72a",
  "privateKey":"67cc68c0eb28224def574bb646a621cb1fdc0665260ecc63c3d5090a425a3a97"
 }

It can be generated at `FAQ page <http://remchain.webflow.io/faq>`_ by clicking "Get Tokens" button and then going through "generate" link. A `keystore.txt` file will be generated for you and may be further used within web-auth demo.

2. Afterwards, in order to create a certificate, one has to get some tokens on their balance. Thus by providing an email address in the very same form and pressing "Submit", the public key provided will receive tokens to its address.

.. note::
 You may check if tokens refill is done by monitoring `Block Explorer <https://explorer-testnet.remme.io/>`_ for your transaction.

Generate and register certificate
=================================

1. Go to `Web Auth Register Page <https://webauth-testnet.remme.io/register>`_ where you will be asked to provide a REMchain keystore file you have just received.

2. Provide certificate details. Some general information about the owner as well as certificate password for local keychain for MacOS storage is required, where for other OS's it is optional. Then press "Create User" and the transaction on the blockchain will be sent for you.

3. You may see the transaction appeared on the blockchain. At this point you will be asked weather you would like to add additional measure of security such as a second factor authentication. You may skip this step as well.

4. Now the certificate is generated for you and you may save it within your local machine's key storage for further use. In case of a MacOS, the keychain will prompt you to enter the password you mentioned in "details" step right away, as you try to open the downloaded file. Later on, chrome allows to extract the certificate from the keychain directly.

In case of other browsers such as Firefox, one needs to import the certificate manually:
`Preferences > Advanced > "Certificates" tab > View Certificates > "You certificates" tab > Import`

Login using certificate
=======================

1. Once a certificate is generated and stored on a user's local storage, one may log into the system by visiting `Login Page <https://webauth-testnet.remme.io/login/>`_
2. By clicking on a "login" button, a user will be prompted to choose a certificate for authentication purposes.
3. The next step will prompt to perform the 2nd factor, if one has check-marked during the registration step. Press "Login" to skip the step.
4. Success. You are now logged in using your certificate! You will be directed to a classified resource.

Revoke certificate
==================

At the upper right corner, by clicking a dropdown arrow, one will find a "Revoke" button, which allows to revoke current certificate one has logged in with.

***********************
How to run DEMO locally
***********************
For installation instructions of the demo, please visit `Web Auth Demo on Github <https://github.com/Remmeauth/remme-webauth-testnet/>`_.
