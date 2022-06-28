#!/bin/bash

for container in $(docker ps -a | grep -oP "mngr|tracker_serv(\d)*"); do
	echo "Stopping container $container"
	docker stop $container
	echo "Removing container $container"
	docker container rm $container
done

