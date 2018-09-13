************
Introduction
************

Overview
========

REMchain - a multi-purpose blockchain service allowing one to store certificate's hash and other important data for verification purposes.

REMME uses python framework Sawtooth by Hyperledger to develop business logic on top of it. A custom consensus is planned to be implemented using Rust language.
The node at its services are wrapped in **Docker containers** and may be run in "one-click".

In order to interact with the node, JS client is provided that uses ES6 standard.

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