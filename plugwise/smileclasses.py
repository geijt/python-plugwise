from homeassistant.components.climate.const import (
    CURRENT_HVAC_COOL,
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_IDLE,
    HVAC_MODE_AUTO,
    HVAC_MODE_HEAT,
    HVAC_MODE_HEAT_COOL,
    HVAC_MODE_OFF,
    PRESET_AWAY,
)

from .constants import (
    BATTERY,
    ID,
    ILLUMINANCE,
    EXTRA_STATE_ATTRIBS,
    HVAC_ACTION,
    HVAC_MODE,
    HVAC_MODES,
    OUTDOOR_TEMP,
    PRESET_MODE,
    PRESET_MODES,
    PW_NOTIFICATION,
    CURRENT_TEMP,
    TARGET_TEMP,
    TEMP_DIFF,
    VALVE_POS,
)

HVAC_MODES_HEAT_ONLY = [HVAC_MODE_HEAT, HVAC_MODE_AUTO, HVAC_MODE_OFF]
HVAC_MODES_HEAT_COOL = [HVAC_MODE_HEAT_COOL, HVAC_MODE_AUTO, HVAC_MODE_OFF]


class Gateway:
    """ Represent the Plugwise Smile/Stretch gateway."""

    def __init__(self, api, devices, dev_id):
        """Initialize the Gateway."""
        self._api = api
        self._dev_id = dev_id
        self._devices = devices
        self._outdoor_temperature = None
        self._plugwise_notification = {}

        self.binary_sensors = {}
        self.sensors = {}

    @property
    def outdoor_temperature(self):
        """Gateway sensor outdoor temperature."""
        return self._outdoor_temperature

    @property
    def plugwise_notification(self):
        """Binary sensor plugwise notification."""
        return self._plugwise_notification

    def update_data(self):
        """Handle update callbacks."""
        # _LOGGER.debug("Processing data from device %d", self._dev_id)
        data = self._api.get_device_data(self._dev_id)

        sensor_list = ["outdoor_temperature"]
        for item in sensor_list:
            if data.get(item) is not None:
                self.sensors[item] = data.get(item)
        
        self.binary_sensors["plugwise_notification"] = (self._api.notifications != {})


