#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module has the class used to control the Nest thermostat.
"""

# Imports #####################################################################
import json
import logging
import operator
import os
import re
import time
from dataclasses import dataclass
from typing import Dict, List

import requests

from .google_auth import get_credentials
from .helpers import print_log
from .models import Action
from .settings import settings
from .utils import is_winter

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


@dataclass(frozen=True)
class Thermostat:
    device_id: str
    label: str
    mode: str
    eco: str
    setpoint_c: float
    structure_id: str
    parent_id: str


class NestAPI:
    base_api_url = f"https://smartdevicemanagement.googleapis.com/v1/enterprises/{settings.nest.product_id.get_secret_value()}"
    verification_wait = 10

    def __init__(self, load=True):
        creds = get_credentials()
        self.token = creds.token

        self.thermostats: Dict[str, Thermostat] = {}

        self.__loaded = False

        if load:
            self.load()

    def _get_token(self):
        creds = get_credentials()
        self.token = creds.token

    def load(self, force=False):
        """
        Reads the data structures from the API.
        """
        if self.__loaded and not force:
            return

        self.__loaded = False

        self.thermostats = {}
        data = self.get(url="/devices")
        for item in data["devices"]:
            logging.debug(item)
            device_id = item["name"].replace(
                f"enterprises/{settings.nest.product_id.get_secret_value()}/devices/",
                "",
            )
            label = (
                item.get("traits", {})
                .get("sdm.devices.traits.Info", {})
                .get("customName")
            ) or ""

            if not label:
                raise ValueError("No custom label set for thermostat")
            elif label in self.thermostats:
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
            structure_id = re.search(
                ".*?(?P<structure>structures/.*?)/", parent_id
            ).group(1)

            self.thermostats[label] = Thermostat(
                device_id=device_id,
                label=label,
                mode=mode,
                eco=eco,
                setpoint_c=setpoint_c,
                structure_id=structure_id,
                parent_id=parent_id,
            )

        self.__loaded = True

    def _get_thermostat(self, label):
        return self.thermostats.get(label)

    def get(self, url="/", request_auth=True):
        """
        Perform a `get` on the API.  This method will attempt to get a new
        access token if needed.  This requires user interaction.
        """
        try:
            return self._get(url)
        except Unauthorized:
            if request_auth:
                self._get_token()
                return self._get(url)
            else:
                raise

    def _get(self, url="/", wait: float = 2.0):
        """
        Use the token to request the provided URL.
        """
        auth = "Bearer ".encode("ascii") + self.token.encode("ascii", "ignore")
        headers = {"authorization": auth, "content-type": "application/json"}

        response = requests.get(
            f"{NestAPI.base_api_url}{url}", headers=headers, allow_redirects=False
        )

        if response.status_code == 307:
            response = requests.get(
                response.headers["Location"], headers=headers, allow_redirects=False
            )

        if response.status_code == 401:
            raise Unauthorized(response)
        elif response.status_code == 429:
            raise RateLimitExceeded(response)

        time.sleep(wait)
        return response.json()

    def put(self, url, payload, request_auth=True):
        """
        Perform a `put` on the API.  This method will attempt to get a new
        access token if needed.  This requires user interaction.
        """
        try:
            return self._put(url, payload)
        except Unauthorized:
            if request_auth:
                self._get_token()
                return self._put(url, payload, request_auth=False)
            else:
                raise

    def _put(self, url, payload, wait: float = 2.0):
        """
        Use the token to `put` the payload to the provided URL.
        """
        auth = "Bearer ".encode("ascii") + self.token.encode("ascii", "ignore")
        headers = {"authorization": auth, "content-type": "application/json"}

        if not isinstance(payload, str):
            payload = json.dumps(payload)

        response = requests.put(
            f"{NestAPI.base_api_url}{url}",
            headers=headers,
            data=payload,
            allow_redirects=False,
        )

        if response.status_code == 307:  # indicates a redirect is needed
            response = requests.put(
                response.headers["Location"],
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
            print("    ID:", thermostat.device_id)
            print("    Mode:", thermostat.mode)
            print("    ECO:", thermostat.eco)
            print(
                "    Setpoint:",
                "N/A" if thermostat.eco == "MANUAL_ECO" else thermostat.setpoint_c,
            )

    def set_away(self, structure, away="away", force=False):
        """
        Sets the `away` mode for the structure.
        """
        if (structure.away == away) and (not force):
            return

        payload = {"away": away}
        url = f"/structures/{structure.structure_id}"
        return self.put(url, payload)

    def set_temperature(self, structure, temp_f: int, comparison=operator.ne):

        thermostats = self._get_structure_thermostats(structure)
        bad_thermostats = [
            t for t in thermostats if comparison(t.target_temperature_f, temp_f)
        ]

        for thermostat in bad_thermostats:
            payload = {"target_temperature_f": temp_f}
            url = f"/devices/thermostats/{thermostat.device_id}"
            self.put(url, payload)

    def set_hvac_mode(self, structure, hvac_mode, force=False):
        """
        Sets the HVAC mode for all thermostats in a structure.
        """
        thermostats = self._get_structure_thermostats(structure)

        if hvac_mode == "__previous_hvac_mode__":
            modes = [x.previous_hvac_mode for x in thermostats]
        else:
            modes = [hvac_mode] * len(thermostats)

        t_map = {t: mode for t in thermostats for mode in modes}

        bad_thermostats = {
            thermostat: mode
            for thermostat, mode in t_map.items()
            if thermostat.hvac_mode != mode
        }

        if not (bad_thermostats or force):
            return

        if not bad_thermostats:
            bad_thermostats = t_map

        for t, mode in bad_thermostats.items():
            payload = {"hvac_mode": mode}
            url = f"/devices/thermostats/{t.device_id}"
            self.put(url, payload)

    def do_away(self):
        """
        Sets up the structure and thermostat in *away* mode.

        1.  Sets the structure to `away`
        2.  Sets the `hvac_mode` to `eco`
        """
        self.load()

        structure_name = settings.nest.structure.lower()
        structure = self._get_structure_by_name(structure_name)

        if not structure:
            raise ValueError(f"Could not find structure in API: {structure_name}")

        self.set_away(structure, "away")
        self.set_hvac_mode(structure, "eco")

    def do_home(self):
        """
        Sets up the structure and thermostat in *home* mode.

        1.  Sets the structure to `home`
        2.  Sets the `hvac_mode` to `heat`
        """
        self.load()

        structure_name = settings.nest.structure.lower()
        structure = self._get_structure_by_name(structure_name)

        if not structure:
            raise ValueError(f"Could not find structure in API: {structure_name}")

        self.set_away(structure, "home")
        if is_winter():
            temp_f = settings.nest.winter_home_min_temp
            self.set_hvac_mode(structure, "heat")
            self.set_temperature(structure, temp_f, comparison=operator.lt)
        else:
            self.set_hvac_mode(structure, "__previous_hvac_mode__")

    def verify(self, action, force_load=True):
        """
        Verify the action actually occurred.
        """
        errors = []

        self.load(force=force_load)
        structure_name = settings.nest.structure.lower()
        structure = self._get_structure_by_name(structure_name)

        if action.value == Action.home.value:
            away = "home"
            mode = "heat"
        else:
            away = "away"
            mode = "eco"

        if structure.away != away:
            errors.append(f"Structure is not marked as {away}!")

        bad_thermostats = [
            x for x in self._get_structure_thermostats(structure) if x.hvac_mode != mode
        ]
        if bad_thermostats:
            errors.append(f"Thermostat mode is not set to {mode}!")

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
