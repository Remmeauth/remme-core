# REMME Core 0.1.0-alpha

**This is alpha version! It is not suitable for any use in production and is intended to demonstrate capabilities of Hyperledger Sawtooth in the scope of REMME.**

## How to run

You will need Docker and Docker Compose installed on your machine.

When you have this repository cloned run the following commands:

* `make build_docker`
* `make run`

After all the package are started up run `docker exec -it $(docker-compose ps -q shell) bash` to enter the console.

You can try `rem-token` and `rem-crt` commands to run operations related to token and certificates respectively.

## To be done in the next releases

* Automated testing (needed to initialize MockValidator with the genesis batch). It is possible, that MockValidator will be replaced with real validator until genesis batches are implemented in MockValidator.
* Massive refactoring related to payments for the process of registration of new certificates.
* First deploy of test network based on PoET consensus.
* Research on implementation of a custom consensus in Sawtooth.
* Architecture of the process of token migration between REMME (test network) and Ethereum networks (Kovan testnet).
