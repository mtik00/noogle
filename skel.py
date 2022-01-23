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
            path.chmod(0o700)


def create_env() -> None:
    template = Path("noogle", "cli", "dev", "templates", ".env").read_text()
    db_path = Path(".secrets", "data", "noogle.sqlite3").resolve()
    for path in [Path(".env"), Path(".secrets", ".env")]:
        if not path.exists():
            print("Creating", path.resolve())
            path.write_text(template.format(db_path=db_path))


def create_logs() -> None:
    path = Path(".secrets", "logs")
    for fname in ["noogle.log"]:
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

    for file in Path(".secrets").glob(".env"):
        file.chmod(0o600)


def main():
    create_folders()
    create_env()
    create_logs()
    set_permissions()


if __name__ == "__main__":
    main()
