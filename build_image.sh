
IMG_NAME = 'bittorrent'
for container in $(docker ps -a | awk '{print $2, $12}' | grep $IMG_NAME | awk '{print $2}'); do
	echo "Stopping container $container"
	docker stop $container
	echo "Removing container $container"
	docker container rm $container
done


for image in $(docker images | awk '{print $1, $3}' | grep 'bittorrent' | awk '{print $2}'); do
    echo "Removing image $image"
    docker image rm $image
done

docker build --tag bittorrent:0.1 .