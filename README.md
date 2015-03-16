Recurrence is -- or someday will be -- a multi-platform open source event reminder.  It's about 0.001% completed right now.

# Developer Overview #

## The Goal of the Project ##

To develop a program capable of providing users with the following **required** features:

  * the ability to define recurring events in a flexible fashion with tracking of, at a minimum, an event description, start date, (optional) end date, recurrence descriptors, and a boolean clearance value.
  * time-window driven display of future uncleared events.
  * full display of past uncleared events.

The original utility of these requirements comes by way of using this program as a bill reminder.  Such a reminder is considered inadequate without the ability to define bill payment deadlines with flexible recurrence patterns, to see those deadlines some period in advance of each occurrence, to mark as "cleared" those bills which have been paid, and to annoy the user to death about past unpaid bills.

The following are, for now at least, **non-requirements**:

  * event exceptions (event occurrences which do not follow the recurrence pattern for the event, or skipped occurrences)
  * time granularity with more than year/month/day precision

## Getting It Done ##

### The Basics ###

Recurrence will be written in Python, targeting a minimum Python version of 2.4.  WxWidgets will be used for the UI.  No additional library dependencies are expected.

Requirements:
  * Python 2.5 (or Python 2.4 + the [uuid module](http://zesty.ca/python/uuid.py))
  * [wxPython](http://www.wxpython.org)

### Data Model ###

We will need to refer to both EventDefinition and EventOccurrence objects.  An EventDefinition will need to store the following:

  * event\_def\_id - uniquely identifies this event definition
  * description - a bit of UTF8 text of arbitrary length
  * start\_date - the year/month/day of the event's first occurrence
  * recurrence - none, or contains the following:
    * until\_date - the year/month/day, inclusive, on which the recurrence ends.
    * oftenness - "yearly", "monthly", "weekly"
    * ?

For the purposes of UI interaction and persistence, we'll need to refer to individual occurrences of events, though, or EventOccurrences:

  * event\_def\_id - identifies the event definition associated with this occurrence
  * event\_occ\_id - uniquely identifies this occurrence
  * date - the year/month/day of this event occurrence
  * cleared - boolean clearance flag

### Storage Model ###

Ideally, data should be persisted in a version-controllable, human readable/tweakable fashion.  That means flat files.  The data files should carry format information (about the file syntax format).

What needs to be persisted?

| EventDefinitions | REQUIRED | Storing these means we needn't store uncleared future occurrences.  We can purge any definitions for which all occurrences are in the past and cleared, though. |
|:-----------------|:---------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Past uncleared EventOccurrences | REQUIRED | We must not lose track of late unpaid bills, for example. |
| Future uncleared EventOccurrences | NOT REQUIRED | These can be rebuilt from the definitions. |
| Past cleared EventOccurrences | NOT REQUIRED | Not required, but perhaps some degree of recent clearance history is valuable? |
| Future cleared EventOccurrences | REQUIRED? | These represent a delta from the future event definitions that are uncleared.  But do we need to track all the cleared future items, or can we store for each event definition a "next uncleared" occurrence date? |

## Approach ##

A multi-step approach might make the most sense here:

  1. Develop the event model classes
  1. Develop a storage/retrieval mechanism for data
  1. Develop a command-line interface for querying data
  1. Develop a command-line interface for modifying data
  1. Develop a GUI