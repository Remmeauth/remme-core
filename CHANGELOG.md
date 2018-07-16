# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).


## [0.4.0-alpha] - 2018-07-16
### Added
- REST API:
  - The endpoint for sending raw transactions. Now it is possible to build and sign a transaction and then submit it to
  a validator with the REST API without running a node while keeping your private keys secure.
  - CORS support for REST API.
- WebSockets for real-time tracking changes on transactions statutes. Other features are on the way.
- Arrays of public keys in Account objects were introduced to easily track all of the certificates issued by a
particular user. The list of certificates is accessible with the REST API endpoint. Please note, that those
changes are subject for future performance optimizations. Those change would not affect the REST API interface, but the
internals is subject to change.
- Possibility to disable economy in private networks. Many of those who want to launch their private networks do not
need economy features so now there is a way to disable them.
- Specifications for transaction families are now publicly available in the repository.
- More configuration options for nodes (see `.env` to see a full list of them).
### Changed
- `token` transaction family was renamed to `account`.
- Moved from storing certificates to storing and managing public keys. This leads to several important consequences:
  - GDPR compliance as no personal data accessible in a certificate is stored on the blockchain.
  - A wide range of supported containers for public keys.
- No dependency on Sawtooth API within REMME REST API. Previously the project used Sawtooth REST API to communicate with
the core. Now it communicates with the core directly via ZMQ sockets.
- Migrate to Python 3.6
- Internal refactoring has been done for cleaner project structure.
  - The transaction processor is now called as `remme.tp` instead of `remme`.
- Swagger UI was updated to a newer version.

## [0.3.1-alpha] - 2018-04-27
### Added
- REST API:
  - Support for certificate signing requests. Now key pairs for certificates can be generated on the client side.
  - Support for enabling and disabling methods and endpoints on API server start up.
  - Local p12 file generation (to generate certificates on the same machine a node is running on).
- Network:
  - Consensus can now be switched to PoET with validator enclave.
### Changed
- Better error messages and statuses in REST API.

## [0.3.0-alpha] - 2018-04-16
### Added
- REST API implementation based on OpenAPI specification and [Connexion](https://github.com/zalando/connexion).
**NOTE**: this API is not suitable for public usage (use it only for clients on a local machine) for now and is a demo
version. New version of API suitable for public use will be rolled out in the next release.
  - Certificate handling: registration, revocation and status checks.
  - Token handling: transfers and balance view.
  - Key pairs management.
- Sphinx-based documentation for source code and overall architecture.
- Capable of running a network of masternodes with DevMode consensus. The next release will contain setup for running it
 with [PoET (Proof of elapsed time)](https://sawtooth.hyperledger.org/docs/core/releases/1.0.1/architecture/poet.html).
### Changed
- Updated file hierarchy for Docker Compose.
- All configuration was moved out to `.env` file.
- No directories generated from Docker mounts. Now all mounts are done to named volumes.

## [0.2.1-alpha] - 2018-03-09
### Added
- Enter parameters for certificate from CLI.
- Continuous integrations setup.
- Push release images to Docker Hub.
- A separate setup for end users.
- Started test coverage.
- Convenient way to generate a new genesis block.
- A fixed amount of token is burnt on a certificate issuance.
### Changed
- Transactions: unified data structures and transaction processors.
- Faster startup in Docker containers for end users and separate Docker container for development purposes (instant
source code updates).
### Security
- Reviewed and fixed security issues on token operations.

## [0.1.0-alpha] – 2018-02-22
### Added
- The architecture and high-level logic of working with SSL / TLS certificates have been developed: issuing and revoked
certificates on the REMME blockchain (REMchain) level;
- The basic elements of the economy of the REM token have been integrated in the form of a mechanism for the token
emission and the possibility of their transfer between users at the REMchain level;
- A command-line interface (CLI) for convenient access to the core functionality (issuing and revoking certificates,
transferring REM tokens between users) has been incorporated.
