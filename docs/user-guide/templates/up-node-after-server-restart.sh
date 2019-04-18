#!/bin/bash

cd /home/remme-core-"$1"
sudo docker rm $(sudo docker ps -a -q) -f
sudo docker rmi $(sudo docker images -q) -f
sudo make run_bg_user
cd ~
