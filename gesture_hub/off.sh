#!/bin/sh

if [ "$#" -lt 1 ]; then
	echo 'usage ip address'
	exit -1
fi

curl $1/off -m 0.1
