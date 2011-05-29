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

"""recurrence_ui:  Recurrence wxWidgets-based GUI application components."""

### NOTE: Many of these classes are subclasses of standard wx
### controls, employing two-stage creation so they can be instantiated
### via the XRC subsystem.  See http://wiki.wxpython.org/TwoStageCreation
### for details of this approach.

import sys
import os
try:
  import recurrence_lib
except ImportError: 
  sys.path.insert(0, os.path.join(os.path.dirname(sys.argv[0]), ".."))
  import recurrence_lib
import datetime
import wx
import wx.xrc


def get_resources():
  """Return the wx.xrc.XmlResource object contain resources for this
  program."""
  try:
    RESOURCES_XRC = os.path.join(os.path.dirname(__file__), 'resources.xrc')
  except:
    RESOURCES_XRC = 'resources.xrc'
  return wx.xrc.XmlResource(RESOURCES_XRC)
    

def _cmp_occurrence_by_date(a, b):
  """Sorting function for EventOccurrence objects, by date, then by
  description."""
  if a.get_date() < b.get_date():
    return -1
  if a.get_date() > b.get_date():
    return 1
  return cmp(a.get_definition().get_description(),
             b.get_definition().get_description())


class RecurrenceEventListCtrl(wx.ListCtrl):
  """Subclass wxListCtrl widget responsible for displaying and
  interacting with Recurrence events."""
  
  def __init__(self):
    pre = wx.PreListCtrl()
    self.PostCreate(pre)
    self.Bind(wx.EVT_WINDOW_CREATE, self.OnCreate)

  def OnCreate(self, event):
    """Event handler for window creation event."""

    # No need to listen for window creation events now.
    self.Unbind(wx.EVT_WINDOW_CREATE)

    # Let's get some columns in place, shall we?
    self.InsertColumn(0, "Date")
    self.InsertColumn(1, "Description")
    self.InsertColumn(2, "Recurrence")

  def RegisterDatafile(self, datafile):
    """Register DATAFILE with the application as the source of event
    information. """
    self.definitions, self.occurrences = \
        recurrence_lib.storage.read_data_file(datafile)
    self.RefreshEventList()

  def RefreshEventList(self):
    """Refresh the event listing, in full."""
    self.DeleteAllItems()
    occs = recurrence_lib.events._get_past_occurrences(self.definitions,
                                                       self.occurrences,
                                                       datetime.date.today())
    occs.sort(_cmp_occurrence_by_date)
    for occ in occs:
      self._AppendEventToList(occ, True)
    occs = recurrence_lib.events._get_future_occurrences(self.definitions,
                                                         self.occurrences,
                                                         datetime.date.today(),
                                                         30)
    occs.sort(_cmp_occurrence_by_date)
    for occ in occs:
      self._AppendEventToList(occ, False)
    self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
    self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
    self.SetColumnWidth(2, wx.LIST_AUTOSIZE)

  def _AppendEventToList(self, occurrence, past=False):
    """Append EventOccurrence OCCURRENCE to the end of the list."""

    def unparse_date(date):
      if date is None:
        return ''
      else:
        return "%d-%02d-%02d" % (date.year, date.month, date.day)
    
    datestr = unparse_date(occurrence.get_date())
    desc = occurrence.get_definition().get_description()
    rec = occurrence.get_definition().get_recurrence()
    if rec:
      rec = recurrence_lib.events.period_to_string(rec.get_period())
    else:
      rec = ""
    idx = self.InsertStringItem(self.GetItemCount(), datestr)
    self.SetStringItem(idx, 1, desc)
    self.SetStringItem(idx, 2, rec)
    self.SetItemTextColour(idx, wx.Colour(past and 255 or 0, 0, 0))


