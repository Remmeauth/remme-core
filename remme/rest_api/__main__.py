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

import argparse
import os

from pkg_resources import resource_filename
import connexion
from flask_cors import CORS
from remme.rest_api.api_methods_switcher import RestMethodsSwitcherResolver
from remme.shared.logging import setup_logging

if __name__ == '__main__':
    setup_logging('rest-api')
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('--bind', default='0.0.0.0')
    arguments = parser.parse_args()
    app = connexion.FlaskApp(__name__, specification_dir='.')

    CORS_ALLOW_ORIGIN = os.getenv('CORS_ALLOW_ORIGIN', default='').split(',')
    CORS_EXPOSE_HEADERS = os.getenv('CORS_EXPOSE_HEADERS', default='').split(',')
    CORS_ALLOW_HEADERS = os.getenv('CORS_ALLOW_HEADERS', default='').split(',')
    CORS_ALLOW_METHODS = os.getenv('CORS_ALLOW_METHODS', default='').split(',')
    CORS_MAX_AGE = int(os.getenv('CORS_MAX_AGE', default=10000))
    CORS_ALLOW_CREDENTIALS = bool(os.getenv('CORS_ALLOW_CREDENTIALS', default=True))
    CORS(app.app, origins=CORS_ALLOW_ORIGIN, methods=CORS_ALLOW_METHODS, max_age=CORS_MAX_AGE,
                    supports_credentials=CORS_ALLOW_CREDENTIALS, allow_headers=CORS_ALLOW_HEADERS,
                    expose_headers=CORS_EXPOSE_HEADERS)

    app.add_api(resource_filename(__name__, 'openapi.yml'), resolver=RestMethodsSwitcherResolver('remme.rest_api'))
    app.run(port=arguments.port, host=arguments.bind)
