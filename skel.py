#!/usr/bin/env python
import os
import shutil
from getpass import getuser
from pathlib import Path


def create_folders() -> None:
    secrets = Path(".secrets")

    if not secrets.exists():
        secrets.mkdir(parents=True)

    secrets.chmod(0o700)

    for d in ["config", "data", "tokens", "logs"]:
        path = secrets / d
        if not path.exists():
            print("Creating", str(path))
            path.mkdir()
            path.chmod(0o700)


def create_env() -> None:
    template = Path("noogle", "cli", "dev", "templates", ".env").read_text()
    db_path = Path(".secrets", "data", "noogle.sqlite3").resolve()
    calendar_token_file = Path(
        ".secrets", "tokens", "calendar-oauth-client-secret.json"
    ).resolve()
    nest_token_file = Path(
        ".secrets", "tokens", "nest-oauth-client-secret.json"
    ).resolve()
    for path in [Path(".env"), Path(".secrets", ".env")]:
        if not path.exists():
            print("Creating", path.resolve())
            path.write_text(
                template.format(
                    db_path=db_path,
                    calendar_token_file=calendar_token_file,
                    nest_token_file=nest_token_file,
                )
            )


def create_logs() -> None:
    path = Path(".secrets", "logs")
    for fname in ["noogle.log"]:
        (path / fname).touch()


def set_permissions() -> None:
    user_group = getuser()

    base = Path(".secrets")
    base.chmod(0o700)
    shutil.chown(base, user_group, user_group)

    for root, dirs, files in os.walk(base, topdown=False):
        for name in files:
            f = Path(root, name)
            f.chmod(0o600)
            shutil.chown(f, user_group, user_group)

        for name in dirs:
            d = Path(root, name)
            d.chmod(0o700)
            shutil.chown(d, user_group, user_group)


def main():
    create_folders()
    create_env()
    create_logs()
    set_permissions()


if __name__ == "__main__":
    main()
