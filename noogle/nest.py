#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module has the class used to control the Nest thermostat.
"""

# Imports #####################################################################
import json
import os
import time
from typing import List

import requests

from dataclasses import dataclass

from .models import Action
from .settings import TOKEN_FOLDER, get_settings
from .utils import is_winter
from .helpers import print_log


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
class Structure:
    structure_id: str
    name: str
    away: str
    thermostats: List[str]


@dataclass(frozen=True)
class Thermostat:
    device_id: str
    name: str
    target_temperature_low_f: float
    target_temperature_f: int
    eco_temperature_low_f: float
    structure_id: str
    hvac_mode: str
    previous_hvac_mode: str


class NestAPI:

    base_api_url = "https://developer-api.nest.com"
    token_file = f"{TOKEN_FOLDER}/nest-token.json"
    verification_wait = 10

    def __init__(self, interactive=True, load=True):
        self.interactive = interactive
        self.project_settings = get_settings()

        if not os.path.exists(NestAPI.token_file):
            self._get_access_token()

        with open(NestAPI.token_file) as fh:
            self.token = json.load(fh)["access_token"]

        self.structures = []
        self.thermostats = []

        self.__loaded = False
        if load:
            self.load()

    def load(self, force=False, request_auth=True):
        """
        Reads the data structures from the API.
        """
        if self.__loaded and not force:
            return

        data = self.get(request_auth=request_auth)

        self.__loaded = False
        self.structures = []
        self.thermostats = []

        for thermostat in data.get("devices", {}).get("thermostats", {}).values():
            t = Thermostat(
                device_id=thermostat["device_id"],
                name=thermostat["name"],
                target_temperature_low_f=thermostat["target_temperature_low_f"],
                target_temperature_f=thermostat["target_temperature_f"],
                eco_temperature_low_f=thermostat["eco_temperature_low_f"],
                structure_id=thermostat["structure_id"],
                hvac_mode=thermostat["hvac_mode"],
                previous_hvac_mode=thermostat["previous_hvac_mode"],
            )
            self.thermostats.append(t)

        for structure in data.get("structures", {}).values():
            s = Structure(
                structure_id=structure["structure_id"],
                name=structure["name"],
                away=structure["away"],
                thermostats=structure["thermostats"],
            )
            self.structures.append(s)

        self.__loaded = True

    def _get_access_token(self):
        if not self.interactive:
            raise Exception("Cannot request access token unless in interactive mode")

        settings = get_settings()
        client_id = settings.get("nest.product-id") or os.environ.get("NEST_PRODUCT_ID")
        client_secret = settings.get("nest.product-secret") or os.environ.get(
            "NEST_PRODUCT_SECRET"
        )

        # If we have to re-authorize, show this URL in the window, have the
        # user accept the perms, and enter the code
        authorization_url = (
            f"https://home.nest.com/login/oauth2?client_id={client_id}&state=1"
        )

        print_log("Go to the following URL and accept the permissions:")
        print_log(authorization_url)
        auth_code = input("...enter the pincode given: ")

        token_url = "https://api.home.nest.com/oauth2/access_token"
        payload = f"code={auth_code}&client_id={client_id}&client_secret={client_secret}&grant_type=authorization_code"
        headers = {"content-type": "application/x-www-form-urlencoded"}
        response = requests.post(token_url, data=payload, headers=headers)

        if response.status_code != 200:
            raise Exception("Could not authenticate: " + response.json())

        with open(NestAPI.token_file, "w") as fh:
            fh.write(response.text)

        self.token = response.json()["access_token"]

    def _get_structure_by_name(self, name):
        return next(
            (x for x in self.structures if name.lower() == x.name.lower()), None
        )

    def _get_thermostat(self, device_id):
        return next(
            (x for x in self.thermostats if device_id.lower() == x.device_id.lower()),
            None,
        )

    def _get_structure_thermostats(self, structure):
        """
        Returns all thermostat objects found in the structure.
        """
        return [t for t in self.thermostats if t.device_id in structure.thermostats]

    def get(self, url="/", request_auth=True):
        """
        Perform a `get` on the API.  This method will attempt to get a new
        access token if needed.  This requires user interaction.
        """
        try:
            return self._get(url)
        except Unauthorized:
            if request_auth:
                self._get_access_token()
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
                self._get_access_token()
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

    def show(self, request_auth=True):
        """
        Displays some information about the structure and thermostat using
        the NestAPI.
        """
        self.load(request_auth=request_auth)

        for structure in self.structures:
            print_log(structure.name)
            print_log(f"    ID: {structure.structure_id}")
            print_log(f"    Away: {structure.away}")
            print_log("    Thermostats:")
            for t in [
                x for x in self.thermostats if x.device_id in structure.thermostats
            ]:
                if t.hvac_mode == "eco":
                    setpoint = f"{t.eco_temperature_low_f} F (eco)"
                else:
                    setpoint = f"{t.target_temperature_low_f} F ({t.hvac_mode})"

                print_log(f"        Device: {t.name}")
                print_log(f"            ID: {t.device_id}")
                print_log(f"            Setpoint: {setpoint}")

    def set_away(self, structure, away="away", force=False):
        """
        Sets the `away` mode for the structure.
        """
        if (structure.away == away) and (not force):
            return

        payload = {"away": away}
        url = f"/structures/{structure.structure_id}"
        return self.put(url, payload)

    def set_temperature(self, structure, temp_f: int, force=False):

        thermostats = self._get_structure_thermostats(structure)
        bad_thermostats = [t for t in thermostats if t.target_temperature_f != temp_f]

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

        structure_name = self.project_settings.get("nest.structure").lower()
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

        structure_name = self.project_settings.get("nest.structure").lower()
        structure = self._get_structure_by_name(structure_name)

        if not structure:
            raise ValueError(f"Could not find structure in API: {structure_name}")

        self.set_away(structure, "home")
        if is_winter():
            temp_f = int(self.project_settings.get("nest.winter-home-temp", 60))
            self.set_hvac_mode(structure, "heat")
            self.set_temperature(structure, temp_f, force=True)
        else:
            self.set_hvac_mode(structure, "__previous_hvac_mode__")

    def verify(self, action, force_load=True):
        """
        Verify the action actually occurred.
        """
        errors = []

        self.load(force=force_load)
        structure_name = self.project_settings.get("nest.structure").lower()
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
