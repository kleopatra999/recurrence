#!/usr/bin/env python
# ====================================================================
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
# ====================================================================

import sys
import os
import random
import shutil
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(sys.argv[0], "../..")))
import recurrence_lib.storage

test_temp_dir = os.path.abspath(os.path.join(sys.argv[0], "../__TMP__"))
test_data_dir = os.path.abspath(os.path.join(sys.argv[0], "../test_data"))

class TestRecurrenceStorage(unittest.TestCase):

  def setUp(self):
    # This is run before each test begins.
    os.mkdir(test_temp_dir)

  def tearDown(self):
    # This is run after each test completes.
    shutil.rmtree(test_temp_dir)

  def _get_data_filename(self, filename):
    return os.path.join(test_data_dir, filename)

  def _get_temp_filename(self, filename):
    return os.path.join(test_temp_dir, filename)
  
  def test_basic_read(self):
    filepath = self._get_data_filename('basic_read')
    definitions, occurrences = \
        recurrence_lib.storage.read_data_file(filepath)

  def test_basic_write(self):
    read_filepath = self._get_data_filename('basic_read')
    definitions, occurrences = \
        recurrence_lib.storage.read_data_file(read_filepath)
    write_filepath = self._get_temp_filename('basic_write')
    recurrence_lib.storage.write_data_file(write_filepath,
                                           definitions, occurrences)
    definitions2, occurrences2 = \
        recurrence_lib.storage.read_data_file(write_filepath)
    self.assertEqual(definitions, definitions2)
    self.assertEqual(occurrences, occurrences2)

if __name__ == '__main__':
  unittest.main()
