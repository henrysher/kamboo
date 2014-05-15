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

import time
import logging
from six.moves import range

from kamboo.exceptions import TimeOutException
from kamboo.exceptions import ValidationError

log = logging.getLogger(__name__)


def clean_null_items(obj):
    for key in list(obj.keys()):
        # For "if" statement,
        # Here are some scenarios for the condition to be true:
        #
        # 1. None
        # 2. False
        # 3. zero for numeric types
        # 4. empty sequences
        # 5. empty dictionaries
        # 6. a value of 0 or False returned
        #    when either __len__ or __nonzero__ is called
        #
        # In this fuction, we need to consider these as null items:
        # 1. None; 4. empty sequences; 5. empty dictionaries

        if isinstance(obj[key], bool) or isinstance(obj[key], int):
            continue
        elif not obj[key]:
            del obj[key]
    return obj


def unique_list_of_dict(src_list):
    if not isinstance(src_list, list):
        raise ValidationError("Expect input as 'list'")
    dest_list = []
    for item in src_list:
        if item not in dest_list:
            dest_list.append(item)
    return dest_list


def compare_list_of_dict(src_list, dest_list):
    if not isinstance(src_list, list) or not isinstance(dest_list, list):
        raise ValidationError("Expect inputs as 'list'")

    added_list = []
    removed_list = []
    s_list = unique_list_of_dict(src_list)
    d_list = unique_list_of_dict(dest_list)

    for item in s_list:
        if item not in d_list:
            removed_list.append(item)

    for item in d_list:
        if item not in s_list:
            added_list.append(item)

    result = {"Add": added_list, "Remove": removed_list}
    return result


def wait_to_complete(resource=None, expected_status=None,
                     unit=5, timeout=300):
    """
    Wait the specified resource to complete
    """
    log.info("Wait for the resource '%s' to be '%s'"
             % (resource.id, expected_status))
    for i in range(int(timeout/unit)):
        status = resource.status
        if status == expected_status:
            return resource
        log.info("Current status of the resource '%s': "
                 "still '%s', not the expected '%s'"
                 % (resource, status, expected_status))
        time.sleep(unit)

    if resource.status == expected_status:
        return resource
    else:
        raise TimeOutException(
            "The operation has '%s' timed out "
            "when no expected result '%s' found" % (timeout, expected_status)
            )
