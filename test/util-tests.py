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

""" Tests for Granola's util module. """

import unittest

from granola.util import *
from decimal import Decimal, ROUND_UP

class UtilTests(unittest.TestCase):

    def test_calculate_speed(self):
        self.assertEquals(Decimal(100), calculate_speed(None, Decimal(100000), 
            Decimal(3600)))
        self.assertEquals(Decimal('8.4'), calculate_speed(None, Decimal(2540), 
            Decimal(1086)).quantize(Decimal('.1')))


