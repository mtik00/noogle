#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module has the class used to control the Nest thermostat.
"""

# Imports #####################################################################
import json
import logging
import operator
import re
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

import requests

from .db import session
from .google_auth import get_credentials
from .helpers import print_log
from .models import Action
from .models import Structure as StructureModel
from .models import Thermostat as ThermostatModel
from .settings import settings
from .utils import celsius_to_fahrenheit, fahrenheit_to_celsius, is_winter

# Metadata ####################################################################
__author__ = "Timothy McFadden"
__creationDate__ = "07-JUN-2017"


# Globals #####################################################################
class APIError(Exception):
    """
    Exception if something went wrong in the API
    """

    def __init__(self, response):
        super().__init__()
        self.response = response

    def __str__(self):
        return self.response.text

    def __repr__(self):
        return f"<API Error: {self.response.text}"


class Unauthorized(APIError):
    def __repr__(self):
        return f"<Unauthorized: {self.response.text}"


class RateLimitExceeded(APIError):
    def __repr__(self):
        return f"<RateLimitExceeded: {self.response.text}"


@dataclass(frozen=False)
class ThermostatInDB:
    name: str
    label: str
    structure_name: str


@dataclass(frozen=True)
class Thermostat:
    name: str
    label: str
    structure_name: str
    mode: str
    eco: str
    setpoint_c: float


@dataclass(frozen=True)
class Structure:
    name: str
    custom_name: str


class NestAPI:
    base_api_url = "https://smartdevicemanagement.googleapis.com/v1/"
    verification_wait = 30

    def __init__(self, load=True):
        creds = get_credentials(name="nest", oauth_token=settings.nest.token_file)
        self.token = creds.token

        self.thermostats: Dict[str, Thermostat] = {}
        self.structures: Dict[str, Structure] = {}

        self.__loaded = False

        if load:
            self.load()

    def _format_url(self, partial: str):
        return f"{NestAPI.base_api_url}{partial}"

    def _get_token(self):
        creds = get_credentials(name="nest", oauth_token=settings.nest.token_file)
        self.token = creds.token

    def _get_structures_from_db(self):
        structures = {}
        for structure in session.query(StructureModel).all():
            structures[structure.name] = Structure(
                name=structure.name, custom_name=structure.custom_name
            )
        return structures

    def _get_structures_from_api(self) -> Dict[str, Structure]:
        logging.info("Reading structures from the Nest API")
        structures = {}

        data = self.request(
            "get",
            url=self._format_url(
                f"enterprises/{settings.nest.product_id.get_secret_value()}/structures"
            ),
        )
        for item in data["structures"]:
            name = item["name"]
            custom_name = (
                item.get("traits", {})
                .get("sdm.structures.traits.Info", {})
                .get("customName")
                or ""
            )
            structure = Structure(
                name=name,
                custom_name=custom_name,
            )
            model = StructureModel(name=name, custom_name=custom_name)
            session.add(model)

            structures[name] = structure

        session.commit()
        return structures

    def _get_thermostats_from_db(self):
        thermostats = {}
        for thermostat in session.query(ThermostatModel).all():
            thermostats[thermostat.name] = ThermostatInDB(
                name=thermostat.name,
                label=thermostat.label,
                structure_name=thermostat.structure_name,
            )
        return thermostats

    def _get_thermostats_from_api(self):
        thermostats = {}
        data = self.request(
            "get",
            url=self._format_url(
                f"enterprises/{settings.nest.product_id.get_secret_value()}/devices"
            ),
        )
        for item in data["devices"]:
            name = item["name"]
            label = (
                item.get("traits", {})
                .get("sdm.devices.traits.Info", {})
                .get("customName")
            ) or ""

            if not label:
                raise ValueError("No custom label set for thermostat")
            elif label in thermostats:
                raise ValueError(f"Multiple thermostats found labeled: '{label}'")

            mode = item["traits"]["sdm.devices.traits.ThermostatMode"]["mode"]
            eco = item["traits"]["sdm.devices.traits.ThermostatEco"]["mode"]
            setpoint_c = (
                item["traits"]["sdm.devices.traits.ThermostatTemperatureSetpoint"].get(
                    "heatCelsius"
                )
                or 0.0
            )

            parent_id = item["parentRelations"][0]["parent"]
            structure_name = re.search(
                "(?P<structure>.*/structures/.*?)/room", parent_id
            ).group(1)

            thermostats[label] = Thermostat(
                name=name,
                label=label,
                mode=mode,
                eco=eco,
                setpoint_c=setpoint_c,
                structure_name=structure_name,
            )

            if (
                not session.query(ThermostatModel)
                .filter_by(name=name, structure_name=structure_name)
                .count()
            ):
                thermostat = ThermostatModel(
                    name=name, label=label, structure_name=structure_name
                )
                session.add(thermostat)

        session.commit()
        return thermostats

    def load(self, force=False):
        """
        Reads the data structures from the API.
        """
        if self.__loaded and not force:
            return

        self.__loaded = False

        self.structures = self._get_structures_from_db()
        if not self.structures:
            self.structures = self._get_structures_from_api()
        logging.debug("found %s structures", len(self.structures))

        self.thermostats = self._get_thermostats_from_api()
        logging.debug("found %s thermostats", len(self.thermostats))

        self.__loaded = True

    def _get_structure_by_name(self, custom_name):
        model = (
            session.query(StructureModel)
            .filter(StructureModel.custom_name.ilike(custom_name))
            .first()
        )

        if not model:
            raise ValueError(
                f"Can't find structure with a custom_name of {custom_name}"
            )

        return self.structures[model.name]

    def _get_structure_thermostats(self, structure: Structure) -> List[Thermostat]:
        thermostats = [
            x for x in self.thermostats.values() if x.structure_name == structure.name
        ]

        if not thermostats:
            raise ValueError(
                f"Can't find any thermostats in structure: {structure.custom_name}"
            )

        return thermostats

    def request(
        self,
        method: str,
        url: str,
        payload: Optional[dict] = None,
        request_auth: bool = True,
    ):
        if method.lower() not in ["get", "put", "post", "head"]:
            raise ValueError(f"Unsupported method: {method}")

        try:
            return self._request(method=method, url=url, payload=payload)
        except Unauthorized:
            if request_auth:
                self._get_token()
                return self._request(method=method, url=url, payload=payload)
            else:
                raise

    def _request(
        self, method: str, url: str, payload: Optional[dict] = None, wait: float = 10.0
    ):
        auth = "Bearer ".encode("ascii") + self.token.encode("ascii", "ignore")
        headers = {"authorization": auth, "content-type": "application/json"}

        if payload and not isinstance(payload, dict):
            raise TypeError(f"Type of payload must be dict; was: {type(payload)}")
        elif payload:
            payload = json.dumps(payload)

        response = requests.request(
            method, url=url, headers=headers, data=payload, allow_redirects=False
        )

        if response.status_code == 307:  # indicates a redirect is needed
            response = requests.request(
                method=method,
                url=response.headers["Location"],
                headers=headers,
                data=payload,
                allow_redirects=False,
            )

        if response.status_code == 401:
            raise Unauthorized(response)
        elif response.status_code == 429:
            raise RateLimitExceeded(response)
        elif response.status_code >= 400:
            raise APIError(response)

        response.raise_for_status()

        time.sleep(wait)
        return response.json()

    def show(self):
        """
        Displays some information about the structure and thermostat using
        the NestAPI.
        """
        self.load()

        for label, thermostat in self.thermostats.items():
            print(label)
            print("    ID:", thermostat.name)
            print("    Mode:", thermostat.mode)
            print("    ECO:", thermostat.eco)
            print(
                "    Setpoint:",
                "N/A"
                if thermostat.eco == "MANUAL_ECO"
                else int(celsius_to_fahrenheit(thermostat.setpoint_c)),
            )

    def set_temperature(self, structure, temp_f: int, comparison=operator.ne):
        temp_c = round(fahrenheit_to_celsius(temp_f), 0)

        thermostats = self._get_structure_thermostats(structure)
        bad_thermostats = [t for t in thermostats if comparison(t.setpoint_c, temp_c)]

        for thermostat in bad_thermostats:
            payload = {
                "command": "sdm.devices.commands.ThermostatTemperatureSetpoint.SetHeat",
                "params": {"heatCelsius": temp_c},
            }
            url = self._format_url(f"{thermostat.name}:executeCommand")
            self.request("post", url, payload)

    def set_eco(
        self, structure: Structure, mode: str = "MANUAL_ECO", force: bool = False
    ):
        if mode.upper() not in ["OFF", "MANUAL_ECO"]:
            raise ValueError(f"Unsupported hvac mode: {mode}")

        thermostats = self._get_structure_thermostats(structure)
        modes = [mode] * len(thermostats)

        t_map = {t: mode for t in thermostats for mode in modes}

        bad_thermostats = {
            thermostat: mode
            for thermostat, mode in t_map.items()
            if thermostat.eco != mode
        }

        if not (bad_thermostats or force):
            return

        if not bad_thermostats:
            bad_thermostats = t_map

        for t, mode in bad_thermostats.items():
            payload = {
                "command": "sdm.devices.commands.ThermostatEco.SetMode",
                "params": {"mode": mode},
            }
            url = self._format_url(f"{t.name}:executeCommand")
            self.request("post", url, payload)

    def set_hvac_mode(self, structure: Structure, hvac_mode: str, force: bool = False):
        """
        Sets the Thermostat mode for all thermostats in a structure.  The only
        supported values are:
            - HEAT
            - COOL
            - HEATCOOL
        """
        if hvac_mode.upper() not in ["HEAT", "COOL", "HEATCOOL"]:
            raise ValueError(f"Unsupported hvac mode: {hvac_mode}")

        thermostats = self._get_structure_thermostats(structure)

        modes = [hvac_mode] * len(thermostats)

        t_map = {t: mode for t in thermostats for mode in modes}

        bad_thermostats = {
            thermostat: mode
            for thermostat, mode in t_map.items()
            if thermostat.mode != mode
        }

        if not (bad_thermostats or force):
            return

        if not bad_thermostats:
            bad_thermostats = t_map

        for t, mode in bad_thermostats.items():
            payload = {
                "command": "sdm.devices.commands.ThermostatMode.SetMode",
                "params": {"mode": mode},
            }
            url = self._format_url(f"{t.name}:executeCommand")
            self.request("post", url, payload)

    def do_away(self):
        """
        Sets up the thermostat in eco mode.
        """
        self.load()

        structure_name = settings.nest.structure.lower()
        structure = self._get_structure_by_name(structure_name)

        if not structure:
            raise ValueError(f"Could not find structure in API: {structure_name}")

        self.set_eco(structure, "MANUAL_ECO")

    def do_home(self):
        """
        Sets up the thermostat in *home* mode.
        """
        self.load()

        structure_name = settings.nest.structure
        structure = self._get_structure_by_name(structure_name)

        if not structure:
            raise ValueError(f"Could not find structure in API: {structure_name}")

        if is_winter():
            temp_f = settings.nest.winter_home_min_temp

            self.set_eco(structure, mode="OFF")
            self.set_hvac_mode(structure, "HEAT")
            self.set_temperature(structure, temp_f, comparison=operator.lt)
        else:
            self.set_hvac_mode(structure, "HEATCOOL")

    def verify(self, action, force_load=True):
        """
        Verify the action actually occurred.
        """
        errors = []

        self.load(force=force_load)
        structure_name = settings.nest.structure.lower()
        structure = self._get_structure_by_name(structure_name)

        # TODO: This should be variable
        if action.value == Action.home.value:
            mode = "HEAT"
            eco = "OFF"
        else:
            mode = "HEAT"
            eco = "MANUAL_ECO"

        bad_thermostats = [
            x
            for x in self._get_structure_thermostats(structure)
            if (x.mode != mode) or (x.eco != eco)
        ]
        if bad_thermostats:
            errors.append(f"Thermostat mode is not set to {mode} and/or eco {eco}!")

        if errors:
            message = "\n".join(errors)
            raise Exception(message)

    def change_needed(self, action):
        """
        Returns `True` if the current state does not match the requested
        action.
        """
        try:
            self.verify(action, force_load=False)
            return False
        except Exception:
            return True

    def do_action(self, action):
        if not self.change_needed(action):
            print_log("No action needed")
            return

        action_map = {Action.away.value: self.do_away, Action.home.value: self.do_home}

        func = action_map.get(action.value, None)
        if func:
            func()

            print_log(f"...waiting {NestAPI.verification_wait}s before verification")
            time.sleep(NestAPI.verification_wait)

            self.verify(action)
        else:
            raise Exception("Unknown action: {!r}".format(action))

        print_log("...OK")


def purge_db():
    """Removes Structures and Thermostats from the database"""
    session.query(ThermostatModel).delete()
    session.query(StructureModel).delete()
    session.commit()
