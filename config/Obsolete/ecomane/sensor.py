"""The Eco Mane Sensor."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    DOMAIN as SENSOR_DOMAIN,
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.entity_platform import AddEntitiesCallback

# from homeassistant.helpers.typing import UndefinedType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    SELECTOR_CIRCUIT,
    SELECTOR_PLACE,
    SENSOR_POWER_PREFIX,
    SENSOR_POWER_SERVICE_TYPE,
)
from .coordinator import (
    EcoManeDataCoordinator,
    EcoManeEnergySensorEntityDescription,
    EcoManePowerSensorEntityDescription,
)
from .name_to_id import ja_to_entity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities from a config entry."""
    # Access data stored in hass.data if needed
    coordinator: EcoManeDataCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    _LOGGER.debug("sensor.py config_entry.entry_id: %s", config_entry.entry_id)

    sensor_dict = coordinator.dict
    sensor_total = coordinator.sensor_total
    _LOGGER.debug("sensor_total: %s", sensor_total)

    ecomane_energy_sensors_descs = coordinator.sensor_descs
    # _LOGGER.debug("ecomane_energy_sensors_descs: %s", ecomane_energy_sensors_descs)

    sensors: list[SensorEntity] = []
    _LOGGER.debug("sensor.py sensors: %s", sensors)
    # センサーのエンティティのリストを作成
    for sensor_desc in ecomane_energy_sensors_descs:
        # _LOGGER.debug("sensor_desc: %s", sensor_desc)
        sensor = EcoManeEnergySensorEntity(coordinator, sensor_desc)
        # _LOGGER.debug("sensor.py energy sensor: %s", sensor)
        sensors.append(sensor)

    # _LOGGER.debug("sensor.py energy sensors: %s", sensors)

    # Power sensors
    for sensor_num in range(sensor_total):
        prefix = f"{SENSOR_POWER_PREFIX}_{sensor_num:02d}"
        place = sensor_dict[f"{prefix}_{SELECTOR_PLACE}"]
        circuit = sensor_dict[f"{prefix}_{SELECTOR_CIRCUIT}"]
        power = sensor_dict[prefix]
        _LOGGER.debug(
            "sensor.py sensor_num: %s, prefix: %s, place: %s, circuit: %s, power: %s",
            sensor_num,
            prefix,
            place,
            circuit,
            power,
        )
        sensors.append(
            EcoManePowerSensorEntity(coordinator, prefix, place, circuit, power)
        )

    # _LOGGER.debug("sensor.py power sensors: %s", sensors)

    if not sensors:
        raise ConfigEntryNotReady("No sensors found")

    # エンティティを追加
    async_add_entities(sensors)
    _LOGGER.debug("sensor.py async_setup_entry has finished async_add_entities")


class EcoManeEnergySensorEntity(CoordinatorEntity, SensorEntity):
    """EcoManeEnergySensor."""

    _attr_has_entity_name = True
    # _attr_id = None
    _attr_div_id: str = ""
    # _attr_name = None
    _attr_description: str | None = None
    _attr_native_unit_of_measurement: str | None = None
    _attr_device_class: SensorDeviceClass | None = None
    _attr_state_class: str | None = None
    _attr_entity_description: EcoManeEnergySensorEntityDescription | None = None
    _attr_state = None
    _attr_unique_id: str | None = None

    def __init__(
        self,
        coordinator: EcoManeDataCoordinator,
        sensor_desc: EcoManeEnergySensorEntityDescription,
    ) -> None:
        """Pass coordinator to CoordinatorEntity."""

        super().__init__(coordinator)

        sensor_id = sensor_desc.key
        self._attr_div_id = sensor_id
        # self._attr_name = sensor_desc.name
        self._attr_description = description = sensor_desc.description
        self._attr_native_unit_of_measurement = sensor_desc.native_unit_of_measurement
        self._attr_device_class = sensor_desc.device_class
        self._attr_state_class = sensor_desc.state_class
        self._attr_entity_description = sensor_desc

        # self._attr_translation_key = ja_to_entity(sensor_desc.name)
        self._attr_translation_key = sensor_desc.translation_key
        self.translation_key = sensor_desc.translation_key
        # self._attr_unique_id = self._attr_translation_key
        # self._attr_name = self._attr_translation_key
        self.entity_id = f"{SENSOR_DOMAIN}.{DOMAIN}_{sensor_desc.translation_key}"

        if (
            coordinator is not None
            and coordinator.config_entry is not None
            and description is not None
        ):
            self._attr_unique_id = (
                f"{coordinator.config_entry.entry_id}_{sensor_desc.translation_key}"
            )

        _LOGGER.debug(
            "sensor_desc.name: %s, _attr_translation_key: %s, _attr_div_id: %s, entity_id: %s, _attr_unique_id: %s",
            sensor_desc.name,
            self._attr_translation_key,
            self._attr_div_id,
            self.entity_id,
            self._attr_unique_id,
        )

        # self._name = sensor_desc.name
        # self._id = sensor_desc.key
        # self._div_id = sensor_desc.key
        # self._description = sensor_desc.description
        # self._device_class = sensor_desc.device_class
        # self._unit_of_measurement = sensor_desc.native_unit_of_measurement
        # self._state_class = sensor_desc.state_class
        # self._state = None
        # self.entity_description = sensor_desc

        # self._attr_name = sensor_desc.name
        # _LOGGER.debug("_id: %s, name: %s", self._id, self.name)

    # @callback
    # def _handle_coordinator_update(self) -> None:
    #     """Handle updated data from the coordinator."""
    #     self._attr_is_on = self.coordinator.data[self.idx]["state"]
    #     self.async_write_ha_state()

    # @property
    # def selector(self):
    #     """HTML Division id."""
    #     return self._selector

    # @property
    # def name(self) -> str | UndefinedType | None:
    #     """Name."""
    #     return self._name

    @property
    def native_value(self) -> str:
        """State."""
        value = self.coordinator.dict.get(
            self._attr_div_id
        )  #         value = self.coordinator.data.get(self._attr_div_id) # なぜか None を返す
        if value is None:
            return ""
        return str(value)

    # @property
    # def native_unit_of_measurement(self) -> str | None:
    #     """Unit of measurement."""
    #     return self._unit_of_measurement

    # @property
    # def entity_id(self):
    #     """Entity ID."""
    #     return self._attr_unique_id

    # @property
    # def translation_key(self):
    #     """Translation key."""
    #     return self._attr_translation_key


