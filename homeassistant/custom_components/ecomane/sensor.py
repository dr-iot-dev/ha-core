"""The Eco Mane Sensor."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import UndefinedType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    SELECTOR_CIRCUIT,
    SELECTOR_PLACE,
    SENSOR_POWER_ATTR_PREFIX,
    SENSOR_POWER_PREFIX,
    SENSOR_POWER_SERVICE_TYPE,
)
from .coordinator import (
    EcoManeDataCoordinator,
    EcoManeEnergySensorEntityDescription,
    EcoManePowerSensorEntityDescription,
)

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

    power_dict = coordinator.dict
    sensor_total = coordinator.sensor_total
    _LOGGER.debug("sensor_total: %s", sensor_total)

    ecomane_energy_sensors_descs = coordinator.sensor_descs

    # センサーのエンティティのリストを作成
    sensors: list[SensorEntity] = [
        EcoManeEnergySensorEntity(coordinator, sensor_desc)
        for sensor_desc in ecomane_energy_sensors_descs
    ]

    # Power sensors
    for sensor_num in range(sensor_total):
        prefix = f"{SENSOR_POWER_PREFIX}_{sensor_num}"
        place = power_dict[f"{prefix}_{SELECTOR_PLACE}"]
        circuit = power_dict[f"{prefix}_{SELECTOR_CIRCUIT}"]
        power = power_dict[prefix]
        sensors.append(
            EcoManePowerSensorEntity(coordinator, prefix, place, circuit, power)
        )

    if not sensors:
        raise ConfigEntryNotReady("No sensors found")

    # エンティティを追加
    async_add_entities(sensors)
    _LOGGER.debug("sensor.py async_setup_entry has finished async_add_entities")


class EcoManeEnergySensorEntity(CoordinatorEntity, SensorEntity):
    """EcoManeEnergySensor."""

    def __init__(
        self,
        coordinator: EcoManeDataCoordinator,
        sensor_desc: EcoManeEnergySensorEntityDescription,
    ) -> None:
        """Pass coordinator to CoordinatorEntity."""

        super().__init__(coordinator)

        self._name = sensor_desc.name
        self.id = sensor_desc.key
        self._div_id = sensor_desc.key
        self._description = sensor_desc.description
        self._device_class = sensor_desc.device_class
        self._unit_of_measurement = sensor_desc.unit_of_measurement
        self._state_class = sensor_desc.state_class
        self._state = None

        # _attr_has_entity_name = True
        # _attr_name = "Example Energy Measurement"
        # _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
        # _attr_device_class = SensorDeviceClass.ENERGY
        # _attr_state_class = SensorStateClass.TOTAL_INCREASING

    # @callback
    # def _handle_coordinator_update(self) -> None:
    #     """Handle updated data from the coordinator."""
    #     self._attr_is_on = self.coordinator.data[self.idx]["state"]
    #     self.async_write_ha_state()

    # @property
    # def selector(self):
    #     """HTML Division id."""
    #     return self._selector

    @property
    def name(self) -> str | UndefinedType | None:
        """Name."""
        return self._name

    @property
    def native_value(self) -> str:
        """Instead of state."""
        value = self.coordinator.data.get(self._div_id)
        if value is None:
            return ""
        return str(value)

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Unit of measurement."""
        return self._unit_of_measurement


class EcoManePowerSensorEntity(CoordinatorEntity, SensorEntity):
    """EcoManeEnergySensor."""

    _attr_has_entity_name = True
    _attr_attribution = "Data provided by Panasonic ECO Mane HEMS"
    _attr_device_class = SensorDeviceClass.POWER
    entity_description: EcoManePowerSensorEntityDescription

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

        self._id = sensor_id
        self._name = f"{place} {circuit}"
        self._power = power
        self._state = None
        self._attr_name = f"{SENSOR_POWER_ATTR_PREFIX}_{sensor_id}"
        _LOGGER.debug("_id: %s, _name: %s, _num: %s", self._id, self._name, self._power)

        self.entity_description = description = EcoManePowerSensorEntityDescription(
            service_type=SENSOR_POWER_SERVICE_TYPE, key=sensor_id
        )

        # self.entity_id = (
        #     f"{SENSOR_DOMAIN}.{DOMAIN}_{description.service_type}_{description.key}"
        # )

        if (
            coordinator is not None
            and coordinator.config_entry is not None
            and description is not None
        ):
            self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.service_type}_{description.key}"

    @property
    def name(self) -> str:
        """Name."""
        return self._name

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

    @property
    def native_unit_of_measurement(self) -> str:
        """Unit of measurement."""
        return UnitOfPower.WATT
