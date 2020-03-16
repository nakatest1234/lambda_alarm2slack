import urllib.request, urllib.error, urllib.parse

# AoSSMS
def aos(send_to, message):
	url = os.environ.get('AOS_ENDPOINT', '')

	if (url):
		payload = {
			'token': os.environ.get('token', ''),
			'clientId': os.environ.get('clientId', ''),
			'smsCode': os.environ.get('smsCode', ''),
			'charset': 'utf8', 
			'phoneNumber': remove_hyphen(send_to),
			'message': '{:.70}'.format(message),
		}

		# force to
		force_send_to = os.environ.get('force_send_to', '')
		if len(force_send_to) > 0:
			payload.update({'phoneNumber': remove_hyphen(force_send_to)})

		print(payload)
		try:
			# AosSMSの仕様(URLエンコードでポスト)
			req = urllib.request.Request(
				url=url,
				data=urllib.parse.urlencode(payload).encode('utf-8'),
				method='POST',
				headers={'Content-Type':'application/x-www-form-urlencoded'},
			)
			return urllib.request.urlopen(req).getcode()
		except Exception as e:
			print('Exception:', e.args, file=sys.stderr)
		except:
			print('Unexpected error:', sys.exc_info()[0], file=sys.stderr)

	return -1

# 
def remove_hyphen(to):
    return re.sub(r'^0', '+81', re.sub(r'\D', '', to))
