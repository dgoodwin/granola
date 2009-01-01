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

from logging import getLogger
log = getLogger("granola.model")

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, \
        String, ForeignKey
from sqlalchemy.orm import mapper, relation
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Sport(Base):
    __tablename__ = "sport"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(40))

    def __init__(self, name=None):
        self.name = name



class Activity(Base):
    __tablename__ = "activity"

    id = Column(Integer, primary_key=True)
    date_id = Column(String(30)) # may not be needed
    sport_id = Column(Integer, ForeignKey('sport.id'))
    sport = relation(Sport)

    def __init__(self, date_id=None, sport_id=None):
        self.date_id = date_id
        self.sport_id = sport_id




def initialize_db(sqlite_db):
    """
    Open the database, presumably for the first time, and populate the schema. 
    """
    log.info("Creating the granola database.")
    db_str = "sqlite:///%s" % sqlite_db
    db = create_engine(db_str, echo=True)

    metadata = Base.metadata
    metadata.bind = db
    metadata.create_all()

