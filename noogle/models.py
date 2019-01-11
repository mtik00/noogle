import enum
from sqlalchemy import Integer, String, Column, Enum
from sqlalchemy.sql import exists
from sqlalchemy_utils import ArrowType
from .db import Base, session
import arrow
from .settings import get_settings


class State(enum.Enum):
    waiting = 0
    complete = 1
    removed = 2

    def __str__(self):
        return self.name


class Action(enum.Enum):
    home = 0
    away = 1
    eco = 2
    heat = 3

    def __str__(self):
        return self.name


class Event(Base):
    """Describes a single event stored in cache."""

    __tablename__ = "events"

    event_id = Column(String, primary_key=True)
    name = Column(String, nullable=True)
    action = Column(Enum(Action), nullable=False)
    calendar_id = Column(String, default="primary")
    parent_event_id = Column(Integer, nullable=True)
    state = Column(Enum(State), nullable=False, default=State.waiting)
    scheduled_date = Column(ArrowType, nullable=True)
    actioned_date = Column(ArrowType, nullable=True)
    description = Column(String, nullable=True)
    structure_name = Column(String, default="", nullable=False)
    structure_id = Column(String, default="", nullable=False)

    def __str__(self):
        return f"<Event {self.action}/{self.state}/{self.scheduled_date}"

    def __repr__(self):
        return str(self)

    @classmethod
    def waiting(cls):
        """Return all waiting events"""
        return session.query(Event).filter(Event.state == State.waiting).all()

    @classmethod
    def exists(cls, event_id):
        """Returns True if the event_id exists, False otherwise"""
        return session.query(exists().where(Event.event_id == event_id)).scalar()

    @classmethod
    def create_from_gcal(cls, gcal_event):
        e = Event(
            name=gcal_event["summary"], event_id=gcal_event["id"], state=State.waiting
        )

        e.actioned_date = None

        parts = e.name.split(":")
        if len(parts) == 2:
            e.action = Action[parts[1].strip()]
        elif len(parts) == 3:
            e.action = Action[parts[1].strip()]
            e.description = parts[2].strip()
        else:
            print(f'WARNING: Cannot parse event name: "{e.name}"')

        if "date" in gcal_event["start"]:
            # The user has an "all day" event in gcal.
            default_time = (
                get_settings().get("calendar.default-home-time")
                if e.action.value == Action.home
                else get_settings().get("calendar.default-away-time")
            )
            e.scheduled_date = arrow.get(
                gcal_event["start"]["date"]
                + " "
                + default_time
                + " "
                + get_settings().get("calendar.timezone", "MST"),
                "YYYY-MM-DD H:mm ZZZ",
            )
        else:
            # NOTE: 'dateTime' includes the timezone
            e.scheduled_date = arrow.get(gcal_event["start"].get("dateTime"))

        session.add(e)
        session.commit()

    def mark_event_missing(self):
        self.state = State.removed
        session.add(self)
        session.commit()

    def mark_event_done(self):
        self.state = State.complete
        session.add(self)
        session.commit()
