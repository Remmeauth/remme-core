#!/bin/bash

sudo rm -rf /home/remme-core-$1 && \
    sudo docker rm $(sudo docker ps -a -q) -f && \
    sudo docker rmi $(sudo docker images -q) -f && \
    sudo sed -i '/REMME_CORE_RELEASE/d' ~/.bashrc && \
    echo "REMME_CORE_RELEASE=$2" >> ~/.bashrc && \
    cd /home/ && curl -L https://github.com/Remmeauth/remme-core/archive/v$2.tar.gz | sudo tar zx && \
    cd remme-core-$2 && \
    sudo -i sed -i "s@80@3333@" /home/remme-core-$2/docker/compose/admin.yml && \
    sudo -i sed -i "s@127.0.0.1@$NODE_IP_ADDRESS@" /home/remme-core-$2/config/network-config.env && \
    sudo -i sed -i '/      - GF_USERS_ALLOW_SIGN_UP=false/a \      - GF_SERVER_ROOT_URL=%(protocol)s:\/\/%(domain)s:\/monitoring\/' /home/remme-core-$2/docker/compose/mon.yml && \
    curl https://gist.githubusercontent.com/dmytrostriletskyi/8c07b752f8efd52d6f69feddd62e3af9/raw/438a72324fe8bfcaf9f56a4023eeaa1fa18ddb9a/seeds-list.txt | sudo tee config/seeds-list.txt > /dev/null && \
    sudo systemctl restart nginx && \
    sudo make run_bg_user
