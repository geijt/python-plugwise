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
    CURRENT_TEMP,
    TARGET_TEMP,
    TEMP_DIFF,
    VALVE_POS,
)

HVAC_MODES_HEAT_ONLY = [HVAC_MODE_HEAT, HVAC_MODE_AUTO, HVAC_MODE_OFF]
HVAC_MODES_HEAT_COOL = [HVAC_MODE_HEAT_COOL, HVAC_MODE_AUTO, HVAC_MODE_OFF]


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

        self.climate_params = {
            self._extra_state_attributes,
            self._hvac_action,
            self._hvac_mode,
            self._hvac_modes,
            self._preset_mode,
            self._preset_modes,
            self._temperature,
            self._setpoint,
        }
        self.sensors = {
            BATTERY[ID],
            ILLUMINANCE[ID],
            OUTDOOR_TEMP[ID],
            TARGET_TEMP[ID],
            CURRENT_TEMP[ID],
            TEMP_DIFF[ID],
            VALVE_POS[ID],
        }
        self._active_device = self._api.active_device_present
        self._heater_id = self._api.heater_id
        self._single_thermostat = self._api.single_master_thermostat()

        self.init_data()
        self.update_data()

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
    def hvac_action(self):
        """Climate HVAC action."""
        return self._hvac_action

    @property
    def hvac_mode(self):
        """Climate active HVAC mode."""
        return self._hvac_mode

    @property
    def hvac_modes(self):
        """Climate available HVAC modes."""
        return self._hvac_modes

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
        climate_data = self._api.get_device_data(self._dev_id)

        # sensor data
        self._battery = climate_data.get("battery")
        self._illuminance = climate_data.get("illuminance")
        self._outdoor_temperature = climate_data.get("outdoor_temperature")
        self._temperature_difference = climate_data.get("temperature_difference")
        self._valve_position = climate_data.get("valve_position")

        # current & target_temps, heater_central data when required
        self._temperature = climate_data.get("temperature")
        if self._active_device and self._smile_class != "thermo_sensor":
            self._setpoint = climate_data.get("setpoint")
            heater_central_data = self._api.get_device_data(self._heater_id)
            self._compressor_state = heater_central_data.get("compressor_state")
            if self._single_thermostat:
                self._cooling_state = heater_central_data.get("cooling_state")
                self._heating_state = heater_central_data.get("heating_state")

        # skip the rest for thermo_sensors
        if self._smile_class == "thermo_sensor":
            return

        # hvac action
        self._hvac_action = CURRENT_HVAC_IDLE
        if self._single_thermostat:
            if self._heating_state:
                self._hvac_action = CURRENT_HVAC_HEAT
            if self._cooling_state:
                self._hvac_action = CURRENT_HVAC_COOL
        elif self._setpoint > self._temperature:
            self._hvac_action = CURRENT_HVAC_HEAT

        # hvac mode
        self._hvac_mode = HVAC_MODE_AUTO
        if "selected_schedule" in climate_data:
            self._selected_schema = climate_data["selected_schedule"]
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

        # hvac modes
        self._hvac_modes = HVAC_MODES_HEAT_ONLY
        if self._compressor_state is not None:
            self._hvac_modes = HVAC_MODES_HEAT_COOL

        # preset modes
        self._get_presets = climate_data.get("presets")
        if self._get_presets:
            self._preset_modes = list(self._get_presets)

        # preset mode
        self._preset_mode = climate_data.get("active_preset")

        # extra state attributes
        attributes = {}
        self._schema_names = climate_data.get("available_schedules")
        self._selected_schema = climate_data.get("selected_schedule")
        if self._schema_names:
            attributes["available_schemas"] = self._schema_names
        if self._selected_schema:
            attributes["selected_schema"] = self._selected_schema
        self._extra_state_attributes = attributes
