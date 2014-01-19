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

log = logging.getLogger(__name__)


class ImageCollection(KambooConnection):
    """
    Represents a collection of EC2 Images
    """
    def __init__(self, service_name, region_name,
                 account_id=None, credentials=None):
        super(ImageCollection, self).__init__(service_name,
                                              region_name,
                                              account_id,
                                              credentials)

    def copy_resource(self, source_region, source_image_id,
                      image_name=None, image_description=None):
        params = {"source_region": source_region,
                  "source_image_id": source_image_id,
                  "name": image_name,
                  "description": image_description}

        r_data = self.conn.copy_image(**clean_null_items(params))

        if "ImageId" not in r_data:
            raise KambooException(
                "Fail to copy the image '%s:%s'" % (source_region,
                                                    source_image_id))
        return Image(r_data["ImageId"], collection=self)

    def get_resource_attribute(self, image_id):
        """
        Fetch the attribute of the specified EC2 Image
        """
        r_data = self.conn.describe_images(image_ids=[image_id])

        if "Images" not in r_data:
            raise KambooException("No such image attribute found")

        if len(r_data["Images"]) > 1:
            raise TooManyRecordsException("More than two images found")

        attr_dict = r_data["Images"][0]
        attr_dict.update(
            {"Permission": self.get_resource_permission(image_id)})
        name = self.__class__.__name__
        keys = [xform_name(key) for key in attr_dict.keys()]

        return namedtuple(name, keys)(*attr_dict.values())

    def get_resource_permission(self, image_id):
        """
        Fetch the permission of the specified EC2 Image
        """
        r_data = self.conn.describe_image_attribute(
            image_id=image_id,
            attribute="launchPermission")

        if "LaunchPermissions" not in r_data:
            raise KambooException("No such image permission found")

        return r_data["LaunchPermissions"]

    def set_resource_permission(self, id, old, new):
        """
        Modify the permission of the specified EC2 Image
        """
        permission_diff = compare_list_of_dict(old, new)
        params = clean_null_items(permission_diff)
        if params:
            self.conn.modify_image_attribute(image_id=id,
                                             launch_permission=params)

    def get_resource_tags(self, image_id):
        """
        Fetch the tags of the specified EC2 Image
        """
        r_data = self.conn.describe_tags(resources=[image_id])

        if "Tags" not in r_data:
            raise KambooException("No such image tags found")

        return r_data["Tags"]

    def set_resource_tags(self, image_id, tags=None):
        """
        Modify the tags of the specified EC2 Image
        """
        r_data = self.conn.create_tags(resources=[image_id], tags=tags)

        if "return" in r_data:
            if r_data["return"] == "true":
                return

        raise KambooException("Fail to add tags to the specified image")


class Image(object):
    """
    Represents an EC2 Image
    """

    def __init__(self, id, attribute=None, collection=None):
        self.id = id
        self.collection = collection
        self.refresh_resource_attribute(id, attribute)

    def __repr__(self):
        return 'Image:%s' % self.id

    @property
    def desc(self):
        return self._desc

    @desc.setter
    def desc(self, value):
        self._desc = self.collection.conn.modify_image_attribute(
            image_id=self.id, description=value)

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

        self.id = attribute.image_id
        self.is_public = attribute.public
        self.name = attribute.name
        self.status = attribute.state
        self.owner = attribute.owner_id
        self.type = attribute.image_type
        self.block_device_mappings = attribute.block_device_mappings
        self.kernel_id = attribute.kernel_id
        self.root_device_name = attribute.root_device_name
        self.root_device_type = attribute.root_device_type

        self._tags = attribute.tags
        self._desc = attribute.description
        self._permission = attribute.permission
