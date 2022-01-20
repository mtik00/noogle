import enum
from sqlalchemy import Integer, String, Column, Enum, UniqueConstraint
from sqlalchemy.sql import exists, and_
from sqlalchemy_utils import ArrowType
from sqlalchemy.exc import IntegrityError

from .db import Base, session
import arrow
from .settings import get_settings
from .utils import get_scheduled_date
from .helpers import print_log


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
    __table_args__ = (
        UniqueConstraint(
            "event_id", "scheduled_date", "calendar_id", name="event_id__date__cal__uc"
        ),
        {"sqlite_autoincrement": True},
    )

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    event_id = Column(String, nullable=False)
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
        return f"<Event {self.action}/{self.state}/{self.scheduled_date}>"

    def __repr__(self):
        return str(self)

    @staticmethod
    def waiting():
        """Return all waiting events"""
        return session.query(Event).filter(Event.state == State.waiting).all()

    @staticmethod
    def exists(event_id, scheduled_date, state=State.waiting):
        """Returns True if the event_id exists, False otherwise"""
        return session.query(
            exists().where(
                and_(
                    Event.event_id == event_id,
                    Event.scheduled_date == scheduled_date,
                    Event.state == state,
                )
            )
        ).scalar()

    @staticmethod
    def create_from_gcal(gcal_event, commit=True):
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
            print_log(f'WARNING: Cannot parse event name: "{e.name}"')

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
            e.scheduled_date = get_scheduled_date(gcal_event)

        if commit:
            try:
                session.add(e)
                session.commit()
            except IntegrityError:
                session.rollback()

        return e

    @staticmethod
    def events_missing(gcal_event_list):
        result = []

        # If there are no events returned, return all waiting events.
        if not gcal_event_list:
            return session.query(Event).filter(Event.state == State.waiting).all()

        for gcal_event in gcal_event_list:
            scheduled_date = get_scheduled_date(gcal_event)

            events = (
                session.query(Event)
                .filter(
                    and_(
                        Event.event_id == gcal_event["id"], Event.state == State.waiting
                    )
                )
                .all()
            )

            if not events:
                continue

            result += [x for x in events if x.scheduled_date != scheduled_date]

        # Ensure that future events cached in the DB show up in the list from google
        gcal_ids = [x["id"] for x in gcal_event_list]
        removed_events = (
            session.query(Event).filter(
                and_(Event.state == State.waiting, Event.event_id.notin_(gcal_ids))
            )
        ).all()
        result += removed_events

        return result

    def mark_event_missing(self):
        self.state = State.removed
        session.add(self)
        session.commit()

    def mark_event_done(self):
        self.state = State.complete
        session.add(self)
        session.commit()

    def commit(self):
        try:
            session.add(self)
            session.commit()
            return True
        except IntegrityError:
            session.rollback()
            raise
