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
from pkg_resources import resource_filename
import connexion
from flask_cors import CORS
from remme.rest_api.api_methods_switcher import RestMethodsSwitcherResolver

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('--bind', default='0.0.0.0')
    arguments = parser.parse_args()
    app = connexion.FlaskApp(__name__, specification_dir='.')
    CORS(app.app)
    app.add_api(resource_filename(__name__, 'openapi.yml'), resolver=RestMethodsSwitcherResolver('remme.rest_api'))
    app.run(port=arguments.port, host=arguments.bind)