class EcoManePowerSensorEntity(CoordinatorEntity, SensorEntity):
    """EcoManeEnergySensor."""

    _attr_has_entity_name = True
    # _attr_name = None
    _attr_translation_key: str
    # _attr_unique_id: str | None = None
    _attr_attribution = "Data provided by Panasonic ECO Mane HEMS"
    _attr_entity_description: EcoManePowerSensorEntityDescription | None = None
    _attr_device_class = SensorDeviceClass.POWER
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: EcoManeDataCoordinator,
        sensor_id: str,
        place: str,
        circuit: str,
        power: str,
    ) -> None:
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator=coordinator)

        # self._attr_unique_id = sensor_id
        # self._name = f"{place} {circuit}"
        # self._power = power
        # self._state = None
        # self._attr_name = f"{SENSOR_POWER_ATTR_PREFIX}_{sensor_id}"

        # self._attr_name = f"{place} {circuit}"
        name = f"{place} {circuit}"
        # self._attr_name = name
        self._attr_translation_key = ja_to_entity(name)
        # self._attr_unique_id = self._attr_translation_key
        # self._attr_name = self._attr_translation_key

        self._power = power

        self.entity_description = description = EcoManePowerSensorEntityDescription(
            service_type=SENSOR_POWER_SERVICE_TYPE, key=sensor_id
        )

        # self.entity_id = (
        #     f"{SENSOR_DOMAIN}.{DOMAIN}_{description.service_type}_{description.key}"
        # )
        self.entity_id = (
            f"{SENSOR_DOMAIN}.{DOMAIN}_{sensor_id}_{self._attr_translation_key}"
        )
        if (
            coordinator is not None
            and coordinator.config_entry is not None
            and description is not None
        ):
            # self.unique_id = f"{coordinator.config_entry.entry_id}_{description.service_type}_{description.key}"
            self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.service_type}_{description.key}"

        # _LOGGER.debug(
        #     f"Debug: _attr_name before access: {getattr(self, '_attr_name', 'Not set')}"
        # )

        # _LOGGER.debug(
        #     "sensor_id: %s, name: %s, self._attr_translation_key: %s, _attr_unique_id: %s, _attr_name: %s, entity_id: %s, _power: %s",
        #     sensor_id,
        #     name,
        #     self._attr_translation_key,
        #     self._attr_unique_id,
        #     self._attr_name,
        #     self.entity_id,
        #     self._power,
        # )

    # @property
    # def name(self) -> str:
    #     """Name."""
    #     return self._name

    @property
    def native_value(self) -> str | None:
        """State."""
        # power_dict = self.coordinator.data
        # if power_dict is None:
        #     _LOGGER.debug("power_dict is None: native_value of %s, id=%s", self._attr_name, self._id)
        #     return None
        # # _LOGGER.debug("native_value of %s, id=%s: %s", self._attr_name, self._id, value)
        # return power_dict.get(self._id)
        return self._power

    # @property
    # def native_unit_of_measurement(self) -> str:
    #     """Unit of measurement."""
    #     return UnitOfPower.WATT

    # @property
    # def entity_id(self):
    #     """Entity ID."""
    #     return self._attr_unique_id

    @property
    def translation_key(self) -> str:
        """Translation key."""
        return str(self._attr_translation_key)
