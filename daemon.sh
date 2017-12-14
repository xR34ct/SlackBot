#!/bin/sh

start () { 
	/home/xr34ct/morpheus/bin/python -u /home/xr34ct/Documents/morpheus/morpheus.py monitoring 2>&1 >> /home/xr34ct/Documents/morpheus/.logs &
}

stop () {
	pid=$(pgrep -f morpheus.py)
	kill "$pid"
}

dev () {
	/home/xr34ct/morpheus/bin/python /home/xr34ct/Documents/morpheus/morpheus.py anet-testing
}


case $1 in
	start|stop|dev) "$1" ;;
esac
