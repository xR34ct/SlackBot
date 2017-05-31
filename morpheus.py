import os
import time
from slackclient import SlackClient
from env import *

AT_BOT = "<@" + BOT_ID + ">"

slack_client = SlackClient(SLACK_BOT_TOKEN)


def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Not sure what you mean Mortal"
    if command.startswith('inv'):
	try:
	       	with open('../scripts/.inv') as f: s = f.read()
		response = 'The gods are offering these services:\n\n' + s
	except OSError:
		response = 'Nothing here Mortal'
    if command.startswith('ok'):
	try:
		if os.stat('../scripts/.alerts').st_size > 0:
			with open('../scripts/.alerts') as f: s = f.read()
			response = 'The following services of the gods are unavailable:\n\n' + s
		else:
			response = 'The god are generous Mortal'
	except OSError:
		response = 'Nothing here Mortal'
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None

if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("Morpheus connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