class RecurrenceTaskBarIcon(wx.TaskBarIcon):
  """Recurrence taskbar icon manager."""

  def __init__(self, popup_menu):
    wx.TaskBarIcon.__init__(self)
    self.alert = False
    self.popup_menu = popup_menu
    self._UpdateIcon()

  def CreatePopupMenu(self):
    """Called when the user invokes the popup menu (that is,
    right-clicks on the taskbar icon)."""
    self.PopupMenu(self.popup_menu)
    
  def _SetAlert(self, alert=True):
    """Ensure that the local alert state is set to ALERT, updating the
    icon if necessary."""
    if bool(alert) != self.alert:
      self.alert = bool(alert)
      self._UpdateIcon()

  def _GetAlert(self):
    """Return the local alert state."""
    return self.alert
      
  def _UpdateIcon(self):
    """Update the icon bitmap based on the current alert state."""
    if self.alert:
      self.SetIcon(wx.Icon("tbicon-alert.xpm", wx.BITMAP_TYPE_XPM))
    else:
      self.SetIcon(wx.Icon("tbicon-normal.xpm", wx.BITMAP_TYPE_XPM))
   

class RecurrenceMainFrame(wx.Frame):
  """Recurrence primary task-bar frame."""

  def __init__(self):
    pre = wx.PreFrame()
    self.PostCreate(pre)
    self.Bind(wx.EVT_WINDOW_CREATE, self.OnCreate)

  def OnCreate(self, event):
    """Event handler for window creation event."""
    
    # No need to listen for window creation events now.
    self.Unbind(wx.EVT_WINDOW_CREATE)

    # We need the XML resources.
    self.resources = get_resources()
   
    # Create the taskbar popup window, and register event handlers.
    self.popup = self.resources.LoadMenu('TaskBarPopupMenu')
    wx.EVT_MENU(self.popup,
                self.resources.GetXRCID('TaskBarMenuItemToggle'),
                self._TaskBarMenuItemToggleSelected)
    wx.EVT_MENU(self.popup,
                self.resources.GetXRCID('TaskBarMenuItemExit'),
                self._TaskBarMenuItemExitSelected)

    # Instantiate the taskbar icon, and register event handlers.
    self.tbicon = RecurrenceTaskBarIcon(self.popup)
    wx.EVT_TASKBAR_LEFT_DOWN(self.tbicon, self._TaskBarLeftClick)

    # Register frame-specific event handers.
    wx.EVT_CLOSE(self, self._FrameClosed)
    wx.EVT_ICONIZE(self, self._FrameIconized)

  def RegisterDatafile(self, datafile):
    entrylist = self.FindWindowByName('EventList')
    try:
      entrylist.RegisterDatafile(datafile)
    except Exception, e:
      dlg = wx.MessageDialog(self,
                             "Error reading data file '%s': %s"
                             % (datafile, str(e)),
                             "Data File Error",
                             wx.OK | wx.ICON_ERROR)
      dlg.ShowModal()
      self.Close()

  def Close(self):
    """Overrides wx.Frame.Close() to ensure that we remove the icon
    installed by the RecurrenceTaskBarIcon() object."""
    self.tbicon.RemoveIcon()
    self.Destroy()

  def _FrameClosed(self, event):
    """Event hander for handling the frame closure event.  We call our
    customized Close() function."""
    self.Close()
    return True

  def _FrameIconized(self, event):
    self.Show(not event.Iconized())
    return True
  
  def _TaskBarLeftClick(self, event):
    """Event handler for a left-click on the taskbar icon.  If the
    frame is iconized(), restore and show it().  Otherwise, iconize
    and hide."""
    if self.IsIconized():
      self.Show(True)
      self.Iconize(False)
    else:
      self.Iconize(True)
      self.Show(False)
    return True

  def _TaskBarMenuItemToggleSelected(self, event):
    """Event handler for selection of the TaskBarMenu's 'Toggle...'
    item.  Toggles the icon alertness state."""
    self.tbicon._SetAlert(not self.tbicon._GetAlert())
    return True

  def _TaskBarMenuItemExitSelected(self, event):
    """Event handler for selection of the TaskBarMenu's 'Exit...'
    item.  Closes down this frame."""
    self.Close()
    return True
