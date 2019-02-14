# Consensus integration testing

## Testing flow

```
+---------------------------------------------------------------+
|    nodes deployment                                           |
|                                                               |
|    +---------------------------------+    +--------------+    |
|    |  node pod                       +----+  node pod 2  |    |
|    |                                 |    +------+-------+    |
|    |  +--------+   +--------------+  |           |            |
|    |  |  init  +-->+  remme node  |  |           |            |
|    |  +--+-----+   +--------------+  |    +------+-------+    |
|    |     |                           +----+  node pod n  |    |
|    +---------------------------------+    +--------------+    |
|          |                                                    |
|          |                                                    |
+-----------------------------------------------+---------------+
           |                                    ^
           | request keys                       |
           | and network config                 |
           v                                    |
        +--+----------------------+             | scale deployment
        |  config dealer service  |             | send transactions
        +--+----------------------+             | track blocks and txns
           |                                    |
           v                                    |
        +--+----------------------+             |
        |  config dealer          |             |
        +-------------------------+             |
                                             +--+----------+
                                             |  tests job  |
                                             +-------------+
```

* **configuration dealer** &mdash; generates public/private key pairs and
  configurations for new nodes;
* **tests job** &mdash; changes the configuration of the network (for example,
  starts and stops nodes), sends transactions and watches node statuses;
* **nodes deployment** &mdash; the actual network.

## Running tests

* Build the core and the consensus;
* Build the tests: `docker-compose -f docker-compose-build.yml build`
* Prefix your image tags with your registry name:
  `docker tag remme/<image_tag> <your_registry_name>/remme/<image_tag>`;
* Push images to your registry;
* Prefix image tags in `integration-testing.yml` with your registry name;
* Run the tests: `kubectl -f integration-testing.yml apply`;
* Get the list of pods: `kubectl --namespace=remme-tests get pods`
* Check the output of tests:
  `kubectl --namespace=remme-tests logs tests-xxxx`;
* Delete what remains in the cluster (check the outputs of
  `kubectl --namespace=remme-tests get deployments` and
  `kubectl --namespace=remme-tests get jobs`).

## Running on Azure

**This is only to demonstrate the overall flow. Refer to Azure manuals for the
details.**

* Authenticate to your Azure account: `az login`;
* Create a resource group: `az group create -l westeurope -n kubetest`;
* Create a Docker registry: `az acr create -n kubetest -g kubetest`;
* Login to registry: `az acr login --name kubetest`
* Create Kubernetes service:
  `az aks create -n kubetest -g kubetest --node-count 3`;
* Login to Kubernetes service: `az aks get-credentials -g kubetest -n kubetest`
* Setup Kubernetes to access the cluster:
  ```bash
    ACR_ID=$(az acr show -g kubetest -n kubetest --query "id" --output tsv)
    AKS_ID=$(az aks show -gkubetest -n kubetest --query "servicePrincipalProfile.clientId" --output tsv)
    az role assignment create --assignee $AKS_ID --role acrpull --scope $ACR_ID
  ```
* Push your images
* Run your tests
