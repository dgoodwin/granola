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

""" Generate Temporary HTML Files To Render Google Maps """

import math

from decimal import Decimal
from granola.log import log

HTML_HEADER = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" 
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" 
    xmlns:v="urn:schemas-microsoft-com:vml">
    <head>
        <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
        <title>%s</title>
        <script src="http://maps.google.com/maps?file=api&amp;v=2&amp;key=ABQIAAAAzr2EBOXUKnm_jVnk0OJI7xSosDVG8KKPE1-m51RBrvYughuyMxQ-i1QfUnH94QxWIa6N4U6MouMmBA"
            type="text/javascript"></script>
        <script type="text/javascript"> 

        function initialize() {
            if (GBrowserIsCompatible()) {
                var map = new GMap2(document.getElementById("map_canvas"));
                // Initialize map, should be done before everything else.
                map.setCenter(new GLatLng(%s, %s), 14);
                map.setMapType(G_SATELLITE_MAP);
                map.setUIToDefault();
                var polyline = new GPolyline([
"""

EARTHS_RADIUS = 6372.797

def distance_between_coords(lat1, lon1, lat2, lon2):
    """ 
    Returns the distance between two pairs of latitude/longitude coordinates.

    Based on http://snipplr.com/view/2531/, sorry for the terrible variable
    names.
    """
    pi180 = Decimal(str(math.pi / 180))
    temp_lat1 = lat1
    temp_lon1 = lon1
    temp_lat2 = lat2
    temp_lon2 = lon1

    temp_lat1 *= pi180
    temp_lon1 *= pi180
    temp_lat2 *= pi180
    temp_lon2 *= pi180

    dlat = temp_lat2 - temp_lat1
    dlon = temp_lon2 - temp_lon1
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(temp_lat1) * \
            math.cos(temp_lat2) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    km = EARTHS_RADIUS * c
    return km


HTML_FOOTER = """
                map.addControl(new GLargeMapControl());
                map.addControl(new GLargeMapControl());
                map.addOverlay(polyline);
            }
        } 
        </script>
  </head>

  <body onload="initialize()">
      <div id="map_canvas" style="width: 750px; height: 550px; float:center; border: 1px solid black;"></div>
  </div>
  <br clear="all"/>
  <br/>
  </body>
</html>
"""

class HtmlGenerator(object):

    def __init__(self, activity):
        self.activity = activity

    def generate_html(self):
        """ 
        Generate HTML to render a Google Map for the configured activity. 
        """

        filepath = "/tmp/granola-%s-%s.html" % (self.activity.id,
                self.activity.sport.name)
        f = open(filepath, "w")

        if len(self.activity.laps) == 0:
            f.write("<html><body>No trackpoints</body></html>")
            f.close()
            return filepath
        elif len(self.activity.laps[0].tracks) == 0:
            f.write("<html><body>No trackpoints</body></html>")
            f.close()
            return filepath
        elif len(self.activity.laps[0].tracks[0].trackpoints) == 0:
            f.write("<html><body>No trackpoints</body></html>")
            f.close()
            return filepath

        (maxLat, maxLon, minLat, minLon, centerLat, centerLon) = \
                self._calculate_center_coords(self.activity)

        title = "Granola Activity Map: %s (%s)" % (self.activity.start_time,
                self.activity.sport.name)
        # TODO: Find a better way to center the map than starting point.
        center_coords = self.activity.laps[0].tracks[0].trackpoints[0]

        f.write(HTML_HEADER % (title, centerLat, centerLon))

        # TODO: iterating trackpoints a second time but probably faster
        # than doing the string concatenation we'd have to do otherwise.
        for lap in self.activity.laps:
            for track in lap.tracks:
                for trackpoint in track.trackpoints:
                    if trackpoint.latitude is None:
                        # TODO: Empty data in a trackpoint indicates a pause, 
                        # could display this easily.
                        continue
                    f.write("new GLatLng(%s, %s)," % (trackpoint.latitude, 
                        trackpoint.longitude))
        f.write("""                        ], "#0000ff", 3);""")
        f.write("""map.addOverlay(new GMarker(new GLatLng(%s, %s)));""" %
                (maxLat, maxLon))
        f.write("""map.addOverlay(new GMarker(new GLatLng(%s, %s)));""" %
                (minLat, minLon))

        f.write(HTML_FOOTER)
        f.close()
        return filepath

    def _calculate_center_coords(self, activity):
        """ Calculate the latitude and longitude to center on. """

        maxLat = None
        minLat = None
        maxLon = None
        minLon = None
        for lap in self.activity.laps:
            for track in lap.tracks:
                for trackpoint in track.trackpoints:
                    if trackpoint.latitude is None:
                        continue
                    if maxLat is None:
                        # Assume all must be None:
                        maxLat = trackpoint.latitude
                        minLat = trackpoint.latitude
                        maxLon = trackpoint.longitude
                        minLon = trackpoint.longitude
                    else:
                        maxLat = max(maxLat, trackpoint.latitude)
                        minLat = min(minLat, trackpoint.latitude)
                        maxLon = max(maxLon, trackpoint.longitude)
                        minLon = min(minLon, trackpoint.longitude)

        span_km = distance_between_coords(maxLat, maxLon, minLat, minLon)
        log.debug("Distance between coordinates: %s" % span_km)

        centerLat = minLat + (maxLat - minLat) / 2
        centerLon = minLon + (maxLon - minLon) / 2

        return (maxLat, maxLon, minLat, minLon, centerLat, centerLon)

