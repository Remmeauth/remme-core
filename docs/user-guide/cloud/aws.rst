*************************
Amazon Web Services (AWS)
*************************

**Amazon Web Services (AWS)** is a subsidiary of ``Amazon`` that provides on-demand cloud computing platforms to individuals,
companies and governments on a paid subscription basis. The technology allows subscribers to have at their disposal a
virtual cluster of computers, available all the time, through the internet.

Step 1: sign up
===============

Visit the |registration_link| to create your own account on ``AWS``.

.. |registration_link| raw:: html

   <a href="https://portal.aws.amazon.com/billing/signup?nc2=h_ct&src=header_signup&redirect_url=https%3A%2F%2Faws.amazon.com%2Fregistration-confirmation" target="_blank">registration link</a>

.. image:: /img/user-guide/cloud/aws/sign-up-form.png
   :width: 100%
   :align: center
   :alt: Sign up form

Enter your contact information along with credit/debit card details into the form  to pay for cloud services.

.. image:: /img/user-guide/cloud/aws/sign-up-contact-info.png
   :width: 100%
   :align: center
   :alt: Sign up contact information

After entering initial credentials you will see the following screen for verifying the account.

.. image:: /img/user-guide/cloud/aws/sign-up-confirmation.png
   :width: 100%
   :align: center
   :alt: Sign up confirmation

Choose a support plan. Read more about this in the |aws_support_plans|.

.. |aws_support_plans| raw:: html

   <a href="https://aws.amazon.com/premiumsupport/plans/" target="_blank">reference</a>

.. image:: /img/user-guide/cloud/aws/choose-account-plan.png
   :width: 100%
   :align: center
   :alt: Choose account plan

You will then be redirected to ``AWS management console``. Press ``Launch a virtual machine`` to create your first server called ``EC2``.

.. image:: /img/user-guide/cloud/aws/aws-management-console.png
   :width: 100%
   :align: center
   :alt: Choose account plan

Step 2: launch instance
=======================

``Amazon EC2`` provides a wide selection of instance types optimized to fit different use cases. Instances are virtual
servers that can run applications. They have varying combinations of CPU, memory, storage, and networking capacity,
and give you the flexibility to choose the appropriate mix of resources for your applications. Learn more about instance
types and how they can meet your computing needs.

Type ``Ubuntu 16.04 LTS`` into the search bar, choose ``AWS Marketplace`` and select image ``Ubuntu 16.04 LTS - Xenial (HVM)``,
which should be regarded as an operating system, then in the window that appears click ``Continue``.

.. image:: /img/user-guide/cloud/aws/choose-instance-image.png
   :width: 100%
   :align: center
   :alt: Choose instance image

Choose the ``t2.medium`` type of the instance that fits all technical requirements for the node then press ``Next: Configure Instance Details``.

.. image:: /img/user-guide/cloud/aws/choose-instance-type.png
   :width: 100%
   :align: center
   :alt: Choose instance type

Leave the default instance details, then press ``Next: Add Storage``.

.. image:: /img/user-guide/cloud/aws/configure-instance.png
   :width: 100%
   :align: center
   :alt: Configure instance

Change ``8`` GiB size to ``60``, then press ``Next: Add tags``.

.. image:: /img/user-guide/cloud/aws/add-storage.png
   :width: 100%
   :align: center
   :alt: Add instance's storage

Set tag named ``Name`` with value ``remme-core-testnet-node``, then press ``Next: Configure Security Group``.

.. image:: /img/user-guide/cloud/aws/set-name-tag.png
   :width: 100%
   :align: center
   :alt: Set name tag


Add the next rule and specify ``Custom TCP`` for type, ``8080`` for port range ``0.0.0.0/0`` for source and ``Open node RPC API port`` for description.
Add the next rule and specify ``Custom TCP`` for type, ``8800`` for port range ``0.0.0.0/0`` for source and ``Nodes synchronisation`` for description.
Then press ``Review and Launch``.

.. image:: /img/user-guide/cloud/aws/instance-firewall.png
   :width: 100%
   :align: center
   :alt: Open RPC API port for requests

Then review your instance configurations to make sure you're following the guide, then press ``Launch``.

.. image:: /img/user-guide/cloud/aws/review-instance-launch.png
   :width: 100%
   :align: center
   :alt: Review instance launch

Choose ``Create a new keypair`` and leave the any name you want (``MyPrivateKeyForConnectionToInstance`` on the screen), then press ``Launch instance``.

.. image:: /img/user-guide/cloud/aws/private-key-for-connection-to-instance.png
   :width: 100%
   :align: center
   :alt: Download private key for connection to instance

Then you will be redirected to the launch status page. Click on the instance identifier right away from ``The following instance launches have been initiated`` phrase.

