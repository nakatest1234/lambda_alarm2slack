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
	elif ('AlarmName' in msg):
		print('process: alarm')
		attachments = get_attachments_alarm(msg)
	else:
		return

	SLACK_ENDPOINT = os.environ.get('SLACK_ENDPOINT', '')
	SLACK_CHANNEL  = os.environ.get('SLACK_CHANNEL', '#general')
	SLACK_USERNAME = os.environ.get('SLACK_USERNAME', 'lambda')
	SLACK_EMOJI    = os.environ.get('SLACK_EMOJI', ':majikayo:')

	slack(SLACK_ENDPOINT, SLACK_CHANNEL , {'attachments':attachments,'username':SLACK_USERNAME,'icon_emoji':SLACK_EMOJI});

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
					'title': 'ステータス',
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


# slack
def slack(url, channel, opt=None):
	payload = {
		'channel': channel,
	}

	if opt is not None:
		payload.update(opt)

	if (url):
		try:
			req = urllib.request.Request(
				url=url,
				data=json.dumps(payload).encode('utf-8'),
				method='POST',
				headers={'Content-Type':'application/json; charset=utf-8'},
			)
			urllib.request.urlopen(req)
		except Exception as e:
			print('Exception:', e.args[0], e.args[1], file=sys.stderr)
		except:
			print('Unexpected error:', sys.exc_info()[0], file=sys.stderr)
