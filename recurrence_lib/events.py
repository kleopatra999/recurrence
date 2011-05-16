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

"""events.py:  Recurrence data model objects."""

import datetime


EVENT_PERIOD_WEEKLY = 'weekly'
EVENT_PERIOD_MONTHLY = 'monthly'
EVENT_PERIOD_YEARLY = 'yearly'


class InvalidEventRecurrencePeriod(Exception): pass
class NotImplementedError(Exception): pass

def period_to_string(s):
  if s == EVENT_PERIOD_YEARLY or \
     s == EVENT_PERIOD_MONTHLY or \
     s == EVENT_PERIOD_WEEKLY:
    return s
  else:
    raise InvalidEventRecurrencePeriod("Unrecognized period value: %s"
                                       % (str(s)))


period_from_string = period_to_string


class EventRecurrence:
  """Describes the recurrence pattern used by an EventDescription object."""
  
  def __init__(self, period=None, until_date=None):
    self.set_period(period)
    self.set_until_date(until_date)

  def set_period(self, period):
    assert period in (None,
                      EVENT_PERIOD_WEEKLY,
                      EVENT_PERIOD_MONTHLY,
                      EVENT_PERIOD_YEARLY)
    self.period = period

  def get_period(self):
    return self.period

  def set_until_date(self, until_date):
    assert until_date is None \
           or type(until_date) == datetime.date
    self.until_date = until_date

  def get_until_date(self):
    return self.until_date

  def __eq__(self, other):
    return self.until_date == other.until_date and \
           self.period == other.period


class EventDefinition:
  """An event definition -- the template, of sorts, from which
  individual event occurrences are created."""
  
  def __init__(self, uuid=None, description=None, start_date=None,
               recurrence=None):
    self.set_uuid(uuid)
    self.set_description(description)
    self.set_start_date(start_date)
    self.set_recurrence(recurrence)

  def set_uuid(self, uuid):
    self.uuid = uuid

  def get_uuid(self):
    return self.uuid

  def set_description(self, description):
    unicode(description, 'utf8')
    self.description = description

  def get_description(self):
    return self.description

  def set_start_date(self, start_date):
    assert type(start_date) == datetime.date
    self.start_date = start_date

  def get_start_date(self):
    return self.start_date

  def set_recurrence(self, recurrence):
    assert recurrence is None or isinstance(recurrence, EventRecurrence)
    self.recurrence = recurrence

  def get_recurrence(self):
    return self.recurrence

  def __eq__(self, other):
    return self.uuid == other.uuid and \
           self.description == other.description and \
           self.start_date == other.start_date and \
           self.recurrence == other.recurrence

  def get_first_occurrence(self):
    return EventOccurrence(self, self.start_date)


class EventOccurrence:
  """A single occurrence of an event."""
  
  def __init__(self, definition=None, date=None, cleared=False):
    self.set_definition(definition)
    self.set_date(date)
    self.set_cleared(cleared)

  def set_definition(self, definition):
    assert definition is None or isinstance(definition, EventDefinition)
    self.definition = definition

  def get_definition(self):
    return self.definition

  def set_date(self, date):
    assert type(date) == datetime.date
    self.date = date

  def get_date(self):
    return self.date

  def set_cleared(self, cleared):
    assert cleared == True or cleared == False
    self.cleared = cleared

  def get_cleared(self):
    return self.cleared

  def __eq__(self, other):
    return self.definition == other.definition and \
           self.date == other.date and \
           self.cleared == other.cleared

  def next(self):
    recurrence = self.definition.get_recurrence()
    if recurrence:
      period = recurrence.get_period()
      until_date = recurrence.get_until_date()
      if period == EVENT_PERIOD_WEEKLY:
        new_date = self.date + datetime.timedelta(7, 0, 0)
      elif period == EVENT_PERIOD_MONTHLY:
        new_month = self.date.month + 1
        new_year = self.date.year
        if new_month == 13:
          new_month = 1
          new_year = new_year + 1
        new_date = datetime.date(new_year,
                                 new_month,
                                 self.date.day)
      elif period == EVENT_PERIOD_YEARLY:
        new_date = datetime.date(self.date.year + 1,
                                 self.date.month,
                                 self.date.day)
      if (not until_date) or (new_date <= until_date):
        return EventOccurrence(self.definition, new_date)
    # no recurrence, or no occurrences before until_date
    return None


def _get_past_occurrences(definitions, occurrences, now_time):
  past_occurrences = []
  for occurrence in occurrences:
    if (not occurrence.get_cleared()) and (occurrence.get_date() < now_time):
      past_occurrences.append(occurrence)
  return past_occurrences


def _get_future_occurrences(definitions, occurrences, now_time, num_days):
  end_time = now_time + datetime.timedelta(num_days, 0, 0)
  future_occurrences = []
  for definition in definitions:
    occ = definition.get_first_occurrence()
    while 1:
      if occ.get_date() >= now_time and occ.get_date() <= end_time:
        future_occ = occ
        for i in range(len(occurrences)):
          if occurrences[i].get_definition() == future_occ.get_definition() \
             and occurrences[i].get_date() == future_occ.get_date() \
             and occurrences[i].get_cleared():
            future_occ = None
        if future_occ:
          future_occurrences.append(future_occ)
      occ = occ.next()
      if occ is None:
        break
      if occ.get_date() > end_time:
        break
  return future_occurrences
