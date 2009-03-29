#!/usr/bin/env python
#
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
Standard build script.
"""

__docformat__ = 'restructuredtext'


import os
import sys

from setuptools import Command, setup
from os.path import walk


class SetupBuildCommand(Command):
    """
    Master setup build command to subclass from.
    """

    user_options = []

    def initialize_options(self):
        """
        Setup the current dir.
        """
        self._dir = os.getcwd()

    def finalize_options(self):
        """
        No clue ... but it's required.
        """
        pass


class RPMBuildCommand(SetupBuildCommand):
    """
    Creates an RPM based off spec files.
    """

    description = "Build an rpm based off of the top level spec file(s)"

    def run(self):
        """
        Run the RPMBuildCommand.
        """
        try:
            if os.system('./setup.py sdist'):
                raise Exception("Couldn't call ./setup.py sdist!")
                sys.exit(1)
            if not os.access('dist/rpms/', os.F_OK):
                os.mkdir('dist/rpms/')
            dist_path = os.path.join(os.getcwd(), 'dist')
            rpm_cmd = 'rpmbuild -ba --define "_rpmdir %s/rpms/" \
                                    --define "_srcrpmdir %s/rpms/" \
                                    --define "_sourcedir %s" *spec' % (
                      dist_path, dist_path, dist_path)
            if os.system(rpm_cmd):
                raise Exception("Could not create the rpms!")
        except Exception, ex:
            print >> sys.stderr, str(ex)


class TODOCommand(SetupBuildCommand):
    """
    Quick command to show code TODO's.
    """

    description = "prints out TODO's in the code"

    def run(self):
        """
        Prints out TODO's in the code.
        """
        import re

        format_str = "%s (%i): %s"

        # If a TODO exists, read it out
        try:
            line_no = 0
            todo_obj = open('TODO', 'r')
            for line in todo_obj.readlines():
                print format_str % ("TODO", line_no, line[:-1])
                line_no += 1
            todo_obj.close()
        except:
            pass

        remove_front_whitespace = re.compile("^[ ]*(.*)$")
        for rootdir in ['src/', 'bin/']:

            for root, dirs, files in os.walk(rootdir):
                for afile in files:
                    if afile[-4:] != '.pyc':
                        full_path = os.path.join(root, afile)
                        fobj = open(full_path, 'r')
                        line_no = 0
                        for line in fobj.readlines():
                            if 'todo' in line.lower():
                                nice_line = remove_front_whitespace.match(
                                    line).group(1)
                                print format_str % (full_path,
                                                       line_no,
                                                       nice_line)
                            line_no += 1


setup(
    name = "granola",
    version = '0.0.1',
    description = "",
    long_description = "",
    author = "Devan Goodwin",
    author_email = 'dgoodwin@dangerouslyinc.com',
    url = "http://rm-rf.ca/granola/",
    # Note released yet
    #download_url = "",
    platforms = ['any'],
    zip_safe = False,
    license = 'GPLv2+',

    package_dir = {'granola': 'src/granola'},
    packages = ['granola'],
    scripts = ['bin/granola'],
    include_package_data = True,

    install_requires = [
        'pysqlite2',
        'sqlite3',
        'sqlalchemy',
        'dateutil',
        'garmin-sync',
    ],

    classifiers = [
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Development Status :: 5 - Production/Stable',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python'],

    cmdclass = {
        'rpm': RPMBuildCommand,
        'todo': TODOCommand,
    },
)