class Thermostat:
    """Represent a Plugwise Thermostat Device."""

    def __init__(self, api, devices, dev_id):
        """Initialize the Thermostat."""
        self._api = api
        self._battery = None
        self._dev_id = dev_id
        self._devices = devices
        self._extra_state_attributes = None
        self._firmware_version = None
        self._friendly_name = None
        self._hvac_action = None
        self._hvac_mode = None
        self._hvac_modes = None
        self._illuminance = None
        self._get_presets = None
        self._model = None
        self._outdoor_temperature = None
        self._preset_mode = None
        self._preset_modes = None
        self._schema_names = None
        self._schema_status = None
        self._selected_schema = None
        self._setpoint = None
        self._smile_class = None
        self._temperature = None
        self._temperature_difference = None
        self._valve_position = None
        self._vendor = None

        self._compressor_state = None
        self._cooling_state = None
        self._heating_state = None

        self.sensors = {}
        #    BATTERY[ID],
        #    ILLUMINANCE[ID],
        #    OUTDOOR_TEMP[ID],
        #    TARGET_TEMP[ID],
        #    CURRENT_TEMP[ID],
        #    TEMP_DIFF[ID],
        #    VALVE_POS[ID],
        #}
        self._active_device = self._api.active_device_present
        self._heater_id = self._api.heater_id
        self._sm_thermostat = self._api.single_master_thermostat()

        self.init_data()

    @property
    def friendly_name(self):
        """Device friendly name."""
        return self._friendly_name

    @property
    def model(self):
        """Device model name."""
        return self._model

    @property
    def vendor(self):
        """Device vendor name."""
        return self._vendor

    @property
    def firmware_version(self):
        """Device firmware version."""
        return self._firmware_version

    @property
    def compressor_state(self):
        """Comlimate HVAC action."""
        return self._compressor_state

    @property
    def cooling_state(self):
        """Climate HVAC action."""
        return self._cooling_state

    @property
    def heating_state(self):
        """Climate HVAC action."""
        return self._heating_state

    @property
    def hvac_mode(self):
        """Climate active HVAC mode."""
        return self._hvac_mode

    @property
    def preset_mode(self):
        """Climate active preset mode."""
        return self._preset_mode

    @property
    def preset_modes(self):
        """Climate preset modes."""
        return self._preset_modes

    @property
    def current_temperature(self):
        """Climate current measured temperature."""
        return self._temperature

    @property
    def target_temperature(self):
        """Climate target temperature."""
        return self._setpoint

    @property
    def extra_state_attributes(self):
        """Climate extra state attributes."""
        return self._extra_state_attributes

    @property
    def battery(self):
        """Thermostat Battery level."""
        return self._battery

    @property
    def illuminance(self):
        """Thermostat illuminance sensor."""
        return self._illuminance

    @property
    def outdoor_temperature(self):
        """Thermostat outdoor temperature."""
        return self._outdoor_temperature

    @property
    def temperature_difference(self):
        """Thermostat temperature difference."""
        return self._temperature_difference

    @property
    def valve_position(self):
        """Thermostat valve position."""
        return self._valve_position

    def init_data(self):
        """Collect the initial data."""
        self._smile_class = self._devices[self._dev_id]["class"]
        self._friendly_name = self._devices[self._dev_id]["name"]
        self._firmware_version = self._devices[self._dev_id]["fw"]
        self._model = self._devices[self._dev_id]["model"]
        self._vendor = self._devices[self._dev_id]["vendor"]

    def update_data(self):
        """Handle update callbacks."""
        # _LOGGER.debug("Processing data from device %d", self._dev_id)
        data = self._api.get_device_data(self._dev_id)

        # sensor data
        sensor_list = [
            "battery",
            "illuminance",
            "outdoor_temperature",
            "setpoint",
            "temperature",
            "temperature_difference",
            "valve_position",
        ]
        for item in sensor_list:
            if data.get(item) is not None:
                self.sensors[item] = data.get(item)

        # skip the rest for thermo_sensors
        if self._smile_class == "thermo_sensor":
            return

        # current & target_temps, heater_central data when required
        self._temperature = data.get("temperature")
        self._setpoint = data.get("setpoint")
        if self._active_device:
            hc_data = self._api.get_device_data(self._heater_id)
            self._compressor_state = hc_data.get("compressor_state")
            if self._sm_thermostat:
                self._cooling_state = hc_data.get("cooling_state")
                self._heating_state = hc_data.get("heating_state")

        # hvac mode
        self._hvac_mode = HVAC_MODE_AUTO
        if "selected_schedule" in data:
            self._selected_schema = data["selected_schedule"]
            self._schema_status = False
            if self._selected_schema is not None:
                self._schema_status = True

        if not self._schema_status:
            if self._preset_mode == PRESET_AWAY:
                self._hvac_mode = HVAC_MODE_OFF
            else:
                self._hvac_mode = HVAC_MODE_HEAT
                if self._compressor_state is not None:
                    self._hvac_mode = HVAC_MODE_HEAT_COOL

        # preset modes
        self._get_presets = data.get("presets")
        if self._get_presets:
            self._preset_modes = list(self._get_presets)

        # preset mode
        self._preset_mode = data.get("active_preset")

        # extra state attributes
        attributes = {}
        self._schema_names = data.get("available_schedules")
        self._selected_schema = data.get("selected_schedule")
        if self._schema_names:
            attributes["available_schemas"] = self._schema_names
        if self._selected_schema:
            attributes["selected_schema"] = self._selected_schema
        self._extra_state_attributes = attributes


