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

log = logging.getLogger(__name__)


class Distee(object):
    """
    Distribute your AWS resource per region and account
    """
    def __init__(self, type=None,
                 source_account_id=None,
                 source_credentials=None,
                 source_region=None,
                 source_id=None,
                 dest_account_id=None,
                 dest_credentials=None,
                 dest_region=None,
                 dest_tags=None):

        self.source_account_id = source_account_id
        self.source_credentials = source_credentials
        self.source_region = source_region
        self.source_id = source_id
        self.dest_account_id = dest_account_id
        self.dest_credentials = dest_credentials
        self.dest_region = dest_region
        self.dest_tags = dest_tags

        module_name = '.'.join(["kamboo", type.lower()])
        resource_name = str(type).title()
        collection_name = ''.join([resource_name, "Collection"])

        module = __import__(module_name, fromlist=[type.lower()])
        self.collection = getattr(module, collection_name)
        self.resource = getattr(module, resource_name)

        self.src_collection = self.collection(region_name=source_region,
                                              account_id=source_account_id,
                                              credentials=source_credentials)

        self.dest_collection = self.collection(region_name=dest_region,
                                               account_id=dest_account_id,
                                               credentials=dest_credentials)

        self.source = self.resource(source_id, collection=self.src_collection)

    def distribute(self, wait=False):
        """
        Distribute the resource
        """

        if self.source_account_id == self.dest_account_id:
            return self.dist_to_same_account(wait=wait)
        else:
            return self.dist_to_different_account(wait=wait)

    def dist_to_same_account(self, collection=None, wait=False):
        """
        Distribute the resource to the same account
        """
        log.info("Distribute the resource '%s'"
                 "to the same account '%s' from '%s' to '%s'" %
                 (self.source_id, self.source_account_id,
                  self.source_region, self.dest_region))

        if collection is None:
            collection = self.dest_collection

        if wait is True:
            new_resource = collection.wait_to_copy_resource(
                self.source_region, self.source_id)
        else:
            new_resource = collection.copy_resource(
                self.source_region, self.source_id)

        log.info("Shifted the resource '%s' "
                 "to the same account '%s' "
                 "under the region '%s' "
                 % (self.source_id, self.source_account_id,
                    self.dest_region))

        if self.dest_tags:
            new_resource.tags = tags
        else:
            new_resource.tags = self.source.tags

        log.info("Attached the tags '%s' to the resource '%s'"
                 % (new_resource.tags, self.source_id))
        return new_resource

    def dist_to_different_account(self, wait=False):
        """
        Distribute the resource to a different account
        """
        log.info("Distribute the resource '%s': "
                 "from the account '%s' to '%s' and "
                 "from the region '%s' to '%s' " %
                 (self.source_id, self.source_account_id, self.dest_account_id,
                  self.source_region, self.dest_region))

        if self.source_region == self.dest_region:
            log.debug("Detected same region for source and destination")
            self.source.add_permission(self.dest_account_id)
            log.info("Shifted the resource '%s' "
                     "to the same account '%s' "
                     "under the region '%s' "
                     % (self.source_id, self.source_account_id,
                        self.dest_region))
            new_resource = self.source
        else:
            collection = self.collection(region_name=self.dest_region,
                                         account_id=self.source_account_id,
                                         credentials=self.source_credentials)

            new_resource = self.dist_to_same_account(
                collection=collection, wait=wait)
            log.info("Shifted the resource '%s' "
                     "to the same account '%s' "
                     "under the region '%s' "
                     % (self.source_id, self.source_account_id,
                        self.dest_region))

            new_resource.add_permission(self.dest_account_id)
            log.info("Shifted the resource '%s' "
                     "to the new account '%s' "
                     % (self.source_id, self.dest_account_id,
                        self.dest_region))

        new_resource = self.resource(new_resource.id,
                                     collection=self.dest_collection)

        if self.dest_tags:
            new_resource.tags = self.dest_tags
        else:
            new_resource.tags = self.source.tags

        log.info("Attached the tags '%s' to the resource '%s'"
                 % (new_resource.tags, self.source_id))

        return new_resource
