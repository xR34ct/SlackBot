#!/bin/bash

function sweep() {
  hosts=$(grep -v '^#' "$inventory"| sed '/^$/d')
  alerts_file="$1"
  touch "$alerts_file"
  tmpfile=$(mktemp)
  while read -r host; do
	port=$(awk '{print $2}' <<< "$host")
	ip=$(awk '{print $1}' <<< "$host")
        name=$(host "$ip" | awk '{ print $5 }')
        service=$(awk '{print $3}' <<< "$host")
	result=$(nmap "$ip" -p "$port" --open | grep "open")
	in_alerts=$(grep "$ip" "$alerts_file" | grep "$port")
	if [[ "$result" ]] && [[ "$in_alerts" ]]; then
		printf "Host: %-16s %-30s Port: %s (%s)\t [%b]\n" "$ip" "($name)" "$port" "$service" "\e[1;32mRESOLVED\e[0m"
		grep -v "$in_alerts" "$alerts_file" > "$tmpfile"
		cat "$tmpfile" > "$alerts_file"
                pre_response="The following service just became RESOLVED:"
                response="$service on $name - $ip"
                #color="good"
                color="#00FF00"
                notify "$pre_response" "$response" "$color"

	elif [[ -z "$result" ]] && [[ -z "$in_alerts" ]]; then 
		printf "Host: %-16s %-30s Port: %s (%s)\t [%b]\n" "$ip" "($name)" "$port" "$service" "\e[1;31mDOWN\e[0m"
		printf "%s\t %s\n" "$ip" "$port" >> "$alerts_file"
		pre_response="The following service just went DOWN:"
                response="$service on $name - $ip"
#                color="danger"
                color="#FF0000"
                notify "$pre_response" "$response" "$color"

       	else
		printf "Host: %-16s %-30s Port: %s (%s)\t [%b]\n" "$ip" "($name)" "$port" "$service" "\e[1;33mUNCHAGNED\e[0m"
	fi
 done <<< "$hosts"
 rm "$tmpfile"
}

function notify(){
   local pipe=/tmp/monitor_pipe
   if [ ! -f "$pipe" ] ; then
       mkfifo "$pipe"
   fi
   local pre="$1"
   local resp="$2"
   local col="$3"
   #echo "$pre" > "$pipe"
   #echo "$resp" > "$pipe"
   #echo "$col" > "$pipe"
   echo "$pre
$resp
$col" > "$pipe"
}

inventory=''
help=''

# Check flags
while getopts 'hi:' flag; do
  case "${flag}" in
    h) help=true ;;
    i) inventory="${OPTARG}" ;;
  esac
done

if [[ -z "$inventory" ]]; then
  help=true
fi

if [[ $help ]] ; then
  echo "Nmap an inventory list with ip address and port."
  echo "Usage: inventory-sweep.sh [-h[elp]] -i [inventory]"
  echo "Inventory should be on the format: "
  echo "127.0.0.1 80  http"
  exit 0
fi



sweep "/tmp/inventory-alerts"
