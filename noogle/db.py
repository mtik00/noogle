#!/usr/bin/env python3.7


from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import sessionmaker

from .settings import settings

engine = create_engine(settings.database.uri.get_secret_value())
Base: DeclarativeMeta = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


def init():
    from .models import Event  # noqa

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
