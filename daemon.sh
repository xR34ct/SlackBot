#!/bin/sh

start () { 
	/home/xr34ct/morpheus/bin/python /home/xr34ct/Documents/morpheus/morpheus.py > /dev/null 2>&1 &
}

stop () {
	pid=$(pgrep -f morpheus)
	kill "$pid"
}

case $1 in
	start|stop) "$1" ;;
esac
