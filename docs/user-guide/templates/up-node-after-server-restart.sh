#!/bin/bash

cd /home/remme-core-"$1"
sudo docker rm $(sudo docker ps -a -q) -f
sudo docker rmi $(sudo docker images -q) -f
sudo make run_bg
sudo docker-compose -f remme-mon-stack-1.0.1/docker-compose.yml up -d
sudo systemctl restart nginx
cd ~
