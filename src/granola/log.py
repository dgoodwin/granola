#   Granola - GPS Enabled Open Source Workout/Adventure Log
#
#   Copyright (C) 2008 Devan Goodwin <dgoodwin@dangerouslyinc.com>
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

""" Utility functions related to logging. """

import logging.config

from os.path import expanduser, exists, abspath


def setup_logging(conf_file_locations):
    """ Configure logging by searching for a logging configuration file
    in the provided list of locations. If none are found, default to no
    logging.
    """
    actual_log_conf_location = None
    for location in conf_file_locations:
        if exists(expanduser(location)):
            actual_log_conf_location = location
            break

    if actual_log_conf_location != None:
        logging.config.fileConfig(expanduser(actual_log_conf_location))
    else:
        print("Unable to locate logging configuration in the " + \
            "following locations:")
        for location in conf_file_locations:
            print("   " + abspath(expanduser(location)))

