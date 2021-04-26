"""
Use of this source code is governed by the MIT license found in the LICENSE file.

The Smile Gateway device to control associated thermostats, etc.
"""
import asyncio
import logging

import aiohttp

from .constants import SWITCH_CLASSES, THERMOSTAT_CLASSES
from .exceptions import InvalidAuthentication, PlugwiseException
from .smile import Smile
from .smileclasses import AuxDevice, Gateway, Plug, Thermostat

_LOGGER = logging.getLogger(__name__)


class GWDevice:
    """ Representing the Plugwise Smile/Stretch gateway to which the various Nodes are connected."""

    def __init__(self, host, password, websession, port=None):
        """Initialize the device."""
        self._api = None
        self._host = host
        self._password = password
        self._port = port
        self._websession = websession

        self._devices = {}
        self._firmware_version = None
        self._friendly_name = None
        self._gateway_id = None
        self._hostname = None
        self._model = None
        self._s_type = None
        self._vendor = None

    @property
    def devices(self) -> dict:
        """All connected plugwise devices with the Appliance ID address as key"""
        return self._devices

    @property
    def firmware_version(self):
        """Device firmware version."""
        return self._firmware_version

    @property
    def gateway_id(self):
        """Device firmware version."""
        return self._gateway_id

    @property
    def friendly_name(self):
        """Device friendly name."""
        return self._friendly_name

    @property
    def hostname(self):
        """Device model name."""
        return self._hostname

    @property
    def model(self):
        """Device model name."""
        return self._model

    @property
    def s_type(self):
        """Device vendor name."""
        return self._s_type

    @property
    def single_master_thermostat(self):
        """Device vendor name."""
        return self._single_master_thermostat

    @property
    def vendor(self):
        """Device vendor name."""
        return self._vendor

    async def discover(self):
        """Connect to the Gateway Device and collect the properties."""
        if self._port:
            api = Smile(
                self._host,
                self._password,
                self._port,
                timeout=30,
                websession=self._websession,
            )
        else:
            api = Smile(
                self._host, self._password, timeout=30, websession=self._websession
            )

        try:
            await api.connect()
        except InvalidAuthentication as err:
            _LOGGER.error("Invalid login:", err)
        except PlugwiseException as err:
            _LOGGER.error("Cannot connect:", err)
        else:
            await api.full_update_device()
            self._api = api

        self._devices = self._api.get_all_devices()
        self._single_master_thermostat = self._api.single_master_thermostat()
        self._gateway_id = self._api.gateway_id
        self._firmware_version = self._api.smile_version[1]
        self._hostname = self._api.smile_hostname
        self._s_type = self._api.smile_type

        for dev_id in self._devices:
            if self._devices[dev_id]["class"] != "gateway":
                continue

            self._friendly_name = self._devices[dev_id]["name"]
            self._model = self._devices[dev_id]["model"]
            self._vendor = self._devices[dev_id]["vendor"]

        return self._api

    async def refresh_data(self):
        """Reconnect to the Gateway Device and collect the data points."""

        await self._api.update_device()

        for dev_id in self._devices:
            if self._devices[dev_id]["class"] in THERMOSTAT_CLASSES:
                thermostat = Thermostat(self._api, self._devices, dev_id)
                thermostat.update_data()
                self._devices[dev_id].update({"hvac_mode": thermostat.hvac_mode})
                self._devices[dev_id].update({"preset_mode": thermostat.preset_mode})
                self._devices[dev_id].update({"preset_mode": thermostat.preset_mode})
                self._devices[dev_id].update({"preset_mode": thermostat.preset_mode})
                self._devices[dev_id].update(
                    {"current_temperature": thermostat.current_temperature}
                )
                self._devices[dev_id].update(
                    {"extra_state_attributes": thermostat.extra_state_attributes}
                )
                self._devices[dev_id].update({"sensors": thermostat.sensors})
            if self._devices[dev_id]["class"] == "thermo_sensor":
                thermostat = Thermostat(self._api, self._devices, dev_id)
                thermostat.update_data()
                self._devices[dev_id].update({"sensors": thermostat.sensors})
            if self._devices[dev_id]["class"] == "heater_central":
                auxdev = AuxDevice(self._api, self._devices, dev_id)
                auxdev.update_data()
                self._devices[dev_id].update({"binary_sensors": auxdev.binary_sensors})
                self._devices[dev_id].update({"sensors": auxdev.sensors})
                self._devices[dev_id].update({"switches": auxdev.switches})
            if self._devices[dev_id]["class"] == "gateway":
                gateway = Gateway(self._api, self._devices, dev_id)
                gateway.update_data()
                self._devices[dev_id].update({"binary_sensors": gateway.binary_sensors})
                self._devices[dev_id].update({"sensors": gateway.sensors})
            if any(dummy in self._devices[dev_id]["types"] for dummy in SWITCH_CLASSES):
                plug = Plug(self._api, self._devices, dev_id)
                plug.update_data()
                if plug.sensors != {}:
                    self._devices[dev_id].update({"sensors": plug.sensors})
                self._devices[dev_id].update({"switches": plug.switches})
