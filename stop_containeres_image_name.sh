#!/bin/bash
# IMG_NAME=$1

for container in $(docker ps | awk '{print $10}'); do
	echo "Stopping container $container"
	docker stop $container
	echo "Removing container $container"
	docker container rm $container
done

