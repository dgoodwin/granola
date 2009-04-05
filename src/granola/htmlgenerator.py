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

HTML_START="""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" 
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" 
    xmlns:v="urn:schemas-microsoft-com:vml">
    <head>
        <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
"""

HTML_2="""
        <script src="http://maps.google.com/maps?file=api&amp;v=2&amp;key=ABQIAAAAzr2EBOXUKnm_jVnk0OJI7xSosDVG8KKPE1-m51RBrvYughuyMxQ-i1QfUnH94QxWIa6N4U6MouMmBA"
            type="text/javascript"></script>
        <script type="text/javascript"> 

        function initialize() {
            if (GBrowserIsCompatible()) {
                var map = new GMap2(document.getElementById("map_canvas"));
                map.addControl(new GLargeMapControl());
                map.addControl(new GLargeMapControl());
"""

HTML_3="""
var polyline = new GPolyline([
"""

HTML_END="""
                        ], "#ff0000", 10);
                map.addOverlay(polyline);
            }
        } 
</script>
  </head>

  <body onload="initialize()">
      <div id="map_canvas" style="width: 640px; height: 480px; float:left; border: 1px solid black;"></div>
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

        if len(self.activity.laps) == 0:
            return "<html><body>No trackpoints</body></html>"
        elif len(self.activity.laps[0].trackpoints) == 0:
            return "<html><body>No trackpoints</body></html>"

        html_title = "<title>Granola Activity: %s</title>\n" % self.activity.id

        center_coords = self.activity.laps[0].trackpoints[0]
        html_center_coords = "map.setCenter(new GLatLng(%s, %s), 13);" \
                % (center_coords.latitude, center_coords.longitude)

        html_coords = ""
        for lap in self.activity.laps:
            for trackpoint in lap.trackpoints:
                if trackpoint.latitude is None:
                    continue
                html_coords += """new GLatLng(%s, %s),""" % (trackpoint.latitude, trackpoint.longitude)


        html = "%s%s%s%s%s%s%s" % (
                HTML_START, 
                html_title,
                HTML_2,
                html_center_coords,
                HTML_3,
                html_coords,
                HTML_END
        )
        filepath = "/tmp/granola-%s-%s-%s.html" % (self.activity.id,
                self.activity.sport.name, self.activity.start_time)
        f = open(filepath, "w")
        f.write(html)
        f.close()
        return filepath



