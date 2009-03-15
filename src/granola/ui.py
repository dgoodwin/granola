#   Granola - GPS Enabled Open Source Workout/Adventure Log
#
#   Copyright (C) 2009 Devan Goodwin <dgoodwin@dangerouslyinc.com>
#
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
#   02110-1301  USA

""" Granola's Graphical User Interface """

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import gobject
import os
import sys

from granola.log import log
from granola.model import *
from granola import write_config

RUNNING = "Running"
BIKING = "Biking"

def find_file_on_path(pathname):
    """
    Scan the Python path and locate a file with the given name.

    See:
      http://www.linuxjournal.com/xstatic/articles/lj/0087/4702/4702l2.html
    """

    if os.path.isabs(pathname):
        return pathname
    for dirname in sys.path:
        candidate = os.path.join(dirname, pathname)
        if os.path.isfile(candidate):
            return candidate
    raise Exception("Could not find %s on the Python path."
        % pathname)

class GranolaMainWindow(object):
    """
    Main Granola GTK UI Window
    """

    def __init__(self, config):
        log.debug("Starting GTK UI.")
        self.config = config

        glade_file = 'granola/glade/mainwindow.glade'
        self.glade_xml = gtk.glade.XML(find_file_on_path(glade_file))
        main_window = self.glade_xml.get_widget('main_window')
        self.activity_popup_menu = self.glade_xml.get_widget(
                'activity_popup_menu')

        signals = {
            'on_quit_menu_item_activate': self.shutdown,
            'on_main_window_destroy': self.shutdown,
            'on_prefs_menu_item_activate': self.open_prefs_dialog,
            'on_runs_treeview_button_press_event': 
                self.on_runs_treeview_button_press_event,
        }
        self.glade_xml.signal_autoconnect(signals)

        self.session = Session()
        self.running = self.session.query(Sport).filter(
                Sport.name == RUNNING).one()
        self.biking = self.session.query(Sport).filter(
                Sport.name == BIKING).one()

        self._populate_tabs()

        main_window.show_all()

    def main(self):
        """ Launch the GTK main loop. """
        gtk.main()

    def shutdown(self, widget):
        """ Closes the application. """
        gtk.main_quit()

    def open_prefs_dialog(self, widget):
        prefs_dialog = PreferencesDialog(self.config)

    def _populate_tabs(self):
        # Populate the runs
        runs_liststore = self._build_runs_liststore()
        runs_treeview = self.glade_xml.get_widget("runs_treeview")
        runs_treeview.set_model(runs_liststore)
        self._populate_activity_treeview(runs_treeview)

        rides_liststore = self._build_rides_liststore()
        runs_treeview = self.glade_xml.get_widget("rides_treeview")
        runs_treeview.set_model(rides_liststore)
        self._populate_activity_treeview(runs_treeview)

    def _populate_activity_treeview(self, runs_treeview):
        """ Populate lists on the running tab. """

        # Create columns:
        date_column = gtk.TreeViewColumn("Date")
        route_column = gtk.TreeViewColumn("Route")
        distance_column = gtk.TreeViewColumn("Distance (km)")
        time_column = gtk.TreeViewColumn("Time")
        avg_speed_column = gtk.TreeViewColumn("Speed (km/hr)")

        runs_treeview.append_column(date_column)
        runs_treeview.append_column(route_column)
        runs_treeview.append_column(distance_column)
        runs_treeview.append_column(time_column)
        runs_treeview.append_column(avg_speed_column)

        cell = gtk.CellRendererText()

        date_column.pack_start(cell, expand=False)
        route_column.pack_start(cell, expand=False)
        distance_column.pack_start(cell, expand=False)
        time_column.pack_start(cell, expand=False)
        avg_speed_column.pack_start(cell, expand=False)

        date_column.set_attributes(cell, text=0)
        route_column.set_attributes(cell, text=1)
        distance_column.set_attributes(cell, text=2)
        time_column.set_attributes(cell, text=3)
        avg_speed_column.set_attributes(cell, text=4)

    def _build_runs_liststore(self):
        """ Return a ListStore with data for all runs. """
        list_store = gtk.ListStore(
                str, # date
                str, # route
                str, # distance
                str, #time
                str, # avg speed
                #float, # avg heart rate
        )
        q = self.session.query(Activity).filter(Activity.sport == 
                self.running).order_by(Activity.start_time.desc())
        for run in q.all():
            duration_seconds = run.duration
            hours = duration_seconds / 3600
            minutes = (duration_seconds / 60) % 60
            seconds = duration_seconds % 60

            list_store.append([
                run.start_time, 
                "N/A", 
                "%.2f" % (run.distance / 1000),
                "%02i:%02i:%02i" % (hours, minutes, seconds),                
                "%.2f" % ((run.distance / 1000) / (duration_seconds / 3600))
            ])

        return list_store

    def _build_rides_liststore(self):
        """ Return a ListStore with data for all rides. """
        list_store = gtk.ListStore(
                str, # date
                str, # route
                str, # distance
                str, #time
                str, # avg speed
                #float, # avg heart rate
        )
        q = self.session.query(Activity).filter(Activity.sport == 
                self.biking).order_by(Activity.start_time.desc())
        for run in q.all():
            duration_seconds = run.duration
            hours = duration_seconds / 3600
            minutes = (duration_seconds / 60) % 60
            seconds = duration_seconds % 60

            list_store.append([
                run.start_time, 
                "N/A", 
                "%.2f" % (run.distance / 1000),
                "%02i:%02i:%02i" % (hours, minutes, seconds),                
                "%.2f" % ((run.distance / 1000) / (duration_seconds / 3600))
            ])

        return list_store

    def on_runs_treeview_button_press_event(self, treeview, event):

        # Handle both left and right mouse button clicks:
        if event.button == 3 or event.button == 1:
            x = int(event.x)
            y = int(event.y)
            time = event.time

            # Select the row:
            pthinfo = treeview.get_path_at_pos(x, y)
            if pthinfo is not None:
                path, col, cellx, celly = pthinfo
                # path[0] appears to be the row here:
                treeview.grab_focus()
                treeview.set_cursor(path, col, 0)

            # Now handle only left clicks:
            if event.button == 3:
                log.debug("x = %s" % x)
                log.debug("y = %s" % y)
                log.debug("time = %s" % time)
                log.debug(pthinfo)

                treeselection = treeview.get_selection()
                # Connect signals to menu items:
                delete = self.glade_xml.get_widget('activity_popup_delete')
                delete.connect_object("activate", 
                        self.activity_popup_menu_delete, treeselection)
                self.activity_popup_menu.popup(None, None, None, 
                        event.button, time)

    def activity_popup_menu_delete(self, treeselection):
        """ 
        Callback for when user clicks "Delete" after right clicking an
        activity. 
        """
        (model, iter) = treeselection.get_selected()
        log.debug("Deleting! %s" % model.get_value(iter,0))



