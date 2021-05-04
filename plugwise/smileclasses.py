""" Plugwise SmileClasses."""
import asyncio

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
    EL_CONSUMED_OFF_PEAK_CUMULATIVE,
    EL_CONSUMED_OFF_PEAK_INTERVAL,
    EL_CONSUMED_OFF_PEAK_POINT,
    EL_CONSUMED_PEAK_CUMULATIVE,
    EL_CONSUMED_PEAK_INTERVAL,
    EL_CONSUMED_PEAK_POINT,
    EL_PRODUCED,
    EL_PRODUCED_INTERVAL,
    EL_PRODUCED_OFF_PEAK_CUMULATIVE,
    EL_PRODUCED_OFF_PEAK_INTERVAL,
    EL_PRODUCED_OFF_PEAK_POINT,
    EL_PRODUCED_PEAK_CUMULATIVE,
    EL_PRODUCED_PEAK_INTERVAL,
    EL_PRODUCED_PEAK_POINT,
    FLAME_ICON,
    FLAME_STATE,
    FLOW_OFF_ICON,
    FLOW_ON_ICON,
    GAS_CONSUMED_CUMULATIVE,
    GAS_CONSUMED_INTERVAL,
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
    NET_EL_CUMULATIVE,
    NET_EL_POINT,
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


class Gateway:
    """ Represent the Plugwise Smile/Stretch gateway."""

    def __init__(self, api, dev_id):
        """Initialize the Gateway."""
        self._api = api
        self._dev_id = dev_id

        self.binary_sensors = {}
        self.sensors = {}

        self.sensor_list = [
            OUTDOOR_TEMP,
            EL_CONSUMED_PEAK_INTERVAL,
            EL_CONSUMED_OFF_PEAK_INTERVAL,
            EL_CONSUMED_OFF_PEAK_POINT,
            EL_CONSUMED_PEAK_POINT,
            EL_CONSUMED_OFF_PEAK_CUMULATIVE,
            EL_CONSUMED_PEAK_CUMULATIVE,
            EL_PRODUCED_PEAK_INTERVAL,
            EL_PRODUCED_OFF_PEAK_INTERVAL,
            EL_PRODUCED_OFF_PEAK_POINT,
            EL_PRODUCED_PEAK_POINT,
            EL_PRODUCED_OFF_PEAK_CUMULATIVE,
            EL_PRODUCED_PEAK_CUMULATIVE,
            NET_EL_POINT,
            NET_EL_CUMULATIVE,
            GAS_CONSUMED_INTERVAL,
            GAS_CONSUMED_CUMULATIVE,
        ]

        self._sm_thermostat = self._api.single_master_thermostat()

        self.init_data()

    def init_data(self):
        """Collect the initial data."""
        data = self._api.get_device_data(self._dev_id)

        if self._sm_thermostat is not None:
            for key, value in PW_NOTIFICATION.items():
                self.binary_sensors.update(PW_NOTIFICATION)

        for sensor in self.sensor_list:
            for key, value in sensor.items():
                if data.get(value[ATTR_ID]) is not None:
                    self.sensors.update(sensor)

    def update_data(self):
        """Handle update callbacks."""
        data = self._api.get_device_data(self._dev_id)

        if self._sm_thermostat is not None:
            for key, value in PW_NOTIFICATION.items():
                self.binary_sensors[key][ATTR_STATE] = self._api.notifications != {}

        for sensor in self.sensor_list:
            for key, value in sensor.items():
                if data.get(value[ATTR_ID]) is not None:
                    self.sensors[key][ATTR_STATE] = data.get(value[ATTR_ID])


