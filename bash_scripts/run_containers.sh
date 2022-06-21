#!/bin/bash

CONT_AMOUNT=$1
CONT_BASE_NAME='tracker_serv'
# TERM='alacritty'

CURR_CONTS=$(docker ps -a | wc -l)
for num in $(seq 1 $CONT_AMOUNT); do
	echo "Initializing tracker docker containers"
	CONT_NAME="$CONT_BASE_NAME$num"
	docker create -it --name $CONT_NAME "tracker:1.0" &
	BACK_PID=$!
	while kill -0 $BACK_PID ; do
		echo "Process is still active..."
		sleep 1
	done
	docker start $CONT_NAME
done
