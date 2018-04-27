# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [0.3.1-alpha] - 2018-04-16
### Added
- REST API:
  - Support for certificate signing requests. Now key pairs for repositories can be generated on the client side.
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
