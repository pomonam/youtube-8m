# Copyright 2018 Juhan, Ruijian All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Contains the base class for modules."""


class BaseModule(object):
    """Inherit from this class when implementing new modules."""
    pass

    # @property
    # def state_size(self):
    #     raise NotImplementedError()
    #
    # @property
    # def output_size(self):
    #     raise NotImplementedError()

    def __call__(self, inputs, state, scope=None):
        raise NotImplementedError()
