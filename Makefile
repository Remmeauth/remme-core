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
RELEASE_NUMBER ?= $(shell git describe --abbrev=0 --tags)

include .env

.PHONY: release

restart_dev:
	docker-compose -f docker-compose/dev.yml -f docker-compose/genesis.yml -f docker-compose/run.yml down
	docker-compose -f docker-compose/dev.yml -f docker-compose/genesis.yml -f docker-compose/run.yml build
	docker-compose -f docker-compose/dev.yml -f docker-compose/genesis.yml -f docker-compose/run.yml up -d

run_dev_no_genesis:
	docker-compose -f docker-compose/base.yml up --build

run_dev:
	docker-compose -f docker-compose/base.yml -f docker-compose/genesis.yml up --build

run_docs:
	docker-compose -f docker-compose/docs.yml up --build

poet_enroll_validators_list:
	docker exec -it $(shell docker-compose -f docker-compose/dev.yml ps -q validator) bash -c "poet registration \
	create -k /etc/sawtooth/keys/validator.priv -o enroll_poet.batch && sawtooth batch submit -f enroll_poet.batch --url http://rest-api:8080"

test:
	docker-compose -f docker-compose/test.yml up --build --abort-on-container-exit

build_protobuf:
	protoc -I=$(PROTO_SRC_DIR) --python_out=$(PROTO_DST_DIR) $(PROTO_SRC_DIR)/*.proto

rebuild_docker:
	docker-compose -f docker-compose/dev.yml build --no-cache

release:
	docker-compose -f docker-compose/dev.yml build
	mkdir $(RELEASE_NUMBER)-release
	mkdir $(RELEASE_NUMBER)-release/docker-compose
	cp {run,genesis}.sh ./$(RELEASE_NUMBER)-release
	cp docker-compose/{dev,run,genesis}.yml ./$(RELEASE_NUMBER)-release/docker-compose
	cp .env ./$(RELEASE_NUMBER)-release
	find ./$(RELEASE_NUMBER)-release -type f -name "docker-compose/{dev,run,genesis}.yml" | xargs sed -i "/.*build: ..*/d"
	zip -r $(RELEASE_NUMBER)-release.zip $(RELEASE_NUMBER)-release
	rm -rf $(RELEASE_NUMBER)-release
