********
Web Auth
********

Overview
========

One of the most prominent needs of any organisation and platform is to authenticate and authorize its members.

In order to help with affairs, REMME has built web auth demo of how a secure login systems works and how to implement it.

We've build a login mechanism with REMchain storage in mind to check against user certificate's hash and its validity.

We also added a 2nd factor option such as Google Authenticator in case of a certificate being stolen by the third party.

You may check out the live version at  `Web Auth Demo <https://webauth-testnet.remme.io/register>`_

How to use DEMO
===============

Before proceeding `Web Auth Demo <https://webauth-testnet.remme.io/register>`_ one needs to generate keystore file.
It can be done at `FAQ page <http://remchain.webflow.io/faq>`_

How to run Production version
=============================

1. Download the latest release from Releases section (<version_number>-release.zip). Unpack it.

2. Start node: Open a terminal inside the unpacked folder and run ./run.sh.

3. You can now use our REST API. By default, it is started on http://localhost:8080. Fancy Swagger UI with documentation is available on http://localhost:8080/api/v1/ui. The API port can be changed in config/network-config.env file.

How to run Development version
==============================

1. Clone this repository to your machine: git clone https://github.com/Remmeauth/remme-core.git

2. This project uses git submodules. To initialize them run `git submodule init` and then `git submodule update --init`. Also, git submodule update is required after every pull from the repository.

3. Run `make run_dev`.

Technical Requirement
=====================

* Docker (>= 18.0.0)

* Unix system (MacOS, Linux etc.)

* At least 2GB hard drive storage available

* At least 1GB RAM

* Machine's time settings are up to date