import os
import boto3
import botocore
from boto3.core.session import Session

os.environ['AWS_CONFIG_FILE'] = "/etc/profiles.cfg"

orig_owner = ""
shared_owner = ""

region = "us-west-2"
session = botocore.session.get_session()
session.profile = 'beta'

session = Session(session=session)
ec2_conn = session.connect_to('ec2', region_name=region)
response_data = ec2_conn.describe_images(
    filters=[{'Name': "tag:Role", "Values": ["ScannerDy"]},
             {'Name': "tag:Version", "Values": ["1051"]}])
import json
print json.dumps(response_data, sort_keys=True, indent=4, separators=(',', ': '))
owner_id = response_data['Images'][0]['OwnerId']
if owner_id != orig_owner:
    exit
ami_id = response_data['Images'][0]['ImageId']
tags = response_data['Images'][0]['Tags']

response_data = ec2_conn.describe_image_attribute(
    image_id=ami_id, attribute='launchPermission')
import json
print json.dumps(response_data, sort_keys=True, indent=4, separators=(',', ': '))

permission = {"Add": [{"UserId": shared_owner}]}
response_data = ec2_conn.modify_image_attribute(
    image_id=ami_id, launch_permission=permission)
import json
print json.dumps(response_data, sort_keys=True, indent=4, separators=(',', ': '))

print '-' * 10, 'switched'

session = botocore.session.get_session()
session.profile = 'qa'

session = Session(session=session)
ec2_conn = session.connect_to('ec2', region_name=region)
reponse_data = ec2_conn.create_tags(resources=[ami_id], tags=tags)
import json
print json.dumps(response_data, sort_keys=True, indent=4, separators=(',', ': '))

response_data = ec2_conn.describe_images(
    filters=[{'Name': "tag:Role", "Values": ["ScannerDy"]},
             {'Name': "tag:Version", "Values": ["1051"]}])
import json
print json.dumps(response_data, sort_keys=True, indent=4, separators=(',', ': '))
