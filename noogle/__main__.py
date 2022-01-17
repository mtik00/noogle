import logging

from .cli import cli
from .logger import init_logger
from .settings import APP_LOG, DEBUG, get_settings

logfile = None
settings = get_settings()
if settings.get("general.use-logfile"):
    logfile = APP_LOG

init_logger(
    timezone=settings.get("calendar.timezone", "UTC"),
    logfile=logfile,
    logfile_mode="a",
    logfile_level=logging.DEBUG,
    debug=DEBUG,
    third_party_loggers=["googleapiclient", "oauth2client"],
)

cli()
