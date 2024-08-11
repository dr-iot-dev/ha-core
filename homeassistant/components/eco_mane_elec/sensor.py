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

from .const import DOMAIN
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

    elec_dict = coordinator.elec_dict
    total = coordinator.total
    _LOGGER.debug("total: %s", total)

    # センサーのエンティティのリストを作成
    sensors = []
    for _i in range(int(total)):
        prefix = f"elecCheck_{_i}"
        txt = elec_dict[prefix + "_txt"]
        txt2 = elec_dict[prefix + "_txt2"]
        num = elec_dict[prefix]
        sensors.append(ElecCheckEntity(coordinator, prefix, txt, txt2, num))

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
        txt: str,
        txt2: str,
        num: str,
    ) -> None:
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator=coordinator)

        self._id = sensor_id
        self._name = txt + " " + txt2
        self._num = num
        self._state = None
        self._attr_name = f"Sensor {sensor_id}"
        _LOGGER.debug("_id: %s, _name: %s, _num: %s", self._id, self._name, self._num)

        self.entity_description = description = ElecCheckSensorEntityDescription(
            service_type="electricity", key=sensor_id
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
        elec_dict = self.coordinator.data
        if elec_dict is None:
            _LOGGER.debug("elec_dict is None")
            return None
        # _LOGGER.debug("native_value of %s, id=%s: %s", self._attr_name, self._id, value)
        return elec_dict.get(self._id)

    @property
    def native_unit_of_measurement(self) -> str:
        """Unit of measurement."""
        return UnitOfPower.WATT
