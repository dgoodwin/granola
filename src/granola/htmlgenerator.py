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
                map.setCenter(new GLatLng(%s, %s), 15);
                map.setUIToDefault();
                var polyline = new GPolyline([
"""

HTML_FOOTER = """
                        ], "#0000ff", 3);
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

        title = "Granola Activity Map: %s (%s)" % (self.activity.start_time,
                self.activity.sport.name)
        # TODO: Find a better way to center the map than starting point.
        center_coords = self.activity.laps[0].tracks[0].trackpoints[0]

        f.write(HTML_HEADER % (title, center_coords.latitude, 
            center_coords.longitude))

        for lap in self.activity.laps:
            for track in lap.tracks:
                for trackpoint in track.trackpoints:
                    if trackpoint.latitude is None:
                        # TODO: Empty data in a trackpoint indicates a pause, 
                        # could display this easily.
                        continue
                    f.write("new GLatLng(%s, %s)," % (trackpoint.latitude, 
                        trackpoint.longitude))

        f.write(HTML_FOOTER)
        f.close()
        return filepath
