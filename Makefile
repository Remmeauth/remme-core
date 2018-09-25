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

RELEASE_NUMBER ?= $(shell git describe --abbrev=0 --tags)

include ./config/network-config.env

.PHONY: release

build:
	docker-compose -f docker-compose/build.yml build

restart_dev:
	docker-compose -f docker-compose/base.yml -f docker-compose/genesis.yml --project-name remme down
	docker-compose -f docker-compose/build.yml build
	docker-compose -f docker-compose/base.yml -f docker-compose/genesis.yml --project-name remme up -d

run_dev_no_genesis: build
	docker-compose -f docker-compose/base.yml up

run_dev: build
	docker-compose -f docker-compose/base.yml -f docker-compose/genesis.yml --project-name remme up

run_docs:
	docker-compose -f docker-compose/docs.yml up --build

run_logio:
	docker-compose -f docker-compose/logio.yml --project-name remme up 

test:
	docker build --target build -t remme/remme-core-dev:latest .
	docker-compose -f docker-compose/test.yml up --build --abort-on-container-exit

rebuild_docker:
	docker-compose -f docker-compose/base.yml build --no-cache

release:
	git checkout $(RELEASE_NUMBER)
	docker-compose -f docker-compose/build.yml build
	mkdir $(RELEASE_NUMBER)-release
	mkdir $(RELEASE_NUMBER)-release/docker-compose
	cp {run,genesis}.sh ./$(RELEASE_NUMBER)-release
	cp docker-compose/{base,genesis}.yml ./$(RELEASE_NUMBER)-release/docker-compose
	docker tag remme/remme-core:latest remme/remme-core:$(RELEASE_NUMBER)
	sed -i -e 's/remme-core:latest/remme-core:$(RELEASE_NUMBER)/' $(RELEASE_NUMBER)-release/docker-compose/*.yml
	cp -R config ./$(RELEASE_NUMBER)-release
	git checkout @{-1}
