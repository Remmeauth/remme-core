# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [0.2.0-alpha] - 2018-03-05
### Added
- Enter parameters for certificate from CLI.
- Continuous integrations setup.
- Push release images to Docker Hub.
- A separate setup for end users.
- Started test coverage.
### Changed
- Transactions: unified data structures and transaction processors.
- Faster startup in Docker containers for end users and separate Docker container for development purposes (instant source code updates).
### Security
- Reviewed and fixed security issues on token operations.

## [0.1.0-alpha] – 2018-02-22
### Added
- The architecture and high-level logic of working with SSL / TLS certificates have been developed: issuing and revoked certificates on the REMME blockchain (REMchain) level;
- The basic elements of the economy of the REM token have been integrated in the form of a mechanism for the token emission and the possibility of their transfer between users at the REMchain level;
- A command-line interface (CLI) for convenient access to the core functionality (issuing and revoking certificates, transferring REM tokens between users) has been incorporated.
