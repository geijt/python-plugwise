""" Plugwise SmileClasses."""

from .constants import (
    ATTR_ICON,
    ATTR_ID,
    ATTR_STATE,
    BATTERY,
    COOLING_ICON,
    CURRENT_TEMP,
    DEVICE_STATE,
    DHW_COMF_MODE,
    DHW_STATE,
    EL_CONSUMED,
    EL_CONSUMED_INTERVAL,
    EL_PRODUCED,
    EL_PRODUCED_INTERVAL,
    FLAME_ICON,
    FLAME_STATE,
    FLOW_OFF_ICON,
    FLOW_ON_ICON,
    HEATING_ICON,
    HVAC_MODE_AUTO,
    HVAC_MODE_HEAT,
    HVAC_MODE_HEAT_COOL,
    HVAC_MODE_OFF,
    IDLE_ICON,
    ILLUMINANCE,
    INTENDED_BOILER_TEMP,
    LOCK,
    MOD_LEVEL,
    OUTDOOR_TEMP,
    PRESET_AWAY,
    PW_NOTIFICATION,
    RELAY,
    RETURN_TEMP,
    SLAVE_BOILER_STATE,
    TARGET_TEMP,
    TEMP_DIFF,
    VALVE_POS,
    WATER_PRESSURE,
    WATER_TEMP,
)


def __init__(self):
    """Initialize the SmileClasses."""
    self._heating_state = None
    self._cooling_state = None


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

        self.sensor_list = [OUTDOOR_TEMP]

        self._sm_thermostat = self._api.single_master_thermostat()

        self.init_data()

    @property
    def outdoor_temperature(self):
        """Gateway sensor outdoor temperature."""
        return self._outdoor_temperature

    @property
    def plugwise_notification(self):
        """Binary sensor plugwise notification."""
        return self._plugwise_notification

    def init_data(self):
        """Collect the initial data."""
        data = self._api.get_device_data(self._dev_id)

        for key, value in PW_NOTIFICATION.items():
            if self._sm_thermostat is not None:
                self.binary_sensors.update(PW_NOTIFICATION)

        for sensor in self.sensor_list:
            for key, value in sensor.items():
                if data.get(value[ATTR_ID]) is not None:
                    self.sensors.update(sensor)

    def update_data(self):
        """Handle update callbacks."""
        data = self._api.get_device_data(self._dev_id)

        for key, value in PW_NOTIFICATION.items():
            if self._sm_thermostat is not None:
                self.binary_sensors[key][ATTR_STATE] = self._api.notifications != {}

        for sensor in self.sensor_list:
            for key, value in sensor.items():
                if data.get(value[ATTR_ID]) is not None:
                    self.sensors[key][ATTR_STATE] = data.get(value[ATTR_ID])


