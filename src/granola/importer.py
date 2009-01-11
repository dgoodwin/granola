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

import os
from xml.etree.ElementTree import ElementTree

from granola.model import *
from granola.log import log

class Importer(object):
    """ Parent Importer class. """

    def scan_dir(self, directory):
        """ Scan a directory for new data files to import. """
        pass

    def import_file(self, filename):
        """ 
        Import the data in the given file. (if we haven't done so before). 
        """
        pass



class GarminTcxImporter(Importer):
    """ 
    Importer for Garmin TCX XML Documents. 
    
    See: http://developer.garmin.com/schemas/tcx/v2/
    """
    # TODO: There must be a way to get this off the ElementTree object:
    xmlns = "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"

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
        """ 
        Import the data in the given file. (if we haven't done so before). 
        """
        if not os.path.exists(filename):
            raise Exception("No such file: %s" % filename)
        log.info("Importing: %s" % filename)

        # TODO: Check that we haven't already imported this file.
        session = Session()

        tree = ElementTree()
        tree.parse(filename)
        root = tree.getroot()
        activities = root.find(self._get_tag("Activities"))
        if activities is None: 
            raise Exception("Unable to parse %s: No activities found." %
                    filename)
        for activity_elem in activities.findall(self._get_tag("Activity")):
            self._parse_activity(session, activity_elem)

    def _parse_activity(self, session, activity):
        """ Parse an XML activity element. """
        sport = self._get_activity_sport(session, activity)

    def _get_activity_sport(self, session, activity):
        """
        Lookup a Sport object for this activity.
        """
        xml_sport = activity.attrib['Sport']
        log.debug("Activity sport: %s" % xml_sport)
        sport = session.query(Sport).filter(Sport.name.like(xml_sport))
        log.debug("Sport: %s" % sport)


    def _get_tag(self, tag):
        """
        Returns the tag name prefixed with the XML namespace.
        i.e. {XMLNS}Tag
        """
        return "{%s}%s" % (self.xmlns, tag)

