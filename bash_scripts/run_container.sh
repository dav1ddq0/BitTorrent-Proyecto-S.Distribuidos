#!/bin/bash

CONT_NAME=$1
docker run -itd --rm --name $CONT_NAME "tracker:1.0"
docker exec --workdir /home/app $CONT_NAME python server_test.py
