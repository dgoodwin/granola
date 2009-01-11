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

from granola.log import log
from granola.const import DATA_DIR

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, \
        String, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import mapper, relation, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLITE_DB = "%s/granola.db" % DATA_DIR

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

    activity_id = Column(Integer, ForeignKey('activity.id'))
    trackpoints = relation(TrackPoint)



class Activity(Base):

    __tablename__ = "activity"

    id = Column(Integer, primary_key=True)
    # Might want to drop this and just use the start time of the first lap:
    start_time = Column(DateTime(timezone=True), nullable=False, unique=True)
    sport_id = Column(Integer, ForeignKey('sport.id'), nullable=False)

    sport = relation(Sport)
    laps = relation(Lap)

    def __init__(self, start_time=None, sport=None):
        self.start_time = start_time
        self.sport = sport



# TODO: Add settings table, store the schema version in it.

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
        Sport("Running"),
        Sport("Biking"),
        Sport("Hiking"),
        Sport("Other"),
    ])
    session.commit()

