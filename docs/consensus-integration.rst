*****************************
Consensus integration testing
*****************************

Prerequiresites
===============

* Docker
* Docker Compose
* `kubectl`

DIND Kubeadm
============

Launching
---------

Launch this software to spin up a local Kubernetes cluster of multiple nodes
(Minikube supports only one node).

https://github.com/kubernetes-sigs/kubeadm-dind-cluster

You can set the number of nodes like that:
`NUM_NODES=3 ./dind-cluster-v1.13.sh up`

Uploading images
----------------

* `./dind-cluster-v1.13.sh copy-image remme/sawtooth:latest`
* `./dind-cluster-v1.13.sh copy-image remme/remme-core:latest`
* `./dind-cluster-v1.13.sh copy-image remme/remme-consensus:latest`

This may take some time. **Use only production builds** (`make build`).

Running the cluster
===================

Configuration
-------------

Run `kubectl get nodes`. Enter one of the nodes into the file
`docker/kubernetes/consensus-testing-config.yml` as the `GENESIS_HOST`. This
node will create the genesis block.

Change the number of replicas in `docker/kubernetes/consensus-testing-local.yml`
according to your needs.

Running the network
-------------------

* Set permissions for in-container kubectl:
  `kubectl -f docker/kubernetes/authorization.yml apply`
* Import the configuration
  `kubectl -f docker/kubernetes/consensus-testing-config.yml apply`.
* Spin up the cluster
  `kubectl -f docker/kubernetes/consensus-testing-local.yml apply`.

The node as `GENESIS_HOST` on the previous step will generate the genesis block.
All nodes will automatically discover each other.

Checking logs
-------------

* Checkout the list of pods: `kubectl get pods`.
* Get logs from a specific pod for a specific container:
  `kubectl logs <pod_name> -c <container_name>`.

Turn off the cluster
--------------------

`kubectl delete deployment remme`
