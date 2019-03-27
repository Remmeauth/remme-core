Server snapshots
================

Snapshots are an effective way to make a complete **backup** of your server. You won't be able to restore individual files,
but rather the whole server. This section provides information on how to use the snapshot features on the supported cloud
providers (:doc:`/user-guide/cloud`).

Amazon Web Services
-------------------

.. _CreateAWSSnapshot:

Create a snapshot
~~~~~~~~~~~~~~~~~

Open an instances page and find out your instance that runs the node. Take out ``instance id`` and ``availability zone``
for further usage.

.. image:: /img/user-guide/advanced-guide/snapshots/aws/instances-page.png
   :width: 100%
   :align: center
   :alt:

Open a volumes page and find out your volume that is attached to the instance that runs the node.

.. image:: /img/user-guide/advanced-guide/snapshots/aws/volumes-page.png
   :width: 100%
   :align: center
   :alt:

Click on the right mouse button and choose the ``Create Snapshot`` option.

.. image:: /img/user-guide/advanced-guide/snapshots/aws/create-snapshot.png
   :width: 100%
   :align: center
   :alt:

After, you will see a pop-up to enter the snapshot details. Enter ``Stable working Remme core testnet node`` into the
description field. Create a tag called ``Name`` with value ``stable-working-remme-core-testnet-node`` (actually,
you can use any convenient names). Then press the ``Create Snapshot`` button.

.. image:: /img/user-guide/advanced-guide/snapshots/aws/snapshot-details.png
   :width: 100%
   :align: center
   :alt:

Open the snapshots page, find out the newly created snapshot and wait until it is completed. Take out the ``snapshot id``
for further usage.

.. image:: /img/user-guide/advanced-guide/snapshots/aws/snapshots-page.png
   :width: 100%
   :align: center
   :alt:

Then go back to the volumes page and press ``Create Volume``.

.. image:: /img/user-guide/advanced-guide/snapshots/aws/create-new-volume.png
   :width: 100%
   :align: center
   :alt:

After, you will get a pop-up to enter the volume details. Leave volume type as ``General Purpose SSD (gp2)``,
enter ``100`` to the ``Size`` field, enter ``availability zone`` of the instance to the corresponding field,
enter ``snapshot id`` to the corresponding field. Create a tag called ``Name`` with value ``Stable working Remme core testnet node``.

.. image:: /img/user-guide/advanced-guide/snapshots/aws/volume-details.png
   :width: 100%
   :align: center
   :alt:

.. _ApplyAWSSnapshot:

Apply a snapshot
~~~~~~~~~~~~~~~~

Open the instances page and stop the instance that runs the node.

.. image:: /img/user-guide/advanced-guide/snapshots/aws/stop-instance.png
   :width: 100%
   :align: center
   :alt:

Go to the volumes page and detach the volume that's currently attached to the instance that runs the node.

.. image:: /img/user-guide/advanced-guide/snapshots/aws/detach-old-volume.png
   :width: 100%
   :align: center
   :alt:

Now attach the volume that you have created from the snapshot in the previous step that describes how to
create a snapshot.

.. image:: /img/user-guide/advanced-guide/snapshots/aws/attach-new-volume.png
   :width: 100%
   :align: center
   :alt:

After, you will get a pop-up to enter the details for attaching volume. Enter the ``instance id`` from the instance that
runs the node to the corresponding field and enter ``/dev/sda1`` to the ``device`` field. Then press ``Attach`` button.

.. image:: /img/user-guide/advanced-guide/snapshots/aws/attach-new-volume-details.png
   :width: 100%
   :align: center
   :alt:

Go back to the instance page and run the stopped instance. Now you can connect to the instance and ensure it has the data
you have backed up using a snapshot.

.. image:: /img/user-guide/advanced-guide/snapshots/aws/start-instance.png
   :width: 100%
   :align: center
   :alt:

Digital Ocean
-------------

Visit an official |do_snapshot_documentation| that explains how to use the snapshot feature.

.. |do_snapshot_documentation| raw:: html

   <a href="https://www.digitalocean.com/docs/images/snapshots/how-to/snapshot-droplets/" target="_blank">Digital Ocean documentation section</a>

Vultr
-----

Visit an official |vultr_snapshot_documentation| that explains how to use the snapshot feature.

.. |vultr_snapshot_documentation| raw:: html

   <a href="https://www.vultr.com/docs/how-to-restore-a-snapshot" target="_blank">Vultr documentation section</a>
