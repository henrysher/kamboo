from collections import namedtuple
from botocore import xform_name
from core import KambooConnection
from utils import compare_list_of_dict, drop_null_items


class ImageCollection(KambooConnection):
    """
    """
    def __init__(self, service_name, region_name,
                 account_id=None, credentials=None):
        super(ImageCollection, self).__init__(service_name,
                                              region_name,
                                              account_id,
                                              credentials)

    def get_resource_attribute(self, image_id):
        try:
            return_data = self.conn.describe_images(image_ids=[image_id])
        except Exception, e:
            pass
        attr_dict = return_data["Images"][0]
        attr_dict.update(
            {"Permission": self.get_resource_permission(image_id)})
        name = self.__class__.__name__
        keys = [xform_name(key) for key in attr_dict.keys()]

        return namedtuple(name, keys)(*attr_dict.values())

    def get_resource_permission(self, image_id):
        try:
            return_data = self.conn.describe_image_attribute(
                image_id=image_id, attribute="launchPermission")
        except Exception, e:
            pass
        return return_data["LaunchPermissions"]

    def set_resource_permission(self, id, old, new):
        params = drop_null_items(compare_list_of_dict(old, new))
        if not params:
            return
        try:
            response_data = self.conn.modify_image_attribute(
                image_id=id, launch_permission=params)
        except Exception, e:
            raise


class Image(object):
    """
    """

    def __init__(self, id, attribute=None, collection=None):
        if not any([attribute, collection]):
            raise
        self.id = id
        self.collection = collection
        self.refresh_resource_attribute(id, attribute)

    def __repr__(self):
        return ""

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
        self.collection.conn.create_tags(resources=[self.id], tags=value)
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