class Thermostat:
    """Represent a Plugwise Thermostat Device."""

    def __init__(self, api, dev_id):
        """Initialize the Thermostat."""

        self._api = api
        self._compressor_state = None
        self._cooling_state = None
        self._dev_id = dev_id
        self._extra_state_attributes = None
        self._get_presets = None
        self._heating_state = None
        self._hvac_mode = None
        self._last_active_schema = None
        self._preset_mode = None
        self._preset_modes = None
        self._schedule_temp = None
        self._schema_names = None
        self._schema_status = None
        self._selected_schema = None
        self._setpoint = None
        self._smile_class = None
        self._temperature = None

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
    def presets(self):
        """Climate list of presets."""
        return self._get_presets

    @property
    def preset_mode(self):
        """Climate active preset mode."""
        return self._preset_mode

    @property
    def preset_modes(self):
        """Climate preset modes."""
        return self._preset_modes

    @property
    def last_active_schema(self):
        """Climate last active schema."""
        return self._last_active_schema

    @property
    def current_temperature(self):
        """Climate current measured temperature."""
        return self._temperature

    @property
    def target_temperature(self):
        """Climate target temperature."""
        return self._setpoint

    @property
    def schedule_temperature(self):
        """Climate target temperature."""
        return self._schedule_temp

    @property
    def extra_state_attributes(self):
        """Climate extra state attributes."""
        return self._extra_state_attributes

    def init_data(self):
        """Collect the initial data."""
        data = self._api.get_device_data(self._dev_id)

        for sensor in self.sensor_list:
            for key, value in sensor.items():
                if data.get(value[ATTR_ID]) is not None:
                    self.sensors.update(sensor)

    async def set_schedule_state(self, loc_id, name, state):
        """
        Set the schedule, with the given name, connected to a location.

        Determined from - DOMAIN_OBJECTS.
        """
        if self.smile_legacy:
            return await self.set_schedule_state_legacy(name, state)

        schema_rule_ids = self.rule_ids_by_name(str(name), loc_id)
        if schema_rule_ids == {} or schema_rule_ids is None:
            return False

        for schema_rule_id, location_id in schema_rule_ids.items():
            template_id = None
            if location_id == loc_id:
                state = str(state)
                locator = f'.//*[@id="{schema_rule_id}"]/template'
                for rule in self.domain_objects.findall(locator):
                    template_id = rule.attrib["id"]

                uri = f"{RULES};id={schema_rule_id}"
                data = (
                    "<rules><rule"
                    f' id="{schema_rule_id}"><name><![CDATA[{name}]]></name><template'
                    f' id="{template_id}"/><active>{state}</active></rule></rules>'
                )

                await self.request(uri, method="put", data=data)

        return True

    async def set_preset(self, loc_id, preset):
        """Set the given location-preset on the relevant thermostat - from LOCATIONS."""
        if self.smile_legacy:
            return await self.set_preset_legacy(preset)

        current_location = self.locations.find(f'location[@id="{loc_id}"]')
        location_name = current_location.find("name").text
        location_type = current_location.find("type").text

        if preset not in self.presets(loc_id):
            return False

        uri = f"{LOCATIONS};id={loc_id}"
        data = (
            "<locations><location"
            f' id="{loc_id}"><name>{location_name}</name><type>{location_type}'
            f"</type><preset>{preset}</preset></location></locations>"
        )

        await self.request(uri, method="put", data=data)
        return True

    async def set_temperature(self, loc_id, temperature):
        """Send temperature-set request to the locations thermostat."""
        temperature = str(temperature)
        uri = self.temperature_uri(loc_id)
        data = (
            "<thermostat_functionality><setpoint>"
            f"{temperature}</setpoint></thermostat_functionality>"
        )

        await self.request(uri, method="put", data=data)
        return True

    async def set_preset_legacy(self, preset):
        """Set the given preset on the thermostat - from DOMAIN_OBJECTS."""
        locator = f'rule/directives/when/then[@icon="{preset}"].../.../...'
        rule = self.domain_objects.find(locator)
        if rule is None:
            return False

        uri = f"{RULES}"
        data = f'<rules><rule id="{rule.attrib["id"]}"><active>true</active></rule></rules>'

        await self.request(uri, method="put", data=data)
        return True

    async def set_schedule_state_legacy(self, name, state):
        """Send a set request to the schema with the given name."""
        schema_rule_id = None
        for rule in self.domain_objects.findall("rule"):
            if rule.find("name").text == name:
                schema_rule_id = rule.attrib["id"]

        if schema_rule_id is None:
            return False

        template_id = None
        state = str(state)
        locator = f'.//*[@id="{schema_rule_id}"]/template'
        for rule in self.domain_objects.findall(locator):
            template_id = rule.attrib["id"]

        uri = f"{RULES};id={schema_rule_id}"
        data = (
            "<rules><rule"
            f' id="{schema_rule_id}"><name><![CDATA[{name}]]></name><template'
            f' id="{template_id}" /><active>{state}</active></rule></rules>'
        )

        await self.request(uri, method="put", data=data)
        return True

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
        self._schedule_temp = data.get("schedule_temperature")
        if self._active_device:
            hc_data = self._api.get_device_data(self._heater_id)
            self._compressor_state = hc_data.get("compressor_state")
            if self._sm_thermostat:
                self._cooling_state = hc_data.get("cooling_state")
                self._heating_state = hc_data.get("heating_state")

        # hvac mode
        self._hvac_mode = HVAC_MODE_AUTO
        if "selected_schedule" in data:
            self._selected_schema = data.get("selected_schedule")
            self._schema_status = False
            if self._selected_schema is not None:
                self._schema_status = True

        self._last_active_schema = data.get("last_used")

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

    def __init__(self, api, dev_id):
        """Initialize the Thermostat."""
        self._api = api
        self._cooling_state = None
        self._dev_id = dev_id
        self._heating_state = None

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
        self._heater_id = self._api.heater_id
        self._sm_thermostat = self._api.single_master_thermostat()

        self.init_data()

    def init_data(self):
        """Collect the initial data."""
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
                    if self._active_device:
                        hc_data = self._api.get_device_data(self._heater_id)
                        if not self._sm_thermostat:
                            self._cooling_state = hc_data.get("cooling_state")
                            self._heating_state = hc_data.get("heating_state")
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

    def __init__(self, api, dev_id):
        """Initialize the Plug."""
        self._api = api
        self._dev_id = dev_id

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

    def init_data(self):
        """Collect the initial data."""
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
