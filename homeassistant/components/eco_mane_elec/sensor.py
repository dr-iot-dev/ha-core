"""The Eco Mane ElecCheck Sensor."""

from __future__ import annotations

from dataclasses import dataclass
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    SELECTOR_CIRCUIT,
    SELECTOR_PLACE,
    SENSOR_POWER_ATTR_PREFIX,
    SENSOR_POWER_PREFIX,
    SENSOR_POWER_SERVICE_TYPE,
)
from .coordinator import ElecCheckDataCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class ElecCheckSensorEntityDescription(SensorEntityDescription):
    """Describes ElecCheck sensor entity."""

    service_type: str


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities from a config entry."""
    # Access data stored in hass.data if needed
    coordinator: ElecCheckDataCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    _LOGGER.debug("sensor.py config_entry.entry_id: %s", config_entry.entry_id)

    power_dict = coordinator.power_dict
    sensor_total = coordinator.sensor_total
    _LOGGER.debug("sensor_total: %s", sensor_total)

    # センサーのエンティティのリストを作成
    sensors = []
    for sensor_num in range(sensor_total):
        prefix = f"{SENSOR_POWER_PREFIX}_{sensor_num}"
        place = power_dict[f"{prefix}_{SELECTOR_PLACE}"]
        circuit = power_dict[f"{prefix}_{SELECTOR_CIRCUIT}"]
        power = power_dict[prefix]
        sensors.append(ElecCheckEntity(coordinator, prefix, place, circuit, power))

    if not sensors:
        raise ConfigEntryNotReady("No sensors found")

    # エンティティを追加
    async_add_entities(sensors)
    _LOGGER.debug("sensor.py async_setup_entry has finished async_add_entities")


class ElecCheckEntity(CoordinatorEntity, SensorEntity):
    """EcoTopMoni."""

    _attr_has_entity_name = True
    _attr_attribution = "Data provided by Panasonic ECO Mane HEMS"
    _attr_device_class = SensorDeviceClass.POWER
    entity_description: ElecCheckSensorEntityDescription

    def __init__(
        self,
        coordinator: ElecCheckDataCoordinator,
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

        self.entity_description = description = ElecCheckSensorEntityDescription(
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
