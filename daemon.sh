#!/bin/sh

start () { 
	/home/xr34ct/morpheus/bin/python /home/xr34ct/Documents/morpheus/morpheus.py monitoring > /home/xr34ct/Documents/morpheus/.logs 2>&1 &
}

stop () {
	pid=$(pgrep -f morpheus)
	kill "$pid"
}

dev () {
	/home/xr34ct/morpheus/bin/python /home/xr34ct/Documents/morpheus/morpheus.py anet-testing
}


case $1 in
	start|stop|dev) "$1" ;;
esac
