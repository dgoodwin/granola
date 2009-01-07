#   Granola - GPS Enabled Open Source Workout/Adventure Log
#
#   Copyright (C) 2008 Devan Goodwin <dgoodwin@dangerouslyinc.com>
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

from logging import getLogger
log = getLogger("granola.import")

import os

class Importer(object):
    """ Parent Importer class. """

    def scan_dir(self, directory):
        """ Scan a directory for new data files to import. """
        pass



class GarminTcxImporter(Importer):
    """ 
    Importer for Garmin TCX XML Documents. 
    
    See: http://developer.garmin.com/schemas/tcx/v2/
    """

    def scan_dir(self, directory):
        """ Scan a directory for new data files to import. """
        if not os.path.exists(directory):
            raise Exception("No such directory: %s" % directory)
        log.debug("Scanning %s for new data." % directory) 
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".tcx"):
                    self.import_file(os.path.join(root, file))

    def import_file(self, filename):
        """ Import the data in the given file if necessary. """
        if not os.path.exists(filename):
            raise Exception("No such file: %s" % filename)
        log.info("Importing: %s" % filename)
        # TODO: Check that we haven't already imported this file.
