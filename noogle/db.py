#!/usr/bin/env python3.7
import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import sessionmaker

from .settings import DATA_FOLDER

db_path = os.path.join(DATA_FOLDER, "noogle.sqlite3")

engine = create_engine(f"sqlite:///{db_path}")
Base: DeclarativeMeta = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


def init():
    from .models import Event  # noqa

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
