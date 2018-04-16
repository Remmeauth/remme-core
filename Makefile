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

PROTO_SRC_DIR = ./protos
PROTO_DST_DIR = ./remme/protos

include .env

.PHONY: release

run_dev_no_genesis:
	docker-compose -f docker-compose.dev.yml -f docker-compose.run.yml up

run_dev:
	docker-compose -f docker-compose.dev.yml -f docker-compose.genesis.yml -f docker-compose.run.yml up

test:
	docker-compose -f docker-compose.test.yml -f docker-compose.run-test.yml up --abort-on-container-exit

build_protobuf:
	protoc -I=$(PROTO_SRC_DIR) --python_out=$(PROTO_DST_DIR) $(PROTO_SRC_DIR)/*.proto

build_docker:
	docker-compose -f docker-compose.dev.yml build

rebuild_docker:
	docker-compose -f docker-compose.dev.yml build --no-cache

release:
	mkdir $(RELEASE_NUMBER)-release
	cp {run,genesis}.sh ./$(RELEASE_NUMBER)-release
	cp docker-compose.{dev,run,genesis}.yml ./$(RELEASE_NUMBER)-release
	find ./$(RELEASE_NUMBER)-release -type f -name "docker-compose.{dev,run,genesis}.yml" | xargs sed -i "/.*build: \..*/d"
	zip -r $(RELEASE_NUMBER)-release.zip $(RELEASE_NUMBER)-release
	rm -rf $(RELEASE_NUMBER)-release
