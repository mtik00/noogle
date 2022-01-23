#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module holds the interface to the application settings.
"""
import logging
import os
from datetime import time
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, BaseSettings, DirectoryPath, FilePath, SecretStr
from pydantic.typing import StrPath


class Logging(BaseModel):
    use_logfile: Optional[bool] = False
    logfile: Optional[FilePath]
    level: int = logging.INFO


class Nest(BaseModel):
    eco_temperature: int = 50
    maximum_hold_days: int = 10
    product_id: SecretStr
    product_secret: SecretStr
    structure: str
    thermostat: Optional[str]
    winter_home_min_temp: int = 65


class Calendar(BaseModel):
    name: str = "primary"
    default_home_time: time = time(hour=9)
    default_away_time: time = time(hour=19)
    lookback: int = 2
    timezone: str = "MST"


class General(BaseModel):
    debug: bool = False
    base_config_folder: DirectoryPath
    token_folder: FilePath


class Mailgun(BaseModel):
    api_key: SecretStr
    domain_name: str
    from_address: str
    to_address: str


class Database(BaseModel):
    uri: SecretStr


class Settings(BaseSettings):
    general: General
    logging: Logging
    nest: Nest
    calendar: Calendar
    mailgun: Mailgun
    database: Database
    env_file: Optional[StrPath] = None

    def __init__(
        __pydantic_self__,
        _env_file: Optional[StrPath] = ".env",
        _env_file_encoding: Optional[str] = None,
        _env_nested_delimiter: Optional[str] = None,
        _secrets_dir: Optional[StrPath] = None,
        **values: Any,
    ) -> None:
        super().__init__(
            _env_file, _env_file_encoding, _env_nested_delimiter, _secrets_dir, **values
        )

        if __pydantic_self__.general.debug and _env_file:
            print("DEBUG: .env file loaded from", Path(_env_file).resolve())
        elif __pydantic_self__.general.debug:
            print("DEBUG: No env file loaded")

        if __pydantic_self__.general.base_config_folder:
            __pydantic_self__.general.base_config_folder = (
                __pydantic_self__.general.base_config_folder.resolve()
            )

            __pydantic_self__.general.token_folder = Path(
                __pydantic_self__.general.base_config_folder, "tokens"
            ).resolve()

    class Config:
        env_prefix = "noogle_"
        env_nested_delimiter = "__"


CUSTOM_ENV = os.environ.get("NOOGLE_ENV", ".env")
settings: Settings = Settings(_env_file=CUSTOM_ENV)
DEBUG = settings.general.debug
