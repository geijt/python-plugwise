"""
Use of this source code is governed by the MIT license found in the LICENSE file.

The Smile Gateway device to control associated thermostats, etc.
"""
import asyncio
import logging

import aiohttp

from .exceptions import InvalidAuthentication, PlugwiseException
from .smile import Smile

_LOGGER = logging.getLogger(__name__)


class GWDevice:
    """ Representing the Plugwise Smile/Stretch gateway to which the various Nodes are connected."""

    def __init__(self, host, password, websession, port=None):
        """Initialize the device."""
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
                self._host, self._password, self._port, websession=self._websession
            )
        else:
            api = Smile(self._host, self._password, websession=self._websession)

        try:
            await api.connect()
        except InvalidAuthentication as err:
            _LOGGER.error("Invalid login:", err)
        except PlugwiseException as err:
            _LOGGER.error("Cannot connect:", err)
        else:
            await api.full_update_device()

        self._devices = api.get_all_devices()
        self._single_master_thermostat = api.single_master_thermostat()
        self._gateway_id = api.gateway_id
        self._firmware_version = api.smile_version[1]
        self._hostname = api.smile_hostname
        self._s_type = api.smile_type

        for dev_id in self._devices:
            if self._devices[dev_id]["class"] != "gateway":
                continue

            self._friendly_name = self._devices[dev_id]["name"]
            self._model = self._devices[dev_id]["model"]
            self._vendor = self._devices[dev_id]["vendor"]

        return api
