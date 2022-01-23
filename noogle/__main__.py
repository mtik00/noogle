import logging

from .cli import cli
from .logger import init_logger
from .settings import settings

logfile = settings.logging.logfile

init_logger(
    timezone=settings.calendar.timezone,
    logfile=logfile,
    logfile_mode="a",
    logfile_level=logging.DEBUG,
    debug=settings.general.debug,
    third_party_loggers=["googleapiclient", "oauth2client"],
)

cli()
