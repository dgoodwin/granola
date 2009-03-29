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

RUNNING = "running"
BIKING = "biking"
FILTER_ALL = "all"

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
        self.session = Session()

        glade_file = 'granola/glade/mainwindow.glade'
        self.glade_xml = gtk.glade.XML(find_file_on_path(glade_file))
        main_window = self.glade_xml.get_widget('main_window')
        
        # Filter main list of activities based on this, None = show all.
        # Storing just the string name here.
        self.filter_sport = None

        # References to various widgets used throughout the class:
        self.activity_popup_menu = self.glade_xml.get_widget(
                'activity_popup_menu')
        self.activity_tv = self.glade_xml.get_widget('activity_treeview')
        self.sport_filter_combobox = self.glade_xml.get_widget(
                'sport_filter_combobox')
        
        signals = {
            'on_quit_menu_item_activate': self.shutdown,
            'on_main_window_destroy': self.shutdown,
            'on_prefs_menu_item_activate': self.open_prefs_dialog,
            'on_activity_treeview_button_press_event': 
                self.activity_tv_mouse_button_cb,
            'on_activity_popup_delete_activate': 
                self.activity_delete_cb,
            'on_sport_filter_combobox_changed':
                self.filter_sport_cb,
        }
        self.glade_xml.signal_autoconnect(signals)

        self.init_ui()

        self.running = self.session.query(Sport).filter(
                Sport.name == RUNNING).one()
        self.biking = self.session.query(Sport).filter(
                Sport.name == BIKING).one()

        self.populate_activities()

        main_window.show_all()

    def main(self):
        """ Launch the GTK main loop. """
        gtk.main()

    def shutdown(self, widget):
        """ Closes the application. """
        gtk.main_quit()

    def init_ui(self):
        """
        Initialize some UI components, things we need to do just once.
        """
        # Setup activity treeview columns:
        sport_column = gtk.TreeViewColumn("Sport")
        date_column = gtk.TreeViewColumn("Date")
        route_column = gtk.TreeViewColumn("Route")
        distance_column = gtk.TreeViewColumn("Distance (km)")
        time_column = gtk.TreeViewColumn("Time")
        avg_speed_column = gtk.TreeViewColumn("Speed (km/hr)")

        self.activity_tv.append_column(sport_column)
        self.activity_tv.append_column(date_column)
        self.activity_tv.append_column(route_column)
        self.activity_tv.append_column(distance_column)
        self.activity_tv.append_column(time_column)
        self.activity_tv.append_column(avg_speed_column)

        cell = gtk.CellRendererText()

        sport_column.pack_start(cell, expand=False)
        date_column.pack_start(cell, expand=False)
        route_column.pack_start(cell, expand=False)
        distance_column.pack_start(cell, expand=False)
        time_column.pack_start(cell, expand=False)
        avg_speed_column.pack_start(cell, expand=False)

        sport_column.set_attributes(cell, text=6)
        date_column.set_attributes(cell, text=1)
        route_column.set_attributes(cell, text=2)
        distance_column.set_attributes(cell, text=3)
        time_column.set_attributes(cell, text=4)
        avg_speed_column.set_attributes(cell, text=5)


        self.lap_tv = self.glade_xml.get_widget('lap_treeview')

        # Setup lap treeview columns:
        number_column = gtk.TreeViewColumn("Lap")
        distance_column = gtk.TreeViewColumn("Distance (km)")
        time_column = gtk.TreeViewColumn("Time")
        avg_speed_column = gtk.TreeViewColumn("Speed (km/hr)")
        avg_hr_column = gtk.TreeViewColumn("Avg HR")
        max_hr_column = gtk.TreeViewColumn("Max HR")

        self.lap_tv.append_column(number_column)
        self.lap_tv.append_column(distance_column)
        self.lap_tv.append_column(time_column)
        self.lap_tv.append_column(avg_speed_column)
        self.lap_tv.append_column(avg_hr_column)
        self.lap_tv.append_column(max_hr_column)

        cell = gtk.CellRendererText()

        number_column.pack_start(cell, expand=False)
        distance_column.pack_start(cell, expand=False)
        time_column.pack_start(cell, expand=False)
        avg_speed_column.pack_start(cell, expand=False)
        avg_hr_column.pack_start(cell, expand=False)
        max_hr_column.pack_start(cell, expand=False)

        number_column.set_attributes(cell, text=0)
        distance_column.set_attributes(cell, text=1)
        time_column.set_attributes(cell, text=2)
        avg_speed_column.set_attributes(cell, text=3)
        avg_hr_column.set_attributes(cell, text=4)
        max_hr_column.set_attributes(cell, text=5)

        # Populate sport filter combobox with the sports in the database:
        sports_liststore = gtk.ListStore(str)
        self.sport_filter_combobox.set_model(sports_liststore)
        cell = gtk.CellRendererText()
        self.sport_filter_combobox.pack_start(cell, True)
        self.sport_filter_combobox.add_attribute(cell, 'text', 0)  

        self.sport_filter_combobox.append_text("all")
        q = self.session.query(Sport).order_by(Sport.name)
        for sport in q.all():
            self.sport_filter_combobox.append_text(sport.name)
        # Activate the first item for All:
        iter = sports_liststore.get_iter_first()
        self.sport_filter_combobox.set_active_iter(iter)

    def open_prefs_dialog(self, widget):
        prefs_dialog = PreferencesDialog(self.config)

    def populate_activities(self):
        """ Populate activity list. """

        running_liststore = self.build_activity_liststore()
        self.activity_tv.set_model(running_liststore)

    def build_activity_liststore(self):
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
                str, # sport
                #float, # avg heart rate
        )
        q = self.session.query(Activity).order_by(Activity.start_time.desc())
        if self.filter_sport is not None:
            q = q.filter(Activity.sport == self.filter_sport)
        #q = self.session.query(Activity).filter(Activity.sport == 
        #        sport).order_by(Activity.start_time.desc())
        for run in q.all():
            duration_seconds = run.duration
            hours = duration_seconds / 3600
            minutes = (duration_seconds / 60) % 60
            seconds = duration_seconds % 60

            list_store.append([
                run.id,
                run.start_time.strftime("%Y-%m-%d"),
                "N/A", 
                "%.2f" % (run.distance / 1000),
                "%02i:%02i:%02i" % (hours, minutes, seconds),                
                "%.2f" % ((run.distance / 1000) / (duration_seconds / 3600)),
                run.sport.name,
            ])

        return list_store

    def display_activity(self, activity):
        """ 
        Display an activities details. (below the activities list)
        """
        start_time_widget = self.glade_xml.get_widget('activity_date_display')
        time_widget = self.glade_xml.get_widget('activity_time_display')
        distance_widget = self.glade_xml.get_widget('activity_distance_display')
        speed_widget = self.glade_xml.get_widget('activity_speed_display')
        pace_widget = self.glade_xml.get_widget('activity_pace_display')
        avg_hr_widget = self.glade_xml.get_widget('activity_hr_display')

        duration_seconds = activity.duration
        hours = duration_seconds / 3600
        minutes = (duration_seconds / 60) % 60
        seconds = duration_seconds % 60

        start_time_widget.set_text(activity.start_time.strftime(
            "%Y-%m-%d %H:%M"))
        time_widget.set_text("%02i:%02i:%02i" % (hours, minutes, seconds)) 
        distance_widget.set_text("%.2f km" % (activity.distance / 1000))
        speed_widget.set_text("%.2f km/hr" % ((activity.distance / 1000) / 
            (duration_seconds / 3600)))
        pace_widget.set_text("-")

        avg_hr = "-" # activity may not have heart rate data
        if activity.heart_rate_avg is not None:
            avg_hr = "%.0f" % activity.heart_rate_avg
        avg_hr_widget.set_text(avg_hr)

        lap_liststore = gtk.ListStore(
                int, # lap number
                str, # distance
                str, # time
                str, # speed
                str, # avg hr
                str, # max hr
        )
        q = self.session.query(Lap)
        q = q.filter(Lap.activity == activity)
        q = q.order_by(Lap.start_time)
        i = 1
        for lap in q.all():
            duration_seconds = lap.duration
            hours = duration_seconds / 3600
            minutes = (duration_seconds / 60) % 60
            seconds = duration_seconds % 60

            lap_liststore.append([
                i,
                "%.2f" % (lap.distance / 1000),
                "%02i:%02i:%02i" % (hours, minutes, seconds),                
                "%.2f" % ((lap.distance / 1000) / (duration_seconds / 3600)),
                lap.heart_rate_avg,
                lap.heart_rate_max,
            ])
            i += 1

        self.lap_tv.set_model(lap_liststore)

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
                selection = self.activity_tv.get_selection()
                (model, iter) = selection.get_selected()
                # Lookup the activity object rather than rely on model columns:
                activity = self.session.query(Activity).filter(Activity.id ==
                        model.get_value(iter, 0)).one()
                self.display_activity(activity)

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
        # model?
        self.populate_activities()

    def filter_sport_cb(self, widget):
        """ 
        Callback for when user changes the filter on sport.
        """
        iter = self.sport_filter_combobox.get_active_iter()
        filter_name = self.sport_filter_combobox.get_model().get_value(iter, 0)
        if filter_name == FILTER_ALL: 
            self.filter_sport = None
        else:
            self.filter_sport = self.session.query(Sport).filter(
                    Sport.name == filter_name).one()
        
        self.populate_activities()



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

