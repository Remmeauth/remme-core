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
.PHONY: test release docker_push docs build

RUN_SCRIPT=./scripts/run.sh
BUILD_DIR=./build

build:
	$(BUILD_DIR)/build.sh -r

build_dev:
	$(BUILD_DIR)/build.sh

build_protobuf:
	protoc -I=./protos --python_out=./remme/protos ./protos/*.proto

clean:
	$(BUILD_DIR)/clean.sh

docker_push:
	$(BUILD_DIR)/push-docker.sh

run_genesis:
	$(RUN_SCRIPT) -g -u

run_genesis_bg:
	$(RUN_SCRIPT) -g -u -b

run:
	$(RUN_SCRIPT) -u

run_bg:
	$(RUN_SCRIPT) -u -b

start_no_genesis:
	make stop && make build_dev && DEV=1 make run

start:
	make stop && make build_dev && DEV=1 make run_genesis

startd:
	make stop && make build_dev && DEV=1 make run_genesis_bg

stop:
	$(RUN_SCRIPT) -g -d

build_docs: build_dev
	docker-compose -f ./docker/compose/docs.yml up --abort-on-container-exit

run_docs:
	sphinx-autobuild -H 0.0.0.0 -p 8000 ./docs ./docs/html

test: build_dev
	docker-compose -f ./docker/compose/testing.yml up --abort-on-container-exit

release:
	$(BUILD_DIR)/release.sh

clean_chain_data:
	docker volume rm remme_chain_data

lint:
	pylint `find . -name "*.py"`

lint_html:
	pylint --output-format=json `find . -name "*.py"` | pylint-json2html -o report.html

enter_testing_console:
	docker run -v `realpath .`:/project/remme -it remme/remme-core:latest /bin/bash
