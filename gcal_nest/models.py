import enum
from sqlalchemy import Integer, String, Column, Enum
from sqlalchemy_utils import ArrowType
from .db import Base


class State(enum.Enum):
    waiting = 0
    complete = 1
    removed = 2

    def __str__(self):
        return self.name


class Action(enum.Enum):
    home = 0
    away = 1

    def __str__(self):
        return self.name


class Event(Base):
    '''Describes a single event stored in cache.'''
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    action = Column(Enum(Action), nullable=False)
    event_id = Column(Integer)
    calendar_id = Column(String, default='primary')
    parent_event_id = Column(Integer)
    state = Column(Enum(State), nullable=False, default=State.waiting)
    scheduled_date = Column(ArrowType)
    actioned_date = Column(ArrowType)
    timezone = Column(String)
    description = Column(String, nullable=True)
