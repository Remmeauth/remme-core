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

TOTAL_SUPPLY ?= 10000000000000

run_dev:
	docker-compose -f docker-compose.yml -f docker-compose.debug-rest.yml -f docker-compose.debug-tp.yml up

shell:
	docker exec -it $(shell docker-compose -f docker-compose.dev.yml ps -q shell) bash

test:
	docker-compose -f docker-compose.test.yml up --abort-on-container-exit

build_protobuf:
	protoc -I=$(PROTO_SRC_DIR) --python_out=$(PROTO_DST_DIR) $(PROTO_SRC_DIR)/*.proto

build_docker:
	docker-compose -f docker-compose.yml build

rebuild_docker:
	docker-compose -f docker-compose.yml build --no-cache
