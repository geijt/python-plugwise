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


class MasterThermostat:
    """Represents a Master Thermostat."""

    def __init__(self, api, dev_id):
        """Initialize the paramaters."""
        self.climate_params = {
            EXTRA_STATE_ATTRIBS[ID],
            HVAC_ACTION[ID],
            HVAC_MODE[ID],
            HVAC_MODES[ID],
            PRESET_MODE[ID],
            PRESET_MODES[ID],
            CURRENT_TEMP[ID],
            TARGET_TEMP[ID],
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
        self._api = api
        self._current_temperature = None
        self._dev_id = dev_id
        self._extra_state_attributes = None
        self._firmware_version = None
        self._friendly_name = None
        self._hvac_action = None
        self._hvac_mode = None
        self._hvac_modes = None
        self._get_presets = None
        self._model = None
        self._preset_mode = None
        self._preset_modes = None
        self._schema_names = None
        self._schema_status = None
        self._selected_schema = None
        self._target_temperature = None
        self._vendor = None

        self._compressor_state = None
        self._cooling_state = None
        self._heating_state = None

        self._climate = {}
        self._sensor = {}
        self._active_device = self._api.active_device_present
        self._heater_id = self._api.heater_id
        self._single_thermostat = self._api.single_master_thermostat()

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
    def hvac_mode(self):
        """Active HVAC mode."""
        return self._hvac_mode

    @property
    def hvac_modes(self):
        """Available HVAC modes."""
        return self._hvac_modes

    @property
    def preset_mode(self):
        """Active preset mode."""
        return self._preset_mode

    @property
    def preset_modes(self):
        """Available preset modes."""
        return self._preset_modes

    @property
    def current_temperature(self):
        """Current measured temperature."""
        return self._current_temperature

    @property
    def target_temperature(self):
        """Target temperature."""
        return self._target_temperature

    @property
    def extra_state_attributes(self):
        """Extra state attributes."""
        return self._extra_state_attributes

    def update_data(self):
        """Handle update callbacks."""
        # _LOGGER.debug("Processing data from device %d", self._dev_id)

        climate_data = self._api.get_device_data(self._dev_id)
        self._friendly_name = climate_data.get("name")
        self._firmware_version = climate_data.get("fw")
        self._model = climate_data.get("model")
        self._vendor = climate_data.get("vensor")
        # QUESTION/TODO: should we split between data that is static, like above, and data that is dynamic?
        if self._active_device:
            heater_central_data = self._api.get_device_data(self._heater_id)
            self._compressor_state = heater_central_data.get("compressor_state")
            self._cooling_state = heater_central_data.get("cooling_state")
            self._heating_state = heater_central_data.get("heating_state")

        # current & target_temps
        self._target_temperature = climate_data.get("setpoint")
        self._current_temperature = climate_data.get("temperature")

        # hvac action
        self._hvac_action = CURRENT_HVAC_IDLE
        if self._single_thermostat:
            if self._heating_state:
                self._hvac_action = CURRENT_HVAC_HEAT
            if self._cooling_state:
                self._hvac_action = CURRENT_HVAC_COOL
        elif self._target_temperature > self._current_temperature:
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
        self._hvac_mode = HVAC_MODES_HEAT_ONLY
        if self._compressor_state is not None:
            self._hvac_mode = HVAC_MODES_HEAT_COOL

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
