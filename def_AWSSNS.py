import boto3

# need role: sns:Publish
def sns(message):
	region_name = os.environ.get('region_name', 'ap-northeast-1')
	TopicArn = os.environ.get('TopicArn', '')
	if len(TopicArn)>0:
		try:
			client = boto3.client('sns', region_name=region_name)
			client.publish(
				TopicArn=TopicArn,
				Message=message,
				Subject='alarm',
			)
			return 0
		except Exception as e:
			print('Exception:', e.args, file=sys.stderr)
		except:
			print('Unexpected error:', sys.exc_info()[0], file=sys.stderr)
