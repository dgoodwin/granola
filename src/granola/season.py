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

""" Granola's Season Module """

from datetime import datetime, timedelta

from granola.log import log

# TODO: TIMEZONES, I guess it's not real critical but there's probably a 
# pile of things to worry about below if we want to get it right. Maybe
# get the user to define their timezone (or use system's), and let the
# chips fall where they may wrt activities.
def find_season(activity_date, seasons):
    """
    Create the appropriate season object for the given activity date.

    Uses the given list of seasons to identify which season this
    activity falls into.
    """
    the_season = None
    i = 0
    for s in seasons:
        if s.month <= activity_date.month and s.day <= activity_date.day:
            the_season = s
        i = i + 1

    # If we couldn't find a season that starts before our activity date,
    # we want the last one. (which must wrap around over the year)
    if the_season == None:
        the_season = seasons[-1]

    # Should have found the season with the start date closest to our 
    # activity by now, so we create the slice for it:
    log.debug("found season %s: %s - %s" % (the_season.name, 
        the_season.month, the_season.day))

    # Previous year if the season month is greater than our activity's:
    start_year = activity_date.year
    if the_season.month > activity_date.month or (the_season.month ==
            activity_date.month and the_season.day > activity_date.day):
        start_year = start_year - 1

    start_date = datetime(year=start_year, month=the_season.month, 
            day=the_season.day)
    log.debug("start_date = %s" % start_date)

    # Now for the end date:
    next_season = seasons[(i + 1) % len(seasons)]
    log.debug("next season %s: %s - %s" % (next_season.name, 
        next_season.month, next_season.day))
    next_season_year = start_year # probably the same but could wrap
    if next_season.month < the_season.month or (next_season.month ==
            the_season.month and next_season.day < the_season.day):
        next_season_year = start_year + 1

    end_date = datetime(year=next_season_year, month=next_season.month,
            day=next_season.day) - timedelta(seconds=1)
    log.debug("end_date = %s" % end_date)

    return SeasonSlice(the_season, start_date, end_date)


class Season(object):
    """ 
    Represents a season by a month and day where the season starts. 

    Sub-classed in the db model for user defined seasons, but also used
    for monthly and yearly statistics as well.
    """
    def __init__(self, month, day, name):
        if month == 2 and day == 29:
            # Nice try Mr. User
            raise LeapDaySeasonBoundaryException()
        self.month = month
        self.day = day
        self.name = name


class SeasonSlice(object):
    """ 
    A concrete season with a defined start and end datetime in a specific
    year.
    """
    def __init__(self, season, start_date, end_date):
        self.season = season
        self.start_date = start_date
        self.end_date = end_date


class LeapDaySeasonBoundaryException(Exception):
    """ 
    Exception thrown if trying to create a Season with a boundary on a
    leap day. 
    """
    pass
