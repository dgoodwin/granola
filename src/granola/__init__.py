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
import ConfigParser

from granola.log import log
from granola.const import DATA_DIR, SQLITE_DB
from granola.model import initialize_db

GRANOLARC = os.path.join(DATA_DIR, "granolarc")


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

def read_or_create_config():
    """
    Read configuration from granolarc, or create it with default
    settings if necessary.
    """
    config = ConfigParser.ConfigParser()
    if os.path.exists(GRANOLARC):
        # Read in existing settings:
        config.read(GRANOLARC)

    # Check for all required settings, if missing add a default:
    default_import_settings = {
            'import_folder': os.path.join(os.path.expanduser("~/"), 
                "exports"),
    }
    if not config.has_section("import"):
        config.add_section("import")
    for setting in default_import_settings.keys():
        if not config.has_option("import", setting):
            default_value = default_import_settings[setting]
            log.warn("Missing setting in granolarc, adding %s = %s" %
                    (setting, default_value))
            config.set("import", setting, default_value)

    # Write the config back out now that we've added a default for anything 
    # that was missing:
    write_config(config)
    return config

def write_config(config):
    """ Write granolarc config to disk. """
    f = open(GRANOLARC, 'w')
    config.write(f)
    f.close()


