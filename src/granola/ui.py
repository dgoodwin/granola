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

        self._populate_trees()

        main_window.show_all()

    def main(self):
        """ Launch the GTK main loop. """
        gtk.main()

    def _populate_trees(self):
        self._populate_running_tab_trees()

    def _populate_running_tab_trees(self):
        """ Populate lists on the running tab. """
        runs_list_store = gtk.ListStore(
                gobject.TYPE_STRING, 
                gobject.TYPE_FLOAT
        )
        runs_list_store.append(["2009-02-08 12:50pm", 4.67])

