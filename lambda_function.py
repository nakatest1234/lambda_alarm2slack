import os
import sys
import json
import urllib.request, urllib.error
import re

# handler
def lambda_handler(event, context):
	# check keys
	if (event.get('Records')):
		if (len(event.get('Records'))):
			Message = event.get('Records')[0].get('Sns', {}).get('Message')
			if (Message is None):
				return -1
			else:
				process(Message)

	return 0


# main
def process(Message):
	msg = json.loads(Message)

	if (msg.get('source')=='aws.batch'):
		print('process: aws.batch')
		attachments = get_attachments_batch(msg)
		chatwork_msg = get_attachments_batch_cw(msg)
	elif ('AlarmName' in msg):
		print('process: alarm')
		attachments = get_attachments_alarm(msg)
		chatwork_msg = get_attachments_alarm_cw(msg)
	else:
		return

	# slack
	slack({'attachments':attachments});

	# chatwork
	chatwork(chatwork_msg)

	return


# alarm
def get_attachments_alarm(msg):
	attachments = [
		{
			'color': 'good' if (msg['NewStateValue']=='OK') else 'danger',
			'text': msg['StateChangeTime']+'(UTC)',
			'fields': [
				{
					'title': msg['AlarmName'],
					'value': msg['AlarmDescription'],
					'short': True,
				},
				{
					'title': 'state',
					'value': '{old}->{new}'.format(old=msg['OldStateValue'],new=msg['NewStateValue']),
					'short': True,
				},
				{
					'value': '```'+msg['NewStateReason']+'```',
					'short': False
				},
			],
		}
	];

	return attachments


# batch
def get_attachments_batch(msg):
	detail = msg['detail']
	re_colon = re.compile(r'(?:.*?):(?:.*?):(?:.*?):(?:.*?):(?:.*?):(.*)')

	attachments = [
		{
			'color': 'danger',
			'text': msg['time']+'(UTC)',
			'fields': [
				{
					'title': 'jobName',
					'value': detail['jobName'],
					'short': True,
				},
				{
					'title': 'statusReason',
					'value': detail['statusReason'],
					'short': True,
				},
				{
					'title': 'jobQueue',
					'value': re_colon.sub(r'\1', detail['jobQueue']),
					'short': True,
				},
				{
					'title': 'jobDef',
					'value': re_colon.sub(r'\1', detail['jobDefinition']),
					'short': True,
				},
				{
					'value': '```'+str(detail['container']['command'])+'```',
					'short': False,
				},
				{
					'value': '```'+detail['container']['reason']+'```',
					'short': False
				},
			],
		}
	];

	return attachments


# alarm cw
def get_attachments_alarm_cw(msg):
	to = os.environ.get('CHATWORK_TO', '')

	if len(to) > 0:
		to += "\n"

	return "{to}[code]Name: {name}\nDescription: {desc}\nstate: {state}\ndetail: {detail}[/code]".format(
		to=to,
		name=msg['AlarmName'],
		desc=msg['AlarmDescription'],
		state='{old}->{new}'.format(old=msg['OldStateValue'],new=msg['NewStateValue']),
		detail=msg['NewStateReason'],
	)


# batch cw
def get_attachments_batch_cw(msg):
	detail = msg['detail']
	re_colon = re.compile(r'(?:.*?):(?:.*?):(?:.*?):(?:.*?):(?:.*?):(.*)')
	to = os.environ.get('CHATWORK_TO', '')

	if len(to) > 0:
		to += "\n"

	return "{to}[code]jobName: {jobName}\nstatusReason: {statusReason}\njobQueue: {jobQueue}\njobDef: {jobDef}\ncommand: {command}\nreason: {reason}[/code]".format(
		to=to,
		jobName=detail['jobName'],
		statusReason=detail['statusReason'],
		jobQueue=re_colon.sub(r'\1', detail['jobQueue']),
		jobDef=re_colon.sub(r'\1', detail['jobDefinition']),
		command=str(detail['container']['command']),
		reason=str(detail['container']['reason']),
	)


# slack
def slack(opt=None):
	url = os.environ.get('SLACK_ENDPOINT', '')

	if (url):
		payload = {
			'channel': os.environ.get('SLACK_CHANNEL', '#general'),
			'username': os.environ.get('SLACK_USERNAME', 'lambda'),
			'icon_emoji': os.environ.get('SLACK_EMOJI', ':majikayo:'),
		}

		if opt is not None:
			payload.update(opt)

		try:
			req = urllib.request.Request(
				url=url,
				data=json.dumps(payload).encode('utf-8'),
				method='POST',
				headers={'Content-Type':'application/json; charset=utf-8'},
			)
			urllib.request.urlopen(req)
		except Exception as e:
			print('Exception:', e.args, file=sys.stderr)
		except:
			print('Unexpected error:', sys.exc_info()[0], file=sys.stderr)


# chatwork
def chatwork(msg):
	CHATWORK_KEY      = os.environ.get('CHATWORK_KEY', '')
	CHATWORK_ENDPOINT = os.environ.get('CHATWORK_ENDPOINT', 'https://api.chatwork.com/v2')
	CHATWORK_ROOM     = os.environ.get('CHATWORK_ROOM', '')

	if (CHATWORK_KEY):
		url = '{}/rooms/{}/messages'.format(CHATWORK_ENDPOINT, CHATWORK_ROOM)

		try:
			req = urllib.request.Request(
				url=url,
				data=urllib.parse.urlencode({'body':msg}).encode('utf-8'),
				method='POST',
				headers={'X-ChatWorkToken':CHATWORK_KEY},
			)
			urllib.request.urlopen(req)
		except Exception as e:
			print('Exception:', e.args, file=sys.stderr)
		except:
			print('Unexpected error:', sys.exc_info()[0], file=sys.stderr)
