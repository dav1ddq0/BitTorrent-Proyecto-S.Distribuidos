#! /bin/bash

CONT_AMOUNT=$1
CONT_BASE_NAME='bittorrent_client'

ONCE='./bittorrent_once.sh'

CURR_CONTS=$(docker ps -a | wc -l)
for num in $(seq 1 $CONT_AMOUNT); do
	echo "Initializing tracker docker containers ..."
	CONT_NAME="$CONT_BASE_NAME$num"
	if [ "$num" -eq "1" ]; then
		echo "Creating first container"
		$TERM -e $ONCE $CONT_NAME &
	else
		echo "Waiting for last container to create ..."
		while [ "$(docker ps -a | wc -l)" -eq "$CURR_CONTS" ]; do
			sleep 1
		done

		$TERM -e $ONCE $CONT_NAME &
	fi
done
