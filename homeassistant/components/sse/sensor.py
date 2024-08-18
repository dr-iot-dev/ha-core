"""Sensor platform for EcoMane integration."""

from __future__ import annotations

from dataclasses import dataclass
import logging

from homeassistant.components.sensor import (
    DOMAIN as SENSOR_DOMAIN,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy, UnitOfMass
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

# ログのフォーマットを設定
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] [%(process)d] [%(filename)s:%(lineno)d] [%(levelname)s] %(message)s",
)
_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class SSESensorEntityDescription(SensorEntityDescription):
    """Describes EcoManePower sensor entity."""

    description: str


sensors_descs = [
    SSESensorEntityDescription(
        # name="購入電気量",
        name="electricity_purchased",
        translation_key="electricity_purchased",
        # description="Electricity purchased",
        description="Electricity purchased 購入電気量",
        key="num_L1",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SSESensorEntityDescription(
        # name="CO2排出量",
        name="co2_emissions",
        translation_key="co2_emissions",
        # description="CO2 Emissions",
        description="CO2 Emissions CO2排出量",
        key="num_R1",
        device_class=SensorDeviceClass.WEIGHT,
        native_unit_of_measurement=UnitOfMass.KILOGRAMS,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities from a config entry."""
    # Access data stored in hass.data if needed
    # センサーのエンティティのリストを作成

    sensors: list[SensorEntity] = []
    for sensor_desc in sensors_descs:
        # _LOGGER.debug("sensor_desc: %s", sensor_desc)
        sensor = SSESensorEntity(sensor_desc)
        # _LOGGER.debug("sensor.py energy sensor: %s", sensor)
        sensors.append(sensor)

    # _LOGGER.debug("sensor.py SSE sensors: %s", sensors)

    if not sensors:
        raise ConfigEntryNotReady("No sensors found")

    # エンティティを追加
    async_add_entities(sensors)
    _LOGGER.debug(
        "sensor.py async_setup_entry has finished async_add_entities %s", sensors
    )


class SSESensorEntity(SensorEntity):
    """EcoManeEnergySensor."""

    # _attr_has_entity_name = True
    has_entity_name = True  # これがないとstrings.jsonの変換が行われない _attr_has_entity_name ではない！
    # _attr_id = None
    _attr_div_id: str = ""
    # _attr_name = None
    _attr_description: str | None = None
    _attr_native_unit_of_measurement: str | None = None
    _attr_device_class: SensorDeviceClass | None = None
    _attr_state_class: str | None = None
    _attr_entity_description: SSESensorEntityDescription | None = None
    _attr_state = None
    _attr_unique_id: str | None = None

    def __init__(
        self,
        sensor_desc: SSESensorEntityDescription,
    ) -> None:
        """Pass coordinator to CoordinatorEntity."""

        super().__init__()

        sensor_id = sensor_desc.key
        self._attr_div_id = sensor_id
        # self._attr_name = sensor_desc.name
        self._attr_description = sensor_desc.description
        self._attr_native_unit_of_measurement = sensor_desc.native_unit_of_measurement
        self._attr_device_class = sensor_desc.device_class
        self._attr_state_class = sensor_desc.state_class
        self._attr_entity_description = sensor_desc

        # self._attr_translation_key = ja_to_entity(sensor_desc.name)
        self._attr_translation_key = sensor_desc.translation_key
        self.translation_key = sensor_desc.translation_key
        self._attr_unique_id = self._attr_translation_key  # sensor の登録に必要
        # self._attr_name = self._attr_translation_key
        self.entity_id = f"{SENSOR_DOMAIN}.{DOMAIN}_{sensor_desc.translation_key}"

        _LOGGER.debug(
            "sensor_desc.name: %s, _attr_translation_key: %s, _attr_div_id: %s, entity_id: %s, _attr_unique_id: %s",
            sensor_desc.name,
            self._attr_translation_key,
            self._attr_div_id,
            self.entity_id,
            self._attr_unique_id,
        )

        # self._name = sensor_desc.name
