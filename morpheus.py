import os
import sys
import time
import socket
import subprocess
from threading import Thread
from slackclient import SlackClient
import ipgetter
import json
from env import *

#BOT_ID = os.environ.get("BOT_ID")
AT_BOT = "<@" + BOT_ID + ">"

INVENTORY_FILE = "/etc/avdagic.net/inv"
OUTAGE_FILE = "/tmp/inventory-alerts"
#ALERT_CHANNEL = "#monitoring"
COMMANDS = ['list', 'inventory', 'outages', 'scan/sweep', 'ip']
ALERT_CHANNEL = sys.argv[1]

# instantiate Slack & Twilio clients
slack_client = SlackClient(SLACK_BOT_TOKEN)

def response_list():
    print ("Preparing response list...")
    pre_response = 'These are the commands the gods anwser to'
    response = '\n'.join(COMMANDS)
    return {'pre_response':pre_response, 'response':response}

def response_ip():
    print ("Preparing response ip")
    pre_response = 'The IP of the gods is:'
    response = ipgetter.myip()
    return {'pre_response':pre_response, 'response':response}

def response_scan():
    print ("Preparing response scan")
    command = "/bin/bash inventory_sweep.sh -i " + INVENTORY_FILE
    process = subprocess.Popen(command.split())
    output, error = process.communicate()
    return {'pre_response':'The gods will now be scaned', 'response':response}

def response_inventory():
    response = ''
    color = 'good'
    try:
        with open(INVENTORY_FILE) as f: s = f.read()
        if os.stat(INVENTORY_FILE).st_size == 0:
            pre_response = 'Nothing here Mortal'
            response = 'The inventory of the gods is empty'
            color = 'danger'
            return {'pre_response':pre_response, 'response':response, 'color':color}
        pre_response = 'The gods are offering these services:'
        response = s
        return {'pre_response':pre_response, 'response':response, 'color':color}
    except IOError:
        pre_resonse = 'Nothing here Mortal'
        response = 'Could not find the inventory of the gods'
        color = 'danger'
        return {'pre_response':pre_response, 'response':response, 'color':color}

def response_outages():
    try:
        with open(OUTAGE_FILE) as f: s = f.read
        if os.stat(OUTAGE_FILE).st_size == 0:
            pre_response = 'The god are generous Mortal'
            response = 'No services are down'
            color = 'good'    
            return {'pre_response':pre_response, 'response':response, 'color':color}
        else:
            pre_response = 'The following services of the gods are unavailable:'
            response = s
            color = 'danger'
            return {'pre_response':pre_response, 'response':response, 'color':color}               
    except IOError:
        pre_response = 'The god are generous Mortal'
        response = 'No services are down'
        color = 'good'
        return {'pre_response':pre_response, 'response':response, 'color':color}    

PIPE_FILE = "/tmp/monitor_pipe"
if not os.path.exists(PIPE_FILE):
    os.mkfifo(PIPE_FILE)
monitor_pipe = os.open(PIPE_FILE, os.O_RDONLY | os.O_NONBLOCK)

def monitor_alerts(pipefd):
    while True:
        with open(PIPE_FILE, 'r') as fifo:
            pre_response = fifo.readline()
            response = fifo.readline()
            color = fifo.readline()
            color = "'" + color[0:7] + "'"
            msg = json.dumps([{'pretext':pre_response,'text':response,'color':color,'mrkdwn_in':['pretext','text']}])
            slack_client.api_call("chat.postMessage",channel=ALERT_CHANNEL,text='',attachments=msg, as_user=True)
        time.sleep(1)

def handle_command(command, channel):
    pre_response = "Not sure what you mean Mortal"
    response = "See list to see what you can ask the gods"
    color = '#00FFFF'
    if command.startswith("inventory"):
        result = response_inventory()
        pre_response=result['pre_response']
        response=result['response']
        color=result['color']

    elif command.startswith("list"):
        result = response_list()
        pre_response=result['pre_response']
        response=result['response']

    elif command.startswith("outages"):
        result = response_outages()
        pre_response=result['pre_response']
        response=result['response']
        color=result['color']

    elif command.startswith("scan") or  command.startswith("sweep"):
        result = response_scan()
        pre_response=result['pre_response']
        response=result['response']

    elif command.startswith("ip"):
        result = response_ip()
        pre_response=result['pre_response']
        response=result['response']
        

    msg = json.dumps([{'pretext':pre_response,'text':response,'color':color,'mrkdwn_in':['pretext','text']}])
    slack_client.api_call("chat.postMessage",channel=channel,text='',attachments=msg, as_user=True)


def parse_slack_output(slack_rtm_output):
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None

if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 
    if slack_client.rtm_connect():
        print("Morpheus connected and running!")
        thread = Thread(target=monitor_alerts, args =[monitor_pipe] )
        thread.start()
        while True:
            try:
                command, channel = parse_slack_output(slack_client.rtm_read())
                if command and channel:
                    handle_command(command, channel)
                time.sleep(READ_WEBSOCKET_DELAY)
            except socket.error:
                slack_client.rtm_connect()
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
