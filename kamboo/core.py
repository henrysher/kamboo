
import botocore
from kotocore.session import Session


class KambooConnection(object):
    """
    Kamboo connection with botocore session initialized
    """
    session = botocore.session.get_session()

    def __init__(self, service_name="ec2", region_name="us-east-1",
                 credentials=None):
        self.region = region_name
        self.credentials = credentials
        if self.credentials:
            self.session.set_credentials(**self.credentials)
        Connection = Session(session=self.session).get_connection(service_name)
        self.conn = Connection(region_name=self.region)
