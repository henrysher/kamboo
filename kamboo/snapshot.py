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
from collections import namedtuple
from botocore import xform_name

from kamboo.core import KambooConnection
from kamboo.exceptions import KambooException, TooManyRecordsException
from kamboo.utils import compare_list_of_dict, clean_null_items
from kamboo.utils import wait_to_complete

log = logging.getLogger(__name__)


class SnapshotCollection(KambooConnection):
    """
    Represents a collection of EC2 Snapshots
    """
    def __init__(self, service_name="ec2", region_name=None,
                 account_id=None, credentials=None):
        super(SnapshotCollection, self).__init__(service_name,
                                                 region_name,
                                                 account_id,
                                                 credentials)

    def copy_resource(self, source_region, source_id,
                      description=None):
        params = {"source_region": source_region,
                  "source_snapshot_id": source_id,
                  "description": description}

        r_data = self.conn.copy_snapshot(**clean_null_items(params))

        if "SnapshotId" not in r_data:
            raise KambooException(
                "Fail to copy the Snapshot '%s:%s'" % (source_region,
                                                       source_id))

        return Snapshot(r_data["SnapshotId"], collection=self)

    def wait_to_copy_resource(self, source_region, source_id,
                              description=None):
        snapshot = self.copy_resource(source_region=source_region,
                                      source_id=source_id,
                                      description=description)
        return wait_to_complete(resource=snapshot, expected_status="available")

    def get_resource_attribute(self, snapshot_id):
        """
        Fetch the attribute of the specified EC2 Snapshot
        """
        r_data = self.conn.describe_snapshots(snapshot_ids=[snapshot_id])

        if "Snapshots" not in r_data:
            raise KambooException("No such Snapshot attribute found")

        if len(r_data["Snapshots"]) > 1:
            raise TooManyRecordsException("More than two Snapshots found")

        attr_dict = r_data["Snapshots"][0]
        try:
            attr_dict.update(
                {"Permission": self.get_resource_permission(snapshot_id)})
        except Exception as e:
            pass

        name = ''.join([self.__class__.__name__, "Attribute"])
        keys = [xform_name(key) for key in attr_dict.keys()]

        return namedtuple(name, keys)(*attr_dict.values())

    def get_resource_permission(self, snapshot_id):
        """
        Fetch the permission of the specified EC2 Snapshot
        """
        r_data = self.conn.describe_snapshot_attribute(
            snapshot_id=snapshot_id,
            attribute="createVolumePermission")

        if "createVolumePermissions" not in r_data:
            raise KambooException("No such Snapshot permission found")

        return r_data["createVolumePermissions"]

    def set_resource_permission(self, id, old, new):
        """
        Modify the permission of the specified EC2 Snapshot
        """
        permission_diff = compare_list_of_dict(old, new)
        params = clean_null_items(permission_diff)
        if params:
            self.conn.modify_snapshot_attribute(
                snapshot_id=id,
                create_volume_permission=params)

    def get_resource_tags(self, snapshot_id):
        """
        Fetch the tags of the specified EC2 Snapshot
        """
        r_data = self.conn.describe_tags(resources=[snapshot_id])

        if "Tags" not in r_data:
            raise KambooException("No such Snapshot tags found")

        return r_data["Tags"]

    def set_resource_tags(self, snapshot_id, tags=None):
        """
        Modify the tags of the specified EC2 Snapshot
        """
        r_data = self.conn.create_tags(resources=[snapshot_id], tags=tags)

        if "return" in r_data:
            if r_data["return"] == "true":
                return

        raise KambooException("Fail to add tags to the specified Snapshot")

    def delete_resource(self, snapshot_id):
        """
        Delete the specified EC2 Snapshot
        """
        r_data = self.collection.conn.delete_snapshot(snapshot_id=id)
        if "return" in r_data:
            if r_data["return"] == "true":
                return

        raise KambooException("Fail to delete the specified Snapshot")


class Snapshot(object):
    """
    Represents an EC2 Snapshot
    """

    def __init__(self, id, attribute=None, collection=None):
        self.id = id
        self.collection = collection
        self.refresh_resource_attribute(id, attribute)

    def __repr__(self):
        return 'Snapshot:%s' % self.id

    @property
    def desc(self):
        return self._desc

    @desc.setter
    def desc(self, value):
        self._desc = self.collection.conn.modify_snapshot_attribute(
            snapshot_id=self.id, description=value)

    @property
    def status(self):
        self.refresh_resource_attribute()
        return self.state

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, value):
        self.collection.set_resource_tags(self.id, tags=value)
        self._tags = value

    @property
    def permission(self):
        return self._permission

    @permission.setter
    def permission(self, value):
        self.collection.set_resource_permission(
            self.id, self._permission, value)
        self._permission = value

    def refresh_resource_attribute(self, id=None, attribute=None):
        if id is None:
            id = self.id
        if not attribute:
            attribute = self.collection.get_resource_attribute(id)
        self.__dict__.update(attribute._asdict())

        self.id = self.snapshot_id
        self._tags = getattr(attribute, "tags", [])
        self._desc = getattr(attribute, "description", "")
        self._permission = getattr(attribute, "permission", [])

    def add_permission(self, account_id):
        new_permission = []
        new_permission.extend(self.permission)
        new_permission.append({"UserId": account_id})
        self.permission = new_permission

    def delete(self, id=None):
        if id is None:
            id = self.id
        self.collection.delete_resource(id)
