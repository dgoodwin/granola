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

        # References to various widgets used throughout the class:
        self.activity_popup_menu = self.glade_xml.get_widget(
                'activity_popup_menu')
        self.running_tv = self.glade_xml.get_widget('runs_treeview')
        self.cycling_tv = self.glade_xml.get_widget('rides_treeview')
        
        # Kinda hacky, used to refer to current treeview so we can re-use
        # the menu code between all activity types.
        self.active_tv = None

        signals = {
            'on_quit_menu_item_activate': self.shutdown,
            'on_main_window_destroy': self.shutdown,
            'on_prefs_menu_item_activate': self.open_prefs_dialog,
            'on_runs_treeview_button_press_event': 
                self.activity_tv_mouse_button_cb,
            'on_rides_treeview_button_press_event': 
                self.activity_tv_mouse_button_cb,
            'on_activity_popup_delete_activate': 
                self.activity_delete_cb,
        }
        self.glade_xml.signal_autoconnect(signals)

        self.session = Session()
        self.running = self.session.query(Sport).filter(
                Sport.name == RUNNING).one()
        self.biking = self.session.query(Sport).filter(
                Sport.name == BIKING).one()

        self.populate_tabs()

        main_window.show_all()

    def main(self):
        """ Launch the GTK main loop. """
        gtk.main()

    def shutdown(self, widget):
        """ Closes the application. """
        gtk.main_quit()

    def open_prefs_dialog(self, widget):
        prefs_dialog = PreferencesDialog(self.config)

    def populate_tabs(self):
        # Populate the runs
        running_liststore = self.build_activity_liststore(self.running)
        self.running_tv.set_model(running_liststore)
        self.populate_activity_treeview(self.running_tv)

        cycling_liststore = self.build_activity_liststore(self.biking)
        self.cycling_tv.set_model(cycling_liststore)
        self.populate_activity_treeview(self.cycling_tv)

    def populate_activity_treeview(self, tv):
        """ Populate activity lists into the given treeview. """

        # Create columns:
        date_column = gtk.TreeViewColumn("Date")
        route_column = gtk.TreeViewColumn("Route")
        distance_column = gtk.TreeViewColumn("Distance (km)")
        time_column = gtk.TreeViewColumn("Time")
        avg_speed_column = gtk.TreeViewColumn("Speed (km/hr)")

        tv.append_column(date_column)
        tv.append_column(route_column)
        tv.append_column(distance_column)
        tv.append_column(time_column)
        tv.append_column(avg_speed_column)

        cell = gtk.CellRendererText()

        date_column.pack_start(cell, expand=False)
        route_column.pack_start(cell, expand=False)
        distance_column.pack_start(cell, expand=False)
        time_column.pack_start(cell, expand=False)
        avg_speed_column.pack_start(cell, expand=False)

        date_column.set_attributes(cell, text=1)
        route_column.set_attributes(cell, text=2)
        distance_column.set_attributes(cell, text=3)
        time_column.set_attributes(cell, text=4)
        avg_speed_column.set_attributes(cell, text=5)

    def build_activity_liststore(self, sport):
        """ 
        Return a ListStore with data for all activities of the given sport. 
        """
        list_store = gtk.ListStore(
                int, # id
                str, # date
                str, # route
                str, # distance
                str, #time
                str, # avg speed
                #float, # avg heart rate
        )
        q = self.session.query(Activity).filter(Activity.sport == 
                sport).order_by(Activity.start_time.desc())
        for run in q.all():
            duration_seconds = run.duration
            hours = duration_seconds / 3600
            minutes = (duration_seconds / 60) % 60
            seconds = duration_seconds % 60

            list_store.append([
                run.id,
                run.start_time, 
                "N/A", 
                "%.2f" % (run.distance / 1000),
                "%02i:%02i:%02i" % (hours, minutes, seconds),                
                "%.2f" % ((run.distance / 1000) / (duration_seconds / 3600))
            ])

        return list_store

    def activity_tv_mouse_button_cb(self, treeview, event):

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

            # Now handle only right clicks:
            if event.button == 3:
                self.activity_popup_menu.popup(None, None, None, 
                        event.button, time)
                self.activity_tv = treeview

    def activity_delete_cb(self, widget):
        """ 
        Callback for when user selected delete from the activity popup menu.
        """
        treeselection = self.activity_tv.get_selection()
        (model, iter) = treeselection.get_selected()
        query = self.session.query(Activity).filter(Activity.id == 
                model.get_value(iter, 0))
        delete_me = query.one() # will error if not exactly one row returned
        log.debug("Deleting! %s" % delete_me)
        self.session.delete(delete_me)
        self.session.commit()

        # TODO: More expensive than it needs to be, could just delete row from
        # model? Or just repopulate the tab we're on.
        self.populate_tabs()



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

