import os
import sys
import json
import urllib.request, urllib.error

def lambda_handler(event, context):

	msg = json.loads(event['Records'][0]['Sns']['Message'])

	attachments = [
		{
			'color': 'good' if (msg['NewStateValue']=='OK') else 'danger',
			'title': msg['AlarmDescription'],
			'text': msg['StateChangeTime']+'(UTC)',
			'fields': [
				{
					'title': 'ステータス',
					'value': '{old}->{new}'.format(old=msg['OldStateValue'],new=msg['NewStateValue']),
					'short': False,
				},
				{
					'title': '理由',
					'value': msg['NewStateReason'],
					'short': False
				},
			],
		}
	];

	SLACK_ENDPOINT = os.environ.get('SLACK_ENDPOINT', '')
	SLACK_CHANNEL  = os.environ.get('SLACK_CHANNEL', '#general')
	SLACK_USERNAME = os.environ.get('SLACK_USERNAME', 'lambda')
	SLACK_EMOJI    = os.environ.get('SLACK_EMOJI', ':majikayo:')

	slack(SLACK_ENDPOINT, SLACK_CHANNEL , {'attachments':attachments,'username':SLACK_USERNAME,'icon_emoji':SLACK_EMOJI});

	return []

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
