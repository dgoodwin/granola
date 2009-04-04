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

# Assume "running" below this threshold as walking:
WALK_RUN_THRESHOLD = 6000.0 / 3600.0


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

        base_filename = os.path.basename(filename)

        # Check if we've imported this file before. Assume
        # if an activity exists with a start time equal to the
        # file name, that way we dont waste time parsing
        # the XML.
        start_time = dateutil.parser.parse(base_filename[0:-4])
        if session.query(Import).filter(Import.identifier ==
                base_filename).first():
            log.info("Skipping: %s" % base_filename)
            return

        log.info("Importing: %s" % filename)

        tree = ElementTree()
        tree.parse(filename)
        root = tree.getroot()
        activities_elem = root.find(self._get_tag("Activities"))
        if activities_elem is None:
            raise Exception("Unable to parse %s: No activities found." %
                    filename)
        for activity_elem in activities_elem.findall(
            self._get_tag("Activity")):
            self._parse_activity(session, activity_elem)

        # Store that we've imported this file in the past, allowing us to
        # delete in the UI without re-importing it if the file is still laying
        # around in the directory. Manual file import should be made available
        # at some point to correct any delete mistakes.
        imp = Import(1, base_filename)
        session.add(imp)

    def _parse_activity(self, session, activity_elem):
        """ Parse an XML activity element. """

        # NOTE: Using the ID for a start time here, it appears to be equal
        # to the start time of the first lap but not sure if this is
        # guaranteed in the XML definition:
        start_time_elem = activity_elem.find(self._get_tag("Id"))
        start_time = dateutil.parser.parse(start_time_elem.text)

        activity = Activity(start_time=start_time, sport=None)
        lap_elements = activity_elem.findall(self._get_tag("Lap"))
        for lap_elem in lap_elements:
            new_lap = self._parse_lap(lap_elem)
            activity.laps.append(new_lap)

        debug_activity(activity)
        sport = self._get_activity_sport(session, activity_elem, activity)
        activity.sport = sport
        session.add(activity)

    def _parse_lap(self, lap_elem):
        """ Parse an XML lap element. """
        start_time = dateutil.parser.parse(lap_elem.attrib['StartTime'])
        duration = float(lap_elem.find(self._get_tag("TotalTimeSeconds")).text)
        distance = float(lap_elem.find(self._get_tag("DistanceMeters")).text)
        speed_max = float(lap_elem.find(self._get_tag("MaximumSpeed")).text)
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

        track_element = lap_elem.find(self._get_tag("Track"))
        if track_element is not None:
            trackpoint_elements = track_element.findall(
                    self._get_tag("Trackpoint"))
            for trackpoint_element in trackpoint_elements:
                new_trackpoint = self._parse_trackpoint(trackpoint_element)
                lap.trackpoints.append(new_trackpoint)

        return lap

    def _parse_trackpoint(self, trackpoint_elem):
        time = dateutil.parser.parse(trackpoint_elem.find(
            self._get_tag("Time")).text)

        altitude = None
        altitude_elem = trackpoint_elem.find(
            self._get_tag("AltitudeMeters"))
        if altitude_elem is not None:
            altitude = float(altitude_elem.text)

        distance = None
        distance_elem = trackpoint_elem.find(
            self._get_tag("DistanceMeters"))
        if distance_elem is not None:
            distance = float(distance_elem.text)


        heart_rate = None
        heart_rate_elem = trackpoint_elem.find(
            self._get_tag("HeartRateBpm"))
        if heart_rate_elem is not None:
            heart_rate_value_elem = heart_rate_elem.find(
                    self._get_tag("Value"))
            heart_rate = int(heart_rate_value_elem.text)

        latitude = None
        longitude = None
        position_elem = trackpoint_elem.find(self._get_tag("Position"))
        if position_elem is not None:
            latitude = float(position_elem.find(
                self._get_tag("LatitudeDegrees")).text)
            longitude = float(position_elem.find(
                self._get_tag("LongitudeDegrees")).text)
        
        tp = TrackPoint(time=time, latitude=latitude, longitude=longitude, 
                altitude=altitude, distance=distance, heart_rate=heart_rate)
        return tp

    def _get_activity_sport(self, session, activity_elem, activity):
        """
        Lookup a Sport object for this activity.
        """
        xml_sport = activity_elem.attrib['Sport']

        # Running slow == walking!
        if xml_sport.lower() == SPORTNAME_RUNNING:
            speed = float(activity.distance) / float(activity.duration)
            if speed < WALK_RUN_THRESHOLD:
                xml_sport = SPORTNAME_WALKING

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
