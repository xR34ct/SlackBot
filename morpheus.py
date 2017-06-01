import os
import time
from slackclient import SlackClient
from env import *
import time
from threading import Thread
import subprocess

AT_BOT = "<@" + BOT_ID + ">"
slack_client = SlackClient(SLACK_BOT_TOKEN)

def monitor():
	alerts = {}
	channel = 'Monitoring'
	while True:
		for line in open(FILE_PATH+'.inv','r'):
			if not "#" in line:
				line = line.strip()
				col = line.split()
	                        ORDER = str(col[0])
        	                IP = str(col[1])
                	        PORT = str(col[2])
                        	SERVICE = str(col[3])
	                        IN_ALERTS = 'false'
        	                ps = subprocess.Popen((['/usr/bin/nmap',IP,'-p',PORT,'--open']), stdout=subprocess.PIPE)
				try:
					RESULT = subprocess.check_output(('grep','open'), stdin=ps.stdout)
					returncode = 0
				except subprocess.CalledProcessError as ex:
					RESULT = ''
					returncode = ex.returncode
					if returncode != 1:
						raise

                	        if bool(alerts):
                        	        if ORDER in alerts:
                                	        IN_ALERTS = 'true'

	                        if bool(RESULT) and IN_ALERTS == 'true':
					print('UP')
					#For Slack automatic
        	                        del alerts[ORDER]
					response = SERVICE + ' on ' + IP + ':' + PORT + ' is resolved'
					slack_client.api_call("chat.postMessage", channel=channel,text=response, as_user=True)
			
					#For Slack question
					f = open(FILE_PATH + '.alerts','r')
					rader = f.readlines()
					f.close()
					f = open(FILE_PATH + '.alerts','w')
					for rad in rader:
						if rad != str(IP) + '\t' + str(PORT):
							f.write(rad)
					f.close()
                	        elif not bool(RESULT) and IN_ALERTS == 'false':
					print('DOWN')
					#For Slack automatic
                        	        alerts[ORDER] = ORDER
					response = SERVICE + ' on ' + IP + ':' + PORT + ' is DOWN'
                                        slack_client.api_call("chat.postMessage", channel=channel,text=response, as_user=True)

					#For Slack question
					f = open(FILE_PATH + '.alerts','w')
					f.write(IP + '\t' + PORT + '\n')
					f.close() 
	time.sleep(1)


def handle_command(command, channel):
	response = "Not sure what you mean Mortal"
	if command.startswith('inv'):
		try:
		       	with open(FILE_PATH + '.inv') as f: s = f.read()
			response = 'The gods are offering these services:\n' + s
		except OSError:
			response = 'Nothing here Mortal'
	if command.startswith('ok'):
		try:
			if os.stat(FILE_PATH + '.alerts').st_size > 0:
				with open(FILE_PATH + '.alerts') as f: s = f.read()
				response = 'The following services of the gods are unavailable:\n' + s
			else:
				response = 'The god are generous Mortal'
		except OSError:
				response = 'Nothing here Mortal'
	slack_client.api_call("chat.postMessage", channel=channel,text=response, as_user=True)

def parse_slack_output(slack_rtm_output):
	output_list = slack_rtm_output
	if output_list and len(output_list) > 0:
       		for output in output_list:
			if output and 'text' in output and AT_BOT in output['text']:
		                return output['text'].split(AT_BOT)[1].strip().lower(), \
                      			output['channel']
	return None, None

if __name__ == "__main__":
	READ_WEBSOCKET_DELAY = 1
	if slack_client.rtm_connect():
		print("Morpheus connected and running!")
		thread = Thread(target=monitor)
		thread.start()
		while True:
			command, channel = parse_slack_output(slack_client.rtm_read())
			if command and channel:
				handle_command(command, channel)
				time.sleep(READ_WEBSOCKET_DELAY)
	else:
        	print("Connection failed. Invalid Slack token or bot ID?")
