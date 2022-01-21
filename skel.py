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
    path = Path(".env")
    if not path.exists():
        path.write_text(
            (
                "NOOGLE_GENERAL__USE_LOGFILE=\n"
                "\n"
                "NOOGLE_NEST__STRUCTURE=\n"
                "NOOGLE_NEST__ECO_TEMPERATURE=\n"
                "NOOGLE_NEST__PRODUCT_ID=\n"
                "NOOGLE_NEST__PRODUCT_SECRET=\n"
                "NOOGLE_NEST__WINTER_HOME_MIN_TEMP=\n"
                "\n"
                "NOOGLE_CALENDAR__NAME=\n"
                "NOOGLE_CALENDAR__DEFAULT_HOME_TIME=\n"
                "NOOGLE_CALENDAR__DEFAULT_AWAY_TIME=\n"
                "NOOGLE_CALENDAR__LOOKBACK=\n"
                "NOOGLE_CALENDAR__TIMEZONE=\n"
                "\n"
                "NOOGLE_MAILGUN__API_KEY=\n"
                "NOOGLE_MAILGUN__DOMAIN_NAME=\n"
                "NOOGLE_MAILGUN__FROM_ADDRESS=\n"
                "NOOGLE_MAILGUN__TO_ADDRESS=\n"
                "\n"
                "NOOGLE_DATABASE__URI=\n"
            )
        )


def create_env_sh() -> None:
    path = Path(".secrets", "env.sh")
    if not path.exists():
        path.write_text(
            (
                "export NEST_PRODUCT_ID=\n"
                "export NEST_PRODUCT_SECRET=\n"
                "\n"
                "export MAILGUN_API_KEY=\n"
                "export MAILGUN_DOMAIN_NAME=\n"
                "export MAILGUN_FROM=\n"
                "export MAILGUN_TO="
            )
        )

        print(
            str(path), "has been created.  You must modify set the variables defined."
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


def create_config() -> None:
    config_file = Path(".secrets", "config", "noogle.ini")
    template = Path("noogle", "cli", "dev", "templates", "conf-format.ini")
    with open(template) as fh:
        template_string = fh.read()

    if config_file.exists():
        print("WARNING: Config file already exists")
        answer = input("...Are you sure you want to overwrite [Yn]? ")
        if not answer.lower().startswith("y"):
            return

    use_logfile = input("Use log file [Yn]? ").lower().startswith("y")
    print("*** Nest Setup")
    nest_structure = input("...enter the name of the Nest structure: ")
    nest_thermostat = input(
        "...enter the name of the thermostat to control (optional): "
    )
    nest_eco_temperature = input("...enter the eco temperature [50]: ") or "50"
    nest_winter_home_min_temperature = (
        input("...enter the minimum temperature to set when 'home' in winter [65]: ")
        or "65"
    )
    nest_max_hold = (
        input("...enter the maximum number of days for 'nest:home' (optional): ") or ""
    )
    print("*** Google Setup")
    gcal_calendar_id = (
        input("...enter the Calendar ID to watch [primary]: ") or "primary"
    )
    default_home_time = (
        input(
            "...enter the default start time for 'all day' _home_ events (24-hour time) [6:00]: "
        )
        or "6:00"
    )
    default_away_time = (
        input(
            "...enter the default start time for 'all day' _away_ events (24-hour time) [19:00]: "
        )
        or "19:00"
    )
    lookback = input("...enter the number of days to look back for events [2]: ") or "2"
    timezone = input("...enter the timezone of the structure [MST]: ") or "MST"

    new_config = template_string.format(
        use_logfile="True" if use_logfile else "False",
        nest_structure=nest_structure,
        nest_thermostat=nest_thermostat,
        nest_eco_temperature=nest_eco_temperature,
        nest_winter_home_min_temperature=nest_winter_home_min_temperature,
        nest_max_hold=nest_max_hold,
        gcal_calendar_id=gcal_calendar_id,
        default_home_time=default_home_time,
        default_away_time=default_away_time,
        lookback=lookback,
        timezone=timezone,
    )

    with open(config_file, "w") as fh:
        fh.write(new_config)

    print("Config file stored at:", str(config_file))


def main():
    create_folders()
    create_config()
    create_env_sh()
    create_env()
    create_logs()
    set_permissions()


if __name__ == "__main__":
    main()