class Thermostat:
    """Represent a Plugwise Thermostat Device."""

    def __init__(self, api, devices, dev_id):
        """Initialize the Thermostat."""

        self._api = api
        self._battery = None
        self._compressor_state = None
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

        self.sensors = {}

        self.sensor_list = [
            BATTERY,
            ILLUMINANCE,
            OUTDOOR_TEMP,
            TARGET_TEMP,
            CURRENT_TEMP,
            TEMP_DIFF,
            VALVE_POS,
        ]

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
        """Compressor state."""
        return self._compressor_state

    @property
    def cooling_state(self):
        """Cooling state."""
        return self._cooling_state

    @property
    def heating_state(self):
        """Heating state."""
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

        data = self._api.get_device_data(self._dev_id)
        for sensor in self.sensor_list:
            for key, value in sensor.items():
                if data.get(value[ATTR_ID]) is not None:
                    self.sensors.update(sensor)

    def update_data(self):
        """Handle update callbacks."""
        data = self._api.get_device_data(self._dev_id)

        # sensor data
        for sensor in self.sensor_list:
            for key, value in sensor.items():
                if data.get(value[ATTR_ID]) is not None:
                    self.sensors[key][ATTR_STATE] = data.get(value[ATTR_ID])

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
        self._compressor_state = None
        self._cooling_state = None
        self._dev_id = dev_id
        self._dhw_state = None
        self._devices = devices
        self._firmware_version = None
        self._flame_state = None
        self._friendly_name = None
        self._heating_state = None
        self._intended_boiler_temperature = None
        self._model = None
        self._modulation_level = None
        self._return_temperature = None
        self._slave_boiler_state = None
        self._smile_class = None
        self._vendor = None
        self._water_pressure = None
        self._water_temperature = None

        self.binary_sensors = {}
        self.sensors = {}
        self.switches = {}

        self.b_sensor_list = [DHW_STATE, FLAME_STATE, SLAVE_BOILER_STATE]

        self.sensor_list = [
            DEVICE_STATE,
            INTENDED_BOILER_TEMP,
            MOD_LEVEL,
            RETURN_TEMP,
            WATER_PRESSURE,
            WATER_TEMP,
        ]

        self.switch_list = [DHW_COMF_MODE]

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

        data = self._api.get_device_data(self._dev_id)

        if self._active_device:
            for b_sensor in self.b_sensor_list:
                for key, value in b_sensor.items():
                    if data.get(value[ATTR_ID]) is not None:
                        self.binary_sensors.update(b_sensor)

        for sensor in self.sensor_list:
            for key, value in sensor.items():
                if data.get(value[ATTR_ID]) is not None or sensor == DEVICE_STATE:
                    self.sensors.update(sensor)

        for switch in self.switch_list:
            for key, value in switch.items():
                if data.get(value[ATTR_ID]) is not None:
                    self.switches.update(switch)

    def update_data(self):
        """Handle update callbacks."""
        data = self._api.get_device_data(self._dev_id)

        if self._active_device:
            for b_sensor in self.b_sensor_list:
                for key, value in b_sensor.items():
                    if data.get(value[ATTR_ID]) is not None:
                        self.binary_sensors[key][ATTR_STATE] = bs_state = data.get(
                            value[ATTR_ID]
                        )
                        if b_sensor == DHW_STATE:
                            self.binary_sensors[key][ATTR_ICON] = (
                                FLOW_ON_ICON if bs_state else FLOW_OFF_ICON
                            )
                        if b_sensor == FLAME_STATE or b_sensor == SLAVE_BOILER_STATE:
                            self.binary_sensors[key][ATTR_ICON] = (
                                FLAME_ICON if bs_state else IDLE_ICON
                            )

        for sensor in self.sensor_list:
            for key, value in sensor.items():
                if data.get(value[ATTR_ID]) is not None:
                    self.sensors[key][ATTR_STATE] = data.get(value[ATTR_ID])
                if sensor == DEVICE_STATE:
                    self.sensors[key][ATTR_STATE] = "idle"
                    self.sensors[key][ATTR_ICON] = IDLE_ICON
                    if self._heating_state:
                        self.sensors[key][ATTR_STATE] = "heating"
                        self.sensors[key][ATTR_ICON] = HEATING_ICON
                    if self._cooling_state:
                        self.sensors[key][ATTR_STATE] = "cooling"
                        self.sensors[key][ATTR_ICON] = COOLING_ICON

        for switch in self.switch_list:
            for key, value in switch.items():
                if data.get(value[ATTR_ID]) is not None:
                    self.switches[key][ATTR_STATE] = data.get(value[ATTR_ID])


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

        self.sensor_list = [
            EL_CONSUMED,
            EL_CONSUMED_INTERVAL,
            EL_PRODUCED,
            EL_PRODUCED_INTERVAL,
        ]

        self.switch_list = [LOCK, RELAY]

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

        data = self._api.get_device_data(self._dev_id)

        for sensor in self.sensor_list:
            for key, value in sensor.items():
                if data.get(value[ATTR_ID]) is not None:
                    self.sensors.update(sensor)

        for switch in self.switch_list:
            for key, value in switch.items():
                if data.get(value[ATTR_ID]) is not None:
                    self.switches.update(switch)

    def update_data(self):
        """Handle update callbacks."""
        data = self._api.get_device_data(self._dev_id)

        for sensor in self.sensor_list:
            for key, value in sensor.items():
                if data.get(value[ATTR_ID]) is not None:
                    self.sensors[key][ATTR_STATE] = data.get(value[ATTR_ID])

        for switch in self.switch_list:
            for key, value in switch.items():
                if data.get(value[ATTR_ID]) is not None:
                    self.switches[key][ATTR_STATE] = data.get(value[ATTR_ID])
