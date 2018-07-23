#!/bin/sh

if [ "$#" -lt 1 ];then
	echo "usage ip_address"
	exit -1
fi

curl $1/on -m 0.1
