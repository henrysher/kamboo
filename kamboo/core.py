# Copyright (c) 2014, Henry Huang
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import botocore
from kotocore.session import Session

log = logging.getLogger(__name__)


class KambooConnection(object):
    """
    Kamboo connection with botocore session initialized
    """

    def __init__(self, service_name="ec2", region_name="us-east-1",
                 account_id=None,
                 credentials=None):
        self.session = botocore.session.get_session()
        self.service = service_name
        self.region = region_name
        self.account_id = account_id
        self.credentials = credentials
        if self.credentials:
            self.session.set_credentials(**self.credentials)
        Connection = Session(session=self.session).get_connection(service_name)
        self.conn = Connection(region_name=self.region)
        log.debug("KambooConnection: [%s, %s, %s]" % (self.account_id,
                                                      self.region,
                                                      self.service))

    def __repr__(self):
        return "KambooConnection: [%s, %s, %s]" % (self.account_id,
                                                   self.region,
                                                   self.service)