class PreferencesDialog(object):

    def __init__(self, config):
        log.debug("Opening Preferences dialog.")
        self.config = config

        glade_file = 'granola/glade/prefs-dialog.glade'
        self.glade_xml = gtk.glade.XML(find_file_on_path(glade_file))
        self.preferences_dialog = self.glade_xml.get_widget("prefs_dialog")

        signals = {
            'on_apply_button_clicked': self.apply_prefs,
            'on_cancel_button_clicked': self.cancel,
        }
        self.glade_xml.signal_autoconnect(signals)
        self.import_folder_chooser = self.glade_xml.get_widget(
                "import_folder_filechooserbutton")
        self.import_folder_chooser.set_filename(
                self.config.get("import", "import_folder"))

        self.preferences_dialog.show_all()

    def apply_prefs(self, widget):
        """ 
        Callback when apply button is pressed. Write settings to disk and close
        the window.
        """
        log.debug("Applying preferences.")
        import_folder = self.import_folder_chooser.get_filename()
        log.debug("   import_folder = %s" % import_folder)
        self.config.set("import", "import_folder", import_folder)
        write_config(self.config)
        self.preferences_dialog.destroy()

    def cancel(self, widget):
        """
        Don't apply any settings and close the window.
        """
        log.debug("Cancel button pressed, closing preferences dialog.")
        self.preferences_dialog.destroy()

