#!/bin/bash

for container in $(docker ps -a | grep -oP "tracker_serv(\d)*"); do
	echo "Stoping container $container"
	docker stop $container > /dev/null
	echo "Removing container $container"
	docker container rm $container > /dev/null
done

