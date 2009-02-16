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

RUNNING = "Running"

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

class GranolaMainWindow:
    """
    Main Granola GTK UI Window
    """

    def __init__(self):
        log.debug("Starting GTK UI.")
        glade_file = 'granola/glade/mainwindow.glade'
        self.glade_xml = gtk.glade.XML(find_file_on_path(glade_file))
        main_window = self.glade_xml.get_widget('main_window')

        self.session = Session()
        self.running = self.session.query(Sport).filter(
                Sport.name == RUNNING).one()

        self._populate_trees()

        main_window.show_all()

    def main(self):
        """ Launch the GTK main loop. """
        gtk.main()

    def _populate_trees(self):
        self._populate_running_tab_trees()

    def _build_runs_liststore(self):
        """ Return a ListStore with data for all runs. """
        runs_liststore = gtk.ListStore(
                str, # date
                str, # route
                str, # distance
                #str, #time
                #float, # avg speed
                #float, # avg heart rate
        )
        q = self.session.query(Activity).filter(Activity.sport == 
                self.running)
        for run in q.all():
            runs_liststore.append([
                run.start_time, 
                "N/A", 
                str(run.distance / 1000)[0:5]
            ])
        return runs_liststore

    def _populate_running_tab_trees(self):
        """ Populate lists on the running tab. """
        runs_liststore = self._build_runs_liststore()

        runs_treeview = self.glade_xml.get_widget("runs_treeview")
        runs_treeview.set_model(runs_liststore)

        # Create columns:
        date_column = gtk.TreeViewColumn("Date")
        route_column = gtk.TreeViewColumn("Route")
        distance_column = gtk.TreeViewColumn("Distance (km)")

        runs_treeview.append_column(date_column)
        runs_treeview.append_column(route_column)
        runs_treeview.append_column(distance_column)

        cell1 = gtk.CellRendererText()
        cell2 = gtk.CellRendererText()

        date_column.pack_start(cell1, expand=False)
        route_column.pack_start(cell1, expand=False)
        distance_column.pack_start(cell2, expand=False)

        date_column.set_attributes(cell1, text=0)
        route_column.set_attributes(cell1, text=1)
        distance_column.set_attributes(cell2, text=2)



