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
def create_first_slice(seasons, activity_date):
    """
    Create the appropriate season slice for the given activity date.

    Uses the given list of seasons to identify which season this
    activity falls into.
    """
    the_season = None
    i = 0
    season_index = None
    for s in seasons:
        if s.month <= activity_date.month and s.day <= activity_date.day:
            the_season = s
            season_index = i
        i = i + 1

    # If we couldn't find a season that starts before our activity date,
    # we want the last one. (which must wrap around over the year)
    if the_season is None:
        the_season = seasons[-1]
        season_index = len(seasons) - 1

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
    next_season = seasons[(season_index + 1) % len(seasons)]
    log.debug("next season %s: %s - %s" % (next_season.name, 
        next_season.month, next_season.day))
    return SeasonSlice(the_season, start_date, next_season)

def build_season_slices(seasons, first_activity_date, last_activity_date):
    """
    Return a list of all season slices using the configured season boundaries,
    first activity date, and last activity date. 
    """

    starting_slice = create_first_slice(seasons, first_activity_date)

    log.debug("Building all season slices:")
    log.debug("   starting slice: %s" % starting_slice)
    log.debug("   last activity: %s" % last_activity_date)
    # What season does the starting slice point to?
    season_index = 0
    for s in seasons:
        if s.month == starting_slice.start_date.month and \
                s.day == starting_slice.start_date.day:
                    break
        else:
            season_index += 1
    log.debug("season_index = %s" % season_index)

    # Keep building season slices until one ends beyond the date of
    # our last activity:
    all_slices = [starting_slice]
    while all_slices[-1].end_date <= last_activity_date:
        log.debug("Building new slice:")
        season_index = (season_index + 1) % len(seasons)
        next_season = seasons[season_index]
        log.debug("   next_season = %s" % next_season)
        start_date = all_slices[-1].end_date + timedelta(seconds=1)
        log.debug("   start_date = %s" % start_date)
        new_slice = SeasonSlice(next_season, start_date, 
                seasons[(season_index + 1) % len(seasons)])
        log.debug("   new_slice = %s" % new_slice)
        all_slices.append(new_slice)

    log.debug("Seasons:")
    for s in all_slices:
        log.debug(s)

    return all_slices


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

    def __repr__(self):
        return "<Season: %s - %s-%s>" % (self.name, self.month, self.day)

class SeasonSlice(object):
    """ 
    A concrete season with a defined start and end datetime in a specific
    year.

    End date is calculated based on the start time of the next season.
    (1 second before)
    """
    def __init__(self, season, start_date, next_season):
        self.season = season
        self.start_date = start_date

        next_season_year = start_date.year # probably the same but could wrap
        if next_season.month < season.month or (next_season.month ==
                season.month and next_season.day < season.day):
            next_season_year += 1

        self.end_date = datetime(year=next_season_year, 
                month=next_season.month,
                day=next_season.day) - timedelta(seconds=1)

    def __repr__(self):
        return "<SeasonSlice %s: %s - %s" % (self.season.name,
                self.start_date, self.end_date)


class LeapDaySeasonBoundaryException(Exception):
    """ 
    Exception thrown if trying to create a Season with a boundary on a
    leap day. 
    """
    pass


# While we're doing all this insanity to support user defined "seasons",
# may as well leverage the same code to do monthly and yearly slices:
# TODO: I18N problem here:
MONTHLY_SEASONS = [
        Season(1, 1, "January"),
        Season(2, 1, "February"),
        Season(3, 1, "March"),
        Season(4, 1, "April"),
        Season(5, 1, "May"),
        Season(6, 1, "June"),
        Season(7, 1, "July"),
        Season(8, 1, "August"),
        Season(9, 1, "September"),
        Season(10, 1, "October"),
        Season(11, 1, "November"),
        Season(12, 1, "December")
]
YEARLY_SEASONS = [Season(1, 1, "Some Year")] # TODO: not the best name eh?
