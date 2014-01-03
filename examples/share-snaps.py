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
op1 = service.get_operation('DescribeSnapshots')
endpoint = service.get_endpoint(region)
param = {'filters': [{'Name': "tag:Timestamp", "Values": ["0"]}]}
http_response, response_data = op1.call(endpoint, **param)
import json
print json.dumps(response_data, sort_keys=True, indent=4, separators=(',', ': '))
snap_id = response_data['Snapshots'][0]['SnapshotId']
tags = response_data['Snapshots'][0]['Tags']

service = session.get_service('ec2')
op1 = service.get_operation('DescribeSnapshotAttribute')
endpoint = service.get_endpoint(region)
param = {'snapshot_id': snap_id, 'attribute': 'createVolumePermission'}
http_response, response_data = op1.call(endpoint, **param)
import json
print json.dumps(response_data, sort_keys=True, indent=4, separators=(',', ': '))

service = session.get_service('ec2')
op1 = service.get_operation('ModifySnapshotAttribute')
endpoint = service.get_endpoint(region)
permission = { "Add": [ { "UserId": shared_owner } ] }
param = {'snapshot_id': snap_id, 'create_volume_permission': permission} 
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
param = {'resources': [snap_id], 'tags': tags} 
http_response, response_data = op1.call(endpoint, **param)
import json
print json.dumps(response_data, sort_keys=True, indent=4, separators=(',', ': '))

service = session.get_service('ec2')
op1 = service.get_operation('DescribeSnapshots')
endpoint = service.get_endpoint(region)
param = {'filters': [{'Name': "tag:Timestamp", "Values": ["0"]}]}
http_response, response_data = op1.call(endpoint, **param)
import json
print json.dumps(response_data, sort_keys=True, indent=4, separators=(',', ': '))

