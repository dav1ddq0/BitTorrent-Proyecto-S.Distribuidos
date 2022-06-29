#! /bin/bash

CONT_NAME=$1
docker run -itd --rm --name $CONT_NAME "bittorrent:0.1"
docker exec --workdir /home/app $CONT_NAME bash