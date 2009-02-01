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
import dateutil.parser
from xml.etree.ElementTree import ElementTree

from granola.model import *
from granola.log import log

def debug_activity(activity):
    """ Log debug info on this activity. """
    log.debug("Activity: %s" % activity.start_time)
    i = 1
    for lap in activity.laps:
        log.debug("   Lap %s:" % i)
        log.debug("      Start Time: %s" % lap.start_time)
        log.debug("      Duration: %s seconds" % lap.duration)
        log.debug("      Distance: %s meters" % lap.distance)
        log.debug("      Max speed: %s meters/second" % lap.speed_max)
        log.debug("      Calories: %s" % lap.calories)
        log.debug("      Max heart rate: %s bpm" % lap.heart_rate_max)
        log.debug("      Avg heart rate: %s bpm" % lap.heart_rate_avg)
        i += 1

class Importer(object):
    """ Parent Importer class. """

    def scan_dir(self, directory):
        """ Scan a directory for new data files to import. """
        pass

    def import_file(self, filename):
        """ 
        Import the data in the given file. 
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

        session = Session()

        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".tcx"):
#                    try:
                        self.import_file(session, os.path.join(root, file))
                        session.commit()
#                    except Exception, ex:
#                        log.error("Error importing: %s" % file)
#                        log.error(ex)
#                        session.rollback()

    def import_file(self, session, filename):
        """ 
        Import the data in the given file. 
        """
        if not os.path.exists(filename):
            raise Exception("No such file: %s" % filename)

        # Check if we've imported this file before. Assume
        # if an activity exists with a start time equal to the 
        # file name, that way we dont waste time parsing
        # the XML.
        start_time = dateutil.parser.parse(os.path.basename(filename)[0:-4])
        if session.query(Activity).filter(Activity.start_time == 
                start_time).first():
            log.info("Skipping: %s" % start_time)
            return

        log.info("Importing: %s" % filename)

        tree = ElementTree()
        tree.parse(filename)
        root = tree.getroot()
        activities_elem = root.find(self._get_tag("Activities"))
        if activities_elem is None: 
            raise Exception("Unable to parse %s: No activities found." %
                    filename)
        for activity_elem in activities_elem.findall(self._get_tag("Activity")):
            self._parse_activity(session, activity_elem)

    def _parse_activity(self, session, activity_elem):
        """ Parse an XML activity element. """
        sport = self._get_activity_sport(session, activity_elem)

        # NOTE: Using the ID for a start time here, it appears to be equal
        # to the start time of the first lap but not sure if this is 
        # guaranteed in the XML definition:
        start_time_elem = activity_elem.find(self._get_tag("Id"))
        start_time = dateutil.parser.parse(start_time_elem.text)

        activity = Activity(start_time=start_time, sport=sport)
        lap_elements = activity_elem.findall(self._get_tag("Lap"))
        for lap_elem in lap_elements:
            new_lap = self._parse_lap(lap_elem)
            activity.laps.append(new_lap)

        debug_activity(activity)
        session.add(activity)

    def _parse_lap(self, lap_elem):
        """ Parse an XML lap element. """
        start_time = dateutil.parser.parse(lap_elem.attrib['StartTime'])
        duration = lap_elem.find(self._get_tag("TotalTimeSeconds")).text
        distance = lap_elem.find(self._get_tag("DistanceMeters")).text
        speed_max = lap_elem.find(self._get_tag("MaximumSpeed")).text
        calories = lap_elem.find(self._get_tag("Calories")).text

        heart_rate_max = None
        max_hr_elem = lap_elem.find(self._get_tag("MaximumHeartRateBpm"))
        if max_hr_elem:
            heart_rate_max = max_hr_elem.find(self._get_tag("Value")).text

        heart_rate_avg = None
        avg_hr_elem = lap_elem.find(self._get_tag("AverageHeartRateBpm"))
        if avg_hr_elem:
            heart_rate_avg = avg_hr_elem.find(self._get_tag("Value")).text

        lap = Lap(start_time=start_time, duration=duration, distance=distance,
                speed_max=speed_max, calories=calories, 
                heart_rate_max=heart_rate_max, heart_rate_avg=heart_rate_avg)
        return lap

    def _get_activity_sport(self, session, activity):
        """
        Lookup a Sport object for this activity.
        """
        xml_sport = activity.attrib['Sport']
        q = session.query(Sport).filter(Sport.name.like(xml_sport))
        # Will error out if no sport is found:
        sport = q.one()
        return sport

    def _get_tag(self, tag):
        """
        Returns the tag name prefixed with the XML namespace.
        i.e. {XMLNS}Tag
        """
        return "{%s}%s" % (self.xmlns, tag)

