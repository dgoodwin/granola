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

""" 
Browser Window Used to Display Google Maps 

Based on the demo code included with PyWebkit.
"""

import gtk
import webkit

from gettext import gettext as _

from granola.log import log
from granola.htmlgenerator import HtmlGenerator

class BrowserPage(webkit.WebView):

    def __init__(self):
        webkit.WebView.__init__(self)


class WebStatusBar(gtk.Statusbar):
    def __init__(self):
        gtk.Statusbar.__init__(self)
        self.iconbox = gtk.EventBox()
        self.iconbox.add(gtk.image_new_from_stock(gtk.STOCK_INFO, 
            gtk.ICON_SIZE_BUTTON))
        self.pack_start(self.iconbox, False, False, 6)
        self.iconbox.hide_all()

    def display(self, text, context=None):
        cid = self.get_context_id("granola")
        self.push(cid, str(text))

    def show_javascript_info(self):
        self.iconbox.show()

    def hide_javascript_info(self):
        self.iconbox.hide()


class WebBrowser(gtk.Window):
    def __init__(self, activity):
        gtk.Window.__init__(self)
        self.activity = activity

        log.debug("Opening browser window.")

        self._loading = False
        self._browser= BrowserPage()
        self._browser.connect('load-started', self._loading_start_cb)
        self._browser.connect('load-progress-changed', 
                self._loading_progress_cb)
        self._browser.connect("title-changed", 
                self._title_changed_cb)
        self._browser.connect("hovering-over-link", 
                self._hover_link_cb)
        self._browser.connect("status-bar-text-changed", 
                self._statusbar_text_changed_cb)
        self._browser.connect("console-message",
                              self._javascript_console_message_cb)

        self._scrolled_window = gtk.ScrolledWindow()
        self._scrolled_window.props.hscrollbar_policy = gtk.POLICY_AUTOMATIC
        self._scrolled_window.props.vscrollbar_policy = gtk.POLICY_AUTOMATIC
        self._scrolled_window.add(self._browser)
        self._scrolled_window.show_all()

        self._statusbar = WebStatusBar()

        vbox = gtk.VBox(spacing=4)
        vbox.pack_start(self._scrolled_window)
        vbox.pack_end(self._statusbar, expand=False, fill=False)

        self.add(vbox)
        self.set_default_size(800, 600)

        self.connect('destroy', self.close_window)
        generator = HtmlGenerator(self.activity)
        html = generator.generate_html()
        self._browser.load_string(html, "text/html", "iso-8859-15", "about:")
        #self._browser.open("file:///home/dev/exports/kml.html")

        self.show_all()

    def close_window(self, widget):
        self.destroy()

    def _set_title(self, title):
        self.props.title = title

    def _loading_start_cb(self, view, frame):
        main_frame = self._browser.get_main_frame()
        if frame is main_frame:
            self._set_title(_("Loading %s - %s") % 
                    (frame.get_title(),frame.get_uri()))

    def _loading_progress_cb(self, view, progress):
        self._set_progress(_("%s%s loaded") % (progress, '%'))

    def _set_progress(self, progress):
        self._statusbar.display(progress)

    def _title_changed_cb(self, widget, frame, title):
        self._set_title(_("%s") % title)

    def _hover_link_cb(self, view, title, url):
        if view and url:
            self._statusbar.display(url)
        else:
            self._statusbar.display('')

    def _statusbar_text_changed_cb(self, view, text):
        if text:
            self._statusbar.display(text)

    def _navigation_requested_cb(self, view, frame, networkRequest):
        return 1

    def _javascript_console_message_cb(self, view, message, line, sourceid):
        self._statusbar.show_javascript_info()

