#!/usr/bin/env python3

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

"""Statistics for metrics collected in InfluxDB.

Usage:
    influxdb_stats.py <influx_host> <port> <user> <password> <db> <node> <metric>

Options:
    influx_host    InfluxDB host that we should work with.
    port           InfluxDB port.
    user           InfluxDB user.
    password       InfluxDB password.
    db             The exact database that stores the metrics.
    node           Node that was sending the metrics.
    metric         The exact metric that we are collecting.

Options:
    -h --help    Show this screen.
    --version    Show version.
"""
from datetime import datetime
from docopt import docopt
from influxdb import DataFrameClient
import seaborn

if __name__ == '__main__':
    args = docopt(__doc__, version='0.1')
    args = {k[1:-1]: v for k, v in args.items()}
    print(args)
    client = DataFrameClient(
        args['influx_host'],
        args['port'],
        args['user'],
        args['password'],
        args['db']
    )
    node = args['node']
    metric = args['metric']
    res = client.query(f'select "execution_time" from "{metric}","{node}"')
    res = res[metric]
    print('Median metric value:', res.median(), 'seconds')
    print('Mean metric value:', res.mean(), 'seconds')
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%SZ')
    plot_title = f'CDF of {metric} on {node}'
    seaborn \
        .distplot(
            res,
            axlabel='Execution time (seconds)',
            hist=False,
            kde_kws=dict(cumulative=True)
        ) \
        .get_figure() \
        .savefig(f'{time} {plot_title}.png')
    plot_title = f'Histogram of {metric} on {node}'
    seaborn \
        .distplot(
            res,
            axlabel='Execution time (seconds)'
        ) \
        .get_figure() \
        .savefig(f'{time} {plot_title}.png')