class AuxDevice:
    """Represent an external Auxiliary Device."""

    def __init__(self, api, devices, dev_id):
        """Initialize the Thermostat."""
        self._api = api
        self._dev_id = dev_id
        self._dhw_state = None
        self._devices = devices
        self._firmware_version = None
        self._flame_state = None
        self._friendly_name = None
        self._intended_boiler_temperature = None
        self._model = None
        self._modulation_level = None
        self._return_temperature = None
        self._slave_boiler_state = None
        self._smile_class = None
        self._vendor = None
        self._water_pressure = None
        self._water_temperature = None

        self._compressor_state = None
        self._cooling_state = None
        self._heating_state = None

        self.binary_sensors = {}
        #    self._dhw_state,
        #    self._flame_state,
        #    self._slave_boiler_state,
        #}
        self.sensors = {}
        #    self._intended_boiler_temperature,
        #    self._modulation_level,
        #    self._return_temperature,
        #    self._water_pressure,
        #    self._water_temperature,
        #}
        self._active_device = self._api.active_device_present

        self.init_data()

    @property
    def friendly_name(self):
        """Device friendly name."""
        return self._friendly_name

    @property
    def model(self):
        """Device model name."""
        return self._model

    @property
    def vendor(self):
        """Device vendor name."""
        return self._vendor

    @property
    def dhw_state(self):
        """Binary sensor DHW state."""
        return self._dhw_state

    @property
    def flame_state(self):
        """Binary sensor flame state."""
        return self._flame_state

    @property
    def slave_boiler_state(self):
        """Binary sensor slave boiler state."""
        return self._slave_boiler_state

    @property
    def intended_boiler_temperature(self):
        """Aux device intended boiler temperature."""
        return self._intended_boiler_temperature

    @property
    def modulation_level(self):
        """Aux device modulation_level."""
        return self._modulation_level

    @property
    def return_temperature(self):
        """Aux device return temperature."""
        return self._return_temperature

    @property
    def water_pressure(self):
        """Aux device water pressure."""
        return self._water_pressure

    @property
    def water_temperature(self):
        """Aux device water pressure."""
        return self._water_temperature

    def init_data(self):
        """Collect the initial data."""
        self._smile_class = self._devices[self._dev_id]["class"]
        self._friendly_name = self._devices[self._dev_id]["name"]
        self._model = self._devices[self._dev_id]["model"]
        self._vendor = self._devices[self._dev_id]["vendor"]

    def update_data(self):
        """Handle update callbacks."""
        # _LOGGER.debug("Processing data from device %d", self._dev_id)
        data = self._api.get_device_data(self._dev_id)

        binary_sensor_list = [
            "dhw_state",
            "flame_state",
            "slave_boiler_state"
        ]
        sensor_list = [
            "intended_boiler_temperature",
            "modulation_level",
            "return_temperature",
            "water_pressure",
            "water_temperature"
        ]
        if self._active_device:
            for item in binary_sensor_list:
                if data.get(item) is not None:
                    self.binary_sensors[item] = data.get(item)
            for item in sensor_list:
                if data.get(item) is not None:
                    self.sensors[item] = data.get(item)


class Plug:
    """ Represent the Plugwise Plug device."""

    def __init__(self, api, devices, dev_id):
        """Initialize the Plug."""
        self._api = api
        self._dev_id = dev_id
        self._devices = devices
        self._electricity_consumed = None
        self._electricity_consumed_interval = None
        self._electricity_produced = None
        self._electricity_produced_interval = None
        self._firmware_version = None
        self._friendly_name = None
        self._lock_state = None
        self._model = None
        self._relay_state = None
        self._vendor = None

        self.sensors = {}
        self.switches = {}

        self.init_data()

    @property
    def friendly_name(self):
        """Device friendly name."""
        return self._friendly_name

    @property
    def model(self):
        """Device model name."""
        return self._model

    @property
    def vendor(self):
        """Device vendor name."""
        return self._vendor

    @property
    def firmware_version(self):
        """Device firmware version."""
        return self._firmware_version

    @property
    def electricity_consumed(self):
        """Plug sensor electricity consumed."""
        return self._electricity_consumed

    @property
    def electricity_consumed_interval(self):
        """Plug sensor electricity consumed interval."""
        return self._electricity_consumed_interval

    @property
    def electricity_produced(self):
        """Plug sensor electricity produced."""
        return self._electricity_produced

    @property
    def electricity_produced_interval(self):
        """Plug sensor electricity produced interval."""
        return self._electricity_produced_interval

    @property
    def lock_state(self):
        """Plug switch lock state."""
        return self._lock_state

    @property
    def relay_state(self):
        """Plug switch state."""
        return self._relay_state

    def init_data(self):
        """Collect the initial data."""
        self._smile_class = self._devices[self._dev_id]["class"]
        self._friendly_name = self._devices[self._dev_id]["name"]
        self._firmware_version = self._devices[self._dev_id]["fw"]
        self._model = self._devices[self._dev_id]["model"]
        self._vendor = self._devices[self._dev_id]["vendor"]

    def update_data(self):
        """Handle update callbacks."""
        # _LOGGER.debug("Processing data from device %d", self._dev_id)
        data = self._api.get_device_data(self._dev_id)

        sensor_list = [
            "electricity_consumed",
            "electricity_consumed_interval",
            "electricity_produced",
            "electricity_produced_interval",
        ]
        for item in sensor_list:
            if data.get(item) is not None:
                self.sensors[item] = data.get(item)

        switch_list = ["lock", "relay"]
        for item in switch_list:
            if data.get(item) is not None:
                self.switches[item] = data.get(item)


