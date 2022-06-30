#! /bin/bash

IMG_NAME=$1

for container in $(docker ps -a | awk '{print $2, $10}' | grep $IMG_NAME | awk '{print $2}'); do
	echo "Stopping container $container"
	docker stop $container
done
