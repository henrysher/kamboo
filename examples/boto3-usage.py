from boto3.core.session import Session
from boto3.core.introspection import Introspection

session = Session()

# API Call for the service
ec2_conn = session.connect_to('ec2', region_name='us-west-2')
print ec2_conn.describe_regions()
print ec2_conn.describe_instances()

# Operation Data for the service
intro = Introspection(session.core_session)
print intro.introspect_service('sqs')
