#!/usr/bin/env python
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
All constants.
"""

import os.path


VERSION = "0.1"
DATA_DIR = os.path.expanduser(os.path.join("~", ".granola"))
SQLITE_DB = os.path.join(DATA_DIR, "granola.db")
LOG_CONF_LOCATIONS = [
    os.path.join("~", ".granola", "logging.conf"),
    os.path.join(".", "conf", "logging.conf"),
]
