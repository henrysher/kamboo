import botocore.session
import os

os.environ['AWS_CONFIG_FILE'] = "/etc/profiles.cfg"

orig_owner = ""
shared_owner = ""

region = "us-west-2"
session = botocore.session.get_session()
session.profile = 'beta'

service = session.get_service('ec2')
op1 = service.get_operation('DescribeRegions')
endpoint = service.get_endpoint(region)
http_response, response_data = op1.call(endpoint)
import json
print json.dumps(response_data, sort_keys=True, indent=4, separators=(',', ': '))

service = session.get_service('ec2')
op1 = service.get_operation('DescribeImages')
endpoint = service.get_endpoint(region)
param = {'filters': [{'Name': "tag:Role", "Values": ["ScannerDy"]}, 
        {'Name': "tag:Version", "Values": ["1051"]}]}
http_response, response_data = op1.call(endpoint, **param)
import json
print json.dumps(response_data, sort_keys=True, indent=4, separators=(',', ': '))
owner_id = response_data['Images'][0]['OwnerId']
if owner_id != orig_owner:
    exit
ami_id = response_data['Images'][0]['ImageId']
tags = response_data['Images'][0]['Tags']

service = session.get_service('ec2')
op1 = service.get_operation('DescribeImageAttribute')
endpoint = service.get_endpoint(region)
param = {'image_id': ami_id, 'attribute': 'launchPermission'}
http_response, response_data = op1.call(endpoint, **param)
import json
print json.dumps(response_data, sort_keys=True, indent=4, separators=(',', ': '))

service = session.get_service('ec2')
op1 = service.get_operation('ModifyImageAttribute')
endpoint = service.get_endpoint(region)
permission = { "Add": [ { "UserId": shared_owner } ] }
param = {'image_id': ami_id, 'launch_permission': permission} 
http_response, response_data = op1.call(endpoint, **param)
import json
print json.dumps(response_data, sort_keys=True, indent=4, separators=(',', ': '))

print '-'*10, 'switched'

region = "us-west-2"
session = botocore.session.get_session()
session.profile = 'qa'

service = session.get_service('ec2')
op1 = service.get_operation('CreateTags')
endpoint = service.get_endpoint(region)
param = {'resources': [ami_id], 'tags': tags} 
http_response, response_data = op1.call(endpoint, **param)
import json
print json.dumps(response_data, sort_keys=True, indent=4, separators=(',', ': '))

service = session.get_service('ec2')
op1 = service.get_operation('DescribeImages')
endpoint = service.get_endpoint(region)
param = {'filters': [{'Name': "tag:Role", "Values": ["ScannerDy"]},
        {'Name': "tag:Version", "Values": ["1051"]}]}
http_response, response_data = op1.call(endpoint, **param)
import json
print json.dumps(response_data, sort_keys=True, indent=4, separators=(',', ': '))

