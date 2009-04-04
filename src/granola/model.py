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

import os.path

from granola.log import log
from granola.const import DATA_DIR, VERSION

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, \
        String, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import mapper, relation, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLITE_DB = "%s/granola.db" % DATA_DIR

SPORTNAME_RUNNING = "running"
SPORTNAME_BIKING = "biking"
SPORTNAME_WALKING = "walking"
SPORTNAME_OTHER = "other"


def connect_to_db():
    """
    Open a connection to our database.

    Should be called only once when this module is first imported.
    """
    db_str = "sqlite:///%s" % SQLITE_DB
    log.debug("Connecting to database: %s" % db_str)

    # Set echo True to see lots of sqlalchemy output:
    db = create_engine(db_str, echo=False)

    return db


Base = declarative_base()
Session = sessionmaker()
# Open a globally accessible connection to the database:
DB = connect_to_db()
Session.configure(bind=DB)


class Sport(Base):

    __tablename__ = "sport"

    id = Column(Integer, primary_key=True)
    name = Column(String(40))

    def __init__(self, name=None):
        self.name = name

    def __repr__(self):
        return self.name


class TrackPoint(Base):

    __tablename__ = "trackpoint"

    id = Column(Integer, primary_key=True)
    lap_id = Column(Integer, ForeignKey('lap.id'))
    time = Column(DateTime(timezone=True))
    latitude = Column(Numeric(9, 6))
    longitude = Column(Numeric(9, 6))
    altitude = Column(Numeric(12, 6))
    distance = Column(Numeric(12, 6))
    heart_rate = Column(Integer)

    def __init__(self, time=None, latitude=None, longitude=None, 
            altitude=None, distance=None, heart_rate=None):
        self.time = time
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.distance = distance
        self.heart_rate = heart_rate


class Lap(Base):

    __tablename__ = "lap"

    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, ForeignKey('activity.id'))
    start_time = Column(DateTime(timezone=True))
    duration = Column(Numeric(14, 6)) # seconds
    distance = Column(Numeric(20, 6)) # meters
    speed_max = Column(Numeric(9, 6)) # meters per second
    calories = Column(Integer)
    heart_rate_max = Column(Integer) # beats per minute
    heart_rate_avg = Column(Integer) # beats per minute

    trackpoints = relation(TrackPoint, cascade="all")

    def __init__(self, start_time=None, duration=None, distance=None,
            speed_max=None, calories=None, heart_rate_max=None,
            heart_rate_avg=None):
        self.start_time = start_time
        self.duration = duration
        self.distance = distance
        self.speed_max = speed_max
        self.calories = calories
        self.heart_rate_max = heart_rate_max
        self.heart_rate_avg = heart_rate_avg

    def __repr__(self):
        return "Lap - %s" % self.start_time


class Activity(Base):

    __tablename__ = "activity"

    id = Column(Integer, primary_key=True)
    # Might want to drop this and just use the start time of the first lap:
    start_time = Column(DateTime(timezone=True), nullable=False, unique=True)
    sport_id = Column(Integer, ForeignKey('sport.id'), nullable=False)

    sport = relation(Sport)
    laps = relation(Lap, cascade="all", backref='activity')

    def __init__(self, start_time=None, sport=None):
        self.start_time = start_time
        self.sport = sport

    def __repr__(self):
        return "Activity<%s - %s>" % \
                (self.id, self.start_time)

    # TODO: All these properties are probably not the best performance wise:

    def _get_distance(self):
        distance = None
        for lap in self.laps:
            if distance == None:
                distance = lap.distance
            else:
                distance += lap.distance
        return distance
    distance = property(_get_distance, None)

    def _get_duration(self):
        duration = None
        for lap in self.laps:
            if duration == None:
                duration = lap.duration
            else:
                duration += lap.duration
        return duration
    duration = property(_get_duration, None)

    def _get_heart_rate_avg(self):
        beats = 0
        for lap in self.laps:
            if lap.heart_rate_avg is None:
                return None
            beats = beats + (lap.heart_rate_avg * (lap.duration / 60))
        return beats / (self.duration / 60)
    heart_rate_avg = property(_get_heart_rate_avg, None)


class Constant(Base):
    """ Store random string constants in the database. """

    __tablename__ = "constant"

    name = Column(String(256), primary_key=True, unique=True)
    value = Column(String(256))

    def __init__(self, name=None, value=None):
        self.name = name
        self.value = value


class Import(Base):
    """
    Items we've automatically imported. Identified by a type and a string.

    TODO: May want to push this to the db if the types expand at all.
    1 = file
    """
    __tablename__ = "import"

    id = Column(Integer, primary_key=True)

    # Type of the auto-import, 1 = file for now.
    import_type = Column(Integer)

    # Some kind of identifier for what was imported, typically a filename.
    identifier = Column(String(256))

    def __init__(self, import_type, identifier):
        self.import_type = import_type
        self.identifier = identifier


def initialize_db():
    """
    Open the database, presumably for the first time, and populate the schema.

    Returns the database engine.
    """
    log.info("Creating the granola database.")

    metadata = Base.metadata
    metadata.bind = DB
    metadata.create_all()

    session = Session()

    # Populate the schema:
    session.add_all([
        Sport(SPORTNAME_RUNNING),
        Sport(SPORTNAME_BIKING),
        Sport(SPORTNAME_WALKING),
        Sport(SPORTNAME_OTHER),
    ])
    session.add_all([
        Constant("schema_version", VERSION),
    ])
    session.commit()
