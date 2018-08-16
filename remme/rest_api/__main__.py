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

import toml
from pkg_resources import resource_filename
import connexion
# from flask_cors import CORS
from remme.rest_api.api_methods_switcher import RestMethodsSwitcherResolver
from remme.rest_api.api_handler import AioHttpApi
from remme.rest_api.validator import proxy
from remme.shared.logging import setup_logging

if __name__ == '__main__':
    config = toml.load('/config/remme-rest-api.toml')["remme"]["rest_api"]
    setup_logging('rest-api')

    parser = argparse.ArgumentParser()

    parser.add_argument('--port', type=int, default=config["port"])
    parser.add_argument('--bind', default=config["bind"])
    arguments = parser.parse_args()
    app = connexion.AioHttpApp(__name__, specification_dir='.')
    app.api_cls = AioHttpApi

    cors_config = config["cors"]
    # CORS(app.app,
    #      origins=cors_config["allow_origin"],
    #      methods=cors_config["allow_methods"],
    #      max_age=cors_config["max_age"],
    #      supports_credentials=cors_config["allow_credentials"],
    #      allow_headers=cors_config["allow_headers"],
    #      expose_headers=cors_config["expose_headers"])
    app.app.router.add_route('GET', '/api/v1/validator/{path:.*?}', proxy)
    app.add_api(resource_filename(__name__, 'openapi.yml'),
                resolver=RestMethodsSwitcherResolver('remme.rest_api', config["available_methods"]))
    app.run(port=arguments.port, host=arguments.bind)
