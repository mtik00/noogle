#!/usr/bin/env python

import subprocess
import sys
from getpass import getuser
from pathlib import Path


def create_folders() -> None:
    if not Path(".secrets").exists():
        Path(".secrets").mkdir()

    for d in ["config", "data", "tokens", "logs"]:
        path = Path(".secrets") / d
        if not path.exists():
            print("Creating", str(path))
            path.mkdir()


def create_env() -> None:
    for path in [Path(".env"), Path(".secrets", ".env")]:
        if not path.exists():
            print("Creating", path.resolve())
            path.write_text(
                (
                    "NOOGLE_GENERAL__DEBUG=True\n"
                    "\n"
                    "NOOGLE_LOGGING__LOGFILE=\n"
                    "\n"
                    "NOOGLE_NEST__STRUCTURE=\n"
                    "NOOGLE_NEST__ECO_TEMPERATURE=50\n"
                    "NOOGLE_NEST__PRODUCT_ID=\n"
                    "NOOGLE_NEST__PRODUCT_SECRET=\n"
                    "NOOGLE_NEST__WINTER_HOME_MIN_TEMP=65\n"
                    "\n"
                    "NOOGLE_CALENDAR__NAME=primary\n"
                    "NOOGLE_CALENDAR__DEFAULT_HOME_TIME=06:00\n"
                    "NOOGLE_CALENDAR__DEFAULT_AWAY_TIME=18:00\n"
                    "NOOGLE_CALENDAR__LOOKBACK=2\n"
                    "NOOGLE_CALENDAR__TIMEZONE=\n"
                    "\n"
                    "NOOGLE_MAILGUN__API_KEY=\n"
                    "NOOGLE_MAILGUN__DOMAIN_NAME=\n"
                    "NOOGLE_MAILGUN__FROM_ADDRESS=\n"
                    "NOOGLE_MAILGUN__TO_ADDRESS=\n"
                    "\n"
                    "NOOGLE_DATABASE__URI=sqlite:////<thisdir>/.secrets/data/noogle.sqlite3\n"
                )
            )


def create_logs() -> None:
    path = Path(".secrets", "logs")
    for fname in ["gcal.log", "nest.log", "noogle.log"]:
        (path / fname).touch()


def set_permissions() -> None:

    if sys.platform == "linux":
        user = getuser()
        cmd = ["sudo", "chown", "-R", f"{user}:{user}", ".secrets"]
        subprocess.check_output(cmd, stdin=subprocess.PIPE)

    for file in Path(".secrets", "logs").glob("*.log"):
        file.chmod(0o600)

    for file in Path(".secrets", "tokens").glob("*.json"):
        file.chmod(0o600)

    for file in Path(".secrets", "data").glob("*"):
        file.chmod(0o600)

    for file in Path(".secrets").glob("*"):
        file.chmod(0o600)


def main():
    create_folders()
    create_env()
    create_logs()
    set_permissions()


if __name__ == "__main__":
    main()
