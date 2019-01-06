#!/usr/bin/env python3.7
import os

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .settings import INSTANCE_FOLDER

db_path = os.path.join(INSTANCE_FOLDER, "noogle.db")

engine = create_engine(f"sqlite:///{db_path}")
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


def init():
    from .models import Event

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
