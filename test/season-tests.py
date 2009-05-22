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

""" Tests for Granola's season module. """

import unittest

from datetime import datetime

from granola.season import *

PRE_SEASON_NAME = "Pre Season"
PRIME_SEASON_NAME = "Prime Season"
POST_SEASON_NAME = "Post Season"
OFF_SEASON_NAME = "Off Season"

class SeasonTests(unittest.TestCase):
    def setUp(self):
        self.pre = Season(5, 1, PRE_SEASON_NAME)
        self.prime = Season(7, 1, PRIME_SEASON_NAME)
        self.post = Season(10, 1, POST_SEASON_NAME)
        self.off = Season(11, 1, OFF_SEASON_NAME)
        self.seasons = [self.pre, self.prime, self.post, self.off]

    def testFindSeason(self):
        activity_date = datetime(2009, 5, 2, 12, 37, 25)
        season_slice = find_season(activity_date, self.seasons)
        self.assertEquals(self.pre, season_slice.season)
        
    def testFindSeason2(self):
        activity_date = datetime(2009, 11, 1, 0, 0, 0)
        season_slice = find_season(activity_date, self.seasons)
        self.assertEquals(self.off, season_slice.season)
        
    def testFindSeason3(self):
        activity_date = datetime(2009, 1, 5, 0, 0, 0)
        season_slice = find_season(activity_date, self.seasons)
        self.assertEquals(self.off, season_slice.season)
        self.assertEquals(2008, season_slice.start_date.year)
        self.assertEquals(2009, season_slice.end_date.year)

    def test_build_all_seasons(self):
        first_activity_date = datetime(2009, 5, 20, 14, 0, 0)
        last_activity_date = datetime(2012, 12, 15, 4, 0, 0)
        season_slice = find_season(first_activity_date, self.seasons)
        all_slices = build_all_slices(self.seasons, season_slice,
                last_activity_date)

    def test_monthly_seasons(self):
        first_activity_date = datetime(2008, 12, 26, 15, 30)
        last_activity_date = datetime(2009, 02, 22, 17, 0)
        season_slice = find_season(first_activity_date, MONTHLY_SEASONS)
        all_slices = build_all_slices(MONTHLY_SEASONS, season_slice, 
                last_activity_date)
        self.assertEquals(3, len(all_slices))
        self.assertEquals("December", all_slices[0].season.name)
        self.assertEquals("January", all_slices[1].season.name)
        self.assertEquals("February", all_slices[2].season.name)
        self.assertEquals(2008, all_slices[0].start_date.year)
        self.assertEquals(2009, all_slices[1].start_date.year)
        self.assertEquals(2009, all_slices[2].start_date.year)


        




