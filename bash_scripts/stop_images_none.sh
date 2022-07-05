#! /bin/bash
COUNTER = 1
for image in $(docker images | awk '{print $1, $3}' | grep '<none>' | awk '{print $2}'); do
	if [ $COUNTER -eq 1 ]; then
        continue
        fi
    COUNTER = COUNTER +1
    echo "Removing image $image ..."
    docker image rm $image
done