#!/usr/bin/env python3.7
import logging
from pathlib import Path

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

    if settings.database.uri.get_secret_value().lower().startswith("sqlite"):
        try:
            path = settings.database.uri.get_secret_value().replace("sqlite:///", "")
            Path(path).chmod(0o600)
        except Exception as e:
            logging.error("Could not chmod %s", path)
