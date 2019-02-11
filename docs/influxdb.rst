******************************
Collecting metrics to InfluxDB
******************************

Some components of our application can send metrics to an InfluxDB so we can
extract some statistics on those metrics later.

Connecting to InfluxDB
======================

Add the following to ``config/remme-client-config.toml`` and fill in your values:

.. code-block:: bash

    [remme.metrics]
    influxdb_address = "localhost"
    influxdb_port = 8086
    influxdb_user = "lrdata"
    influxdb_password = "12345678"
    influxdb_database = "lrdata"

Fetching metrics
================

All metrics are tagged with a hostname. Each transaction type has its separate
metric name, for example ``remme.tp.AtomicSwap.0`` for ``AtomicSwap.init`` (see
numbering in Protocol Buffers definitions). To fetch this metric via InfluxQL
on host ``node-1``:

``select "execution_time" from "remme.tp.AtomicSwap.0","node-1"``

Analyzing metrics
=================

We have a separate script at ``utils/execution_time_stats.py``. That script will
output the basic stats to the terminal and save CDF and histogram of the
selected metric to separate PNG files.
