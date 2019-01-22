# Copyright 2018 REMME
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------

"""Metrics collection system for REMME Core.

This module contains wrappers around metrics system to make metrics collection
easy to use. The metric collection mechanism is based on InfluxDB.
"""

import logging
import platform
from requests.exceptions import ConnectionError
import time
from datetime import datetime
from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError, InfluxDBServerError
from remme.settings.default import load_toml_with_defaults

LOGGER = logging.getLogger(__name__)


class _TimeMeasurement:
    """The class used to measure times and send the metric to the collector.
    """
    def __init__(self, metrics_sender, metric):
        """Initialize time measurement.

        The measurement will start from the moment of initialization of an
        instance and will finish the measurement on the `done()` call.

        :param metrics_sender: `MetricsSender` instance.
        :param metric: The name of the metric.
        """
        if not isinstance(metrics_sender, MetricsSender):
            raise ValueError(f'Expected `metrics_sender` to be an instance of '
                             f'MetricsSender, got type {type(metrics_sender)}')
        if not isinstance(metric, str):
            raise ValueError(f'Expected `metric` to be a string, got type '
                             f'{type(metric)}')

        self._metrics_sender = metrics_sender
        self._metric = metric
        self._done = False
        self._start_time = time.time()

    def done(self):
        """Sends the time metric to the collector.

        The metric format is
            {
                'execution_time': stop_time - self._start_time
            }
        """
        if self._done:
            return

        stop_time = time.time()
        self._done = True
        values = {
            'execution_time': stop_time - self._start_time
        }
        self._metrics_sender.send_metric(self._metric, values)


class MetricsSender:
    """The wrapper around low-level metrics routines

    This class performs the majority of routine related to metrics, such as
    connecting to InfluxDB and constructing requests.
    """
    def __init__(self, address, port, user, password, db):
        """Initialize metrics collection.

        This wrapper tests the connection at the time of initialization. If the
        connection was not successful no exception is thrown. Writing to such
        connection with `send_metric` will have no effect.

        If the specified database does not exist this wrapper will try to create
        it.

        :param address: The IP address or DNS name of the InfluxDB server.
        :param port: The port exposed by the InfluxDB server.
        :param user: InfluxDB user name.
        :param password: InfluxDB user password.
        :param db: The name of the database for metrics.
        """
        self._influxdb_client = InfluxDBClient(address, port, user, password)
        self._ready = False

        try:
            self._influxdb_client.ping()
            LOGGER.info(f'Successfully connected to the InfluxDB instance on '
                        f'{address}:{port}.')
        except (InfluxDBClientError, InfluxDBServerError, ConnectionError):
            LOGGER.error(f'Cannot connect to the InfluxDB instance on '
                         f'{address}:{port}.')
            return

        try:
            self._influxdb_client.create_database(db)
            LOGGER.info(f'Created the `{db}` database in InfluxDB.')
        except InfluxDBClientError:
            # The DB already exists
            pass
        except InfluxDBServerError:
            LOGGER.error(f'Caught server error while trying to create the '
                         f'`{db}` database in InfluxDB.')
            return

        self._influxdb_client.switch_database(db)
        self._ready = True

    def send_metric(self, metric, values):
        """Send metrics to the database.

        If the connection initialization was not successful, this method will do
        nothing.

        :param metric: The name of the metric (will be prefixed with "remme").
        :param values: The dict of values for the metric.

        :Example:

        >>> metrics_sender = MetricsSender("localhost", 8086, "user", "password", "db")
        >>> metrics_sender.send_metric("processing_time", { "value": 100 })
        """
        if not self._ready:
            return

        if not isinstance(metric, str):
            raise ValueError(f'Metric name should be a string, got '
                             f'{type(metric)}.')
        if not isinstance(values, dict):
            raise ValueError(f'Values should be in a dict, got type '
                             f'{type(values)}.')

        data_point = {
            'measurement': f'remme.{metric}',
            'tags': {
                'hostname': platform.node()
            },
            'time': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
            'fields': values
        }

        try:
            self._influxdb_client.write_points([data_point])
        except InfluxDBClientError:
            LOGGER.error(f'Failed to send metrics because of a client error.')
        except InfluxDBServerError:
            LOGGER.error(f'Failed to send metrics because of a server error.')

    def get_time_measurement(self, metric):
        """Used to measure execution times of different procedures.

        :param metric: The name of the metric (will be prefixed with "remme").
        :return: `_TimeMeasurement` object used to measure times and send the metric.

        :Example:

        >>> metrics_sender = MetricsSender("localhost", 8086, "user", "password", "db")
        >>> measurement = metrics_sender.get_time_measurement("processing_time")
        >>> # do some work...
        >>> # this will measure the time from `measurement` init and send the metric
        >>> measurement.done()
        """
        return _TimeMeasurement(self, metric)


config = load_toml_with_defaults('/config/remme-client-config.toml')['remme']['metrics']

METRICS_SENDER = MetricsSender(
    config['influxdb_address'],
    config['influxdb_port'],
    config['influxdb_user'],
    config['influxdb_password'],
    config['influxdb_database']
)
"""Global MetricsSender instance initialized from the configuration file.
"""