.. image:: /img/user-guide/cloud/aws/instance-is-launching.png
   :width: 100%
   :align: center
   :alt: Instance is launching

The instances dashboard should be opened. Take a look at your instance, its status (should be running). Find ``public DNS``
and ``IPv4 Public IP``, which you will need for subsequent steps.

.. image:: /img/user-guide/cloud/aws/instances-dashboard.png
   :width: 100%
   :align: center
   :alt: Instances dashboard

Step 4: login to instance
=========================

If you click on the ``Connect`` button, you will get the instructions (terminal commands) on how to connect to the instance.
If you use ``Windows``, please follow |windows_putty_aws_guide| from ``AWS``.

.. |windows_putty_aws_guide| raw:: html

   <a href="https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/putty.html?icmpid=docs_ec2_console" target="_blank">connecting to your Linux instance from Windows Using PuTTY</a>

.. image:: /img/user-guide/cloud/aws/how-to-connect-to-instance.png
   :width: 100%
   :align: center
   :alt: How to connect to instance instructions

The flow is illustrated below.

.. image:: /img/user-guide/cloud/aws/connect-to-instance-commands.png
   :width: 100%
   :align: center
   :alt: Connect to the instance terminal commands

.. image:: /img/user-guide/cloud/aws/connection-has-been-done.png
   :width: 100%
   :align: center
   :alt: Terminal output that says connection has been done successfully

If you need any assistance connecting to your instance, please see |connection_to_instance_docs|.

.. |connection_to_instance_docs| raw:: html

   <a href="https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstances.html?icmpid=docs_ec2_console" target="_blank">AWS connection documentation</a>

Step 5: start the project
=========================

Copy commands below and paste it into the terminal. You can change the value of ``REMME_CORE_RELEASE`` below, just take
a look at our `release list <https://github.com/Remmeauth/remme-core/releases>`_. We would recommend the latest version of
the project that already specified in the command below.

.. code-block:: console

   $ export REMME_CORE_RELEASE=0.7.0-alpha
   $ sudo apt-get install apt-transport-https ca-certificates curl software-properties-common make -y && \
         echo "REMME_CORE_RELEASE=$REMME_CORE_RELEASE" >> ~/.bashrc && \
         cd /home/ && curl -L https://github.com/Remmeauth/remme-core/archive/v$REMME_CORE_RELEASE.tar.gz | sudo tar zx && \
         cd remme-core-$REMME_CORE_RELEASE && \
         sudo apt update && sudo apt upgrade -y && \
         curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - && \
         sudo apt update && \
         sudo apt install docker.io -y && \
         sudo curl -o /usr/local/bin/docker-compose -L "https://github.com/docker/compose/releases/download/1.23.2/docker-compose-$(uname -s)-$(uname -m)" && \
         sudo chmod +x /usr/local/bin/docker-compose && \
         sudo make run_genesis_bg

.. image:: /img/user-guide/cloud/aws/installation-command.png
   :width: 100%
   :align: center
   :alt: Terminal installation command example

The expected result of this command is illustrated below.

.. image:: /img/user-guide/cloud/digital-ocean/installation-output.png
   :width: 100%
   :align: center
   :alt: Installation output

If during installation the same window as illustrated below appears, just press ``Enter``.

.. image:: /img/user-guide/cloud/digital-ocean/installation-possible-window.png
   :width: 100%
   :align: center
   :alt: Installation possible window

When you see the same output as illustrated below, it means the node is ready to accept requests.

.. image:: /img/user-guide/cloud/digital-ocean/proof-core-is-up.png
   :width: 100%
   :align: center
   :alt: Proof core is up

To check if your node has completed a correct setup, use the following commands, being logged in your instance. Remember to
change ``157.230.146.230`` to your server's ``IP address``.

.. code-block:: console

   $ export NODE_IP_ADDRESS=157.230.146.230
   $ curl -X POST http://$NODE_IP_ADDRESS:8080 -H 'Content-Type: application/json' -d \
         '{"jsonrpc":"2.0","id":"11","method":"get_node_config","params":{}}' | python3 -m json.tool

The response should look similar to this:

.. code-block:: console

   {
       "id": "11",
       "jsonrpc": "2.0",
       "result": {
           "node_public_key": "028e7e9b060d7c407e428676299ced9afef4ce782995294d8ea01fd0f08cec9765"
       }
   }

The flow is illustrated below.

.. image:: /img/user-guide/cloud/digital-ocean/proof-core-is-working.png
   :width: 100%
   :align: center
   :alt: Proof core is working

What's next?
============

1. Visit our :doc:`/user-guide/advanced-guide` for more details on user experience.
2. Communication with the node is available through :doc:`/apis/rpc` API, so check it out.
