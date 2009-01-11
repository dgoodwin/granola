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
granola .... yum!
"""

import logging
import os
import os.path

from granola.log import log
from granola.model import initialize_db


DATA_DIR = os.path.expanduser("~/.granola")
SQLITE_DB = "%s/granola.db" % DATA_DIR


def is_first_run():
    """
    Return True if this is the first time the user has run this program.
    """
    if (not os.path.exists(DATA_DIR)):
        return True
    if (not os.path.exists(SQLITE_DB)):
        return True
    return False


def initialize_granola():
    """
    Create the data directory, database, config files, and anything else
    required on the first run of the software.
    """
    log.info("Creating %s." % DATA_DIR)
    try:
        os.mkdir(DATA_DIR)
    except OSError:
        pass

    initialize_db()

