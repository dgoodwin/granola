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

""" Various utility functions. """

from decimal import Decimal

def calculate_speed(session, meters, seconds):
    """
    Calculate speed in km/h or mph depending on user preference.
    Returns a Decimal, and expects meters and seconds to be Decimal 
    as well.

    Session passed in here, currently unused as we don't yet have 
    configurable units, but when we do they'll be in the db.
    """
    speed = Decimal('0.0')
    # Watch for division by 0: 
    if seconds > 0 and meters > 0: 
        speed = (meters / 1000) / (seconds / 3600)
    return speed

def calculate_pace(session, meters, seconds):
    """
    Calculate pace in seconds per km or mile, depending on user preference.
    Returns a Decimal, and expects meters and seconds to be Decimal 
    as well.

    Session passed in here, currently unused as we don't yet have 
    configurable units, but when we do they'll be in the db.
    """
    pace = Decimal('0.0')
    # Watch for division by 0: 
    if seconds > 0 and meters > 0: 
        pace = (seconds * 1000) / meters
    return pace

def format_time_str(seconds):
    """
    Return a HH:MM:SS string for the given duration in seconds.
    """
    hours = seconds / 3600
    minutes = (seconds / 60) % 60
    seconds = seconds % 60

    return "%02i:%02i:%02i" % (hours, minutes, seconds)
        


