"""The Eco Mane Sensor."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import (
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

from .const import DOMAIN, SELECTOR_CIRCUIT, SELECTOR_PLACE, SENSOR_POWER_SERVICE_TYPE
from .coordinator import (
    EcoManeDataUpdateCoordinator,
    EcoManeEnergySensorEntityDescription,
    EcoManePowerSensorEntityDescription,
    get_sensor_power_prefix,
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
    coordinator: EcoManeDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    _LOGGER.debug("sensor.py config_entry.entry_id: %s", config_entry.entry_id)

    sensor_dict = coordinator.data
    # _LOGGER.debug("async_setup_entry coordinator.data: %s", coordinator.data)
    # _LOGGER.debug("async_setup_entry coordinator.dict: %s", coordinator.dict)
    sensor_total = coordinator.sensor_total
    _LOGGER.debug("sensor_total: %s", sensor_total)

    ecomane_energy_sensors_descs = coordinator.sensor_descs

    sensors: list[SensorEntity] = []
    # _LOGGER.debug("sensor.py sensors: %s", sensors)

    # Energy sensors
    for sensor_desc in ecomane_energy_sensors_descs:
        sensor = EcoManeEnergySensorEntity(coordinator, sensor_desc)
        sensors.append(sensor)

    # Power sensors
    for sensor_num in range(sensor_total):
        prefix = get_sensor_power_prefix(sensor_num)
        place = sensor_dict[f"{prefix}_{SELECTOR_PLACE}"]
        circuit = sensor_dict[f"{prefix}_{SELECTOR_CIRCUIT}"]
        sensors.append(EcoManePowerSensorEntity(coordinator, prefix, place, circuit))

    if not sensors:
        raise ConfigEntryNotReady("No sensors found")

    # エンティティを追加
    async_add_entities(sensors)
    _LOGGER.debug("sensor.py async_setup_entry has finished async_add_entities")


class EcoManeEnergySensorEntity(CoordinatorEntity, SensorEntity):
    """EcoManeEnergySensor."""

    _attr_has_entity_name = True
    _attr_unique_id: str | None = None
    _attr_div_id: str = ""
    _attr_description: str | None = None
    _attr_native_unit_of_measurement: str | None = None
    _attr_device_class: SensorDeviceClass | None = None
    _attr_state_class: str | None = None
    _attr_state = None

    def __init__(
        self,
        coordinator: EcoManeDataUpdateCoordinator,
        sensor_desc: EcoManeEnergySensorEntityDescription,
    ) -> None:
        """Pass coordinator to CoordinatorEntity."""

        super().__init__(coordinator)

        self._attr_translation_key = sensor_desc.translation_key
        self._attr_div_id = sensor_desc.div_id
        self._attr_description = sensor_desc.description
        self._attr_native_unit_of_measurement = sensor_desc.native_unit_of_measurement
        self._attr_device_class = sensor_desc.device_class
        self._attr_state_class = sensor_desc.state_class
        self.entity_description = sensor_desc

        if (
            coordinator is not None
            and coordinator.config_entry is not None
            and self.translation_key is not None
        ):
            self._attr_unique_id = (
                f"{coordinator.config_entry.entry_id}_{self.translation_key}"
            )
        else:
            raise ConfigEntryNotReady("No coordinator or translation key")

        # _LOGGER.debug(
        #     "sensor_desc.name: %s, translation_key: %s, div_id: %s, entity_id: %s, unique_id: %s",
        #     sensor_desc.name,
        #     self.translation_key,
        #     self.div_id,
        #     self.entity_id,
        #     self.unique_id,
        # )

    @property
    def native_value(self) -> str:
        """State."""
        value = self.coordinator.dict.get(
            self._attr_div_id
        )  #         value = self.coordinator.data.get(self._attr_div_id) # なぜか None を返す
        if value is None:
            return ""
        return str(value)

    @property
    def div_id(self):
        """Div ID."""
        return self._attr_div_id

    @property
    def translation_key(self):
        """Translation key."""
        return self._attr_translation_key


class EcoManePowerSensorEntity(CoordinatorEntity, SensorEntity):
    """EcoManeEnergySensor."""

    _attr_has_entity_name = True
    _attr_unique_id: str | None = None
    _attr_translation_key: str | None = None
    _attr_attribution = "Data provided by Panasonic ECO Mane HEMS"
    _attr_entity_description: EcoManePowerSensorEntityDescription | None = None
    _attr_device_class = SensorDeviceClass.POWER
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_key_prefix: str = ""

    def __init__(
        self,
        coordinator: EcoManeDataUpdateCoordinator,
        key_prefix: str,  # eg. "em_power_0"
        place: str,  # eg. "リビング"
        circuit: str,  # eg. "エアコン"
    ) -> None:
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator=coordinator)

        self._attr_key_prefix = key_prefix
        name = f"{place} {circuit}"  # eg. "リビング エアコン"
        self._attr_translation_key = ja_to_entity(name)  # eg. "living_air_conditioner"
        if (
            coordinator is not None
            and coordinator.config_entry is not None
            and self.translation_key is not None
        ):
            self._attr_unique_id = (
                f"{coordinator.config_entry.entry_id}_{self.translation_key}"
            )
        else:
            raise ConfigEntryNotReady("No coordinator or translation key")

        self.entity_description = EcoManePowerSensorEntityDescription(
            service_type=SENSOR_POWER_SERVICE_TYPE, key=key_prefix
        )

        # _LOGGER.debug(
        #     "__init__ _key_prefix: %s, name: %s, translation_key: %s, unique_id: %s, entity_id: %s",
        #     self.key_prefix,
        #     name,
        #     self.translation_key,
        #     self.unique_id,
        #     self.entity_id,
        # )

    @property
    def native_value(self) -> str | None:
        """State."""
        return self.coordinator.data.get(self.key_prefix)

    @property
    def translation_key(self):
        """Translation key."""
        return self._attr_translation_key

    @property
    def key_prefix(self):
        """Key prefix."""
        return self._attr_key_prefix
