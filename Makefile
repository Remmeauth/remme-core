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

.PHONY: clean run_genesis run_genesis_bg stop_genesis run run_bg stop run_docs
.PHONY: run_logio run_logio_bg stop_logio test release docker_push docs build
.PHONY: test

RUN_SCRIPT=./scripts/run.sh
BUILD_DIR=./build

build:
	$(BUILD_DIR)/build.sh -r

build_dev:
	$(BUILD_DIR)/build.sh

clean:
	$(BUILD_DIR)/clean.sh

docker_push:
	$(BUILD_DIR)/push-docker.sh

run_genesis:
	$(RUN_SCRIPT) -g -u

run_genesis_bg:
	$(RUN_SCRIPT) -g -u -b

stop_genesis:
	$(RUN_SCRIPT) -g -d

run:
	$(RUN_SCRIPT) -u

run_bg:
	$(RUN_SCRIPT) -u -b

restart_no_genesis:
	make stop && make build_dev && make run

restart:
	make stop && make build_dev && make run_genesis

restart_bg:
	make stop && make build_dev && make run_genesis_bg

stop:
	$(RUN_SCRIPT) -d

docs:
	$(BUILD_DIR)/build-docs.sh

run_docs:
	$(BUILD_DIR)/docs-server.sh

run_logio:
	$(RUN_SCRIPT) -l -u

run_logio_bg:
	$(RUN_SCRIPT) -l -u -b

stop_logio:
	$(RUN_SCRIPT) -l -d

test:
	$(BUILD_DIR)/test.sh

release:
	$(BUILD_DIR)/release.sh

clean_chain_data:
	docker volume rm remme_chain_data

lint:
	pylint `find . -name "*.py"`

lint_html:
	pylint --output-format=json `find . -name "*.py"` | pylint-json2html -o report.html
