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

# pylint: disable=invalid-name
import requests

DEALER_ADDRESS = 'http://configuration-dealer.remme-test.svc.cluster.local:8000/'
PRIV_KEY_LOCATION = '/etc/sawtooth/keys/validator.priv'
PUB_KEY_LOCATION = '/etc/sawtooth/keys/validator.pub'
ENV_FILE = '/config/network-config.env'

response = requests.get(DEALER_ADDRESS)
data = response.json()

with open(PRIV_KEY_LOCATION, 'w') as f:
    f.write(data['privkey'])

with open(PUB_KEY_LOCATION, 'w') as f:
    f.write(data['pubkey'])

ip = data['ip']
run_mode = data['run_mode']
seeds = data['peers']
env_contents = f'REMME_VALIDATOR_IP={ip}\nREMME_START_MODE={run_mode}\nSEEDS_LIST={seeds}'

with open(ENV_FILE, 'w') as f:
    f.write(env_contents)
