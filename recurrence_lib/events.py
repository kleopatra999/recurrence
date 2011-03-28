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

"""events.py:  Recurrence data model object."""


EVENT_PERIOD_WEEKLY = 'weekly'
EVENT_PERIOD_MONTHLY = 'monthly'
EVENT_PERIOD_YEARLY = 'yearly'


class EventRecurrence:
  """Describes the recurrence pattern used by an EventDescription object."""
  
  def __init__(self):
    self.until_date = None
    self.period = None

  def set_period(self, period):
    assert period in (EVENT_PERIOD_WEEKLY,
                      EVENT_PERIOD_MONTHLY,
                      EVENT_PERIOD_YEARLY)
    self.period = period

  def get_period(self):
    return self.period

  def set_until_date(self, until_date):
    self.until_date = date

  def get_until_date(self):
    return self.until_date


class EventDefinition:
  """An event definition -- the template, of sorts, from which
  individual event occurrences are created."""
  
  def __init__(self):
    self.uuid = None
    self.description = None
    self.start_date = None
    self.recurrence = None

  def set_uuid(self, uuid):
    self.uuid = uuid

  def get_id(self):
    return self.uuid

  def set_description(self, description):
    unicode(description, 'utf8')
    self.description = description

  def get_description(self):
    return self.description

  def set_start_date(self, start_date):
    self.start_date = start_date

  def get_start_date(self):
    return self.start_date

  def set_recurrence(self, recurrence):
    assert recurrence is None or isinstance(recurrence, EventRecurrence)
    self.recurrence = recurrence

  def get_recurrence(self):
    return self.recurrence


class EventOccurrence:
  """A single occurrence of an event."""
  
  def __init__(self):
    self.definition = None
    self.date = None
    self.cleared = None

  def set_definition(self, definition):
    assert definition is None or isinstance(recurrence, EventDefinition)
    self.definition = definition

  def get_definition(self):
    return self.definition

  def set_date(self, date):
    self.date = date

  def get_date(self):
    return self.date

  def set_cleared(self, cleared):
    assert cleared is None or type(cleared) == type(True)
    self.cleared = cleared

  def get_cleared(self):
    return self.cleared
