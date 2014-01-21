
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


class KambooException(Exception):
    """
    A base exception class for all Kamboo-related exceptions.
    """
    pass


class ValidationError(KambooException):
    pass


class TimeOutException(KambooException):
    pass


class TooManyRecordsException(KambooException):
    """
    Exception raised when a search of records returns more
    records than requested.
    """
    pass
