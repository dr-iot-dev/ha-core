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
from homeassistant.helpers.device_registry import DeviceInfo
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
    EcoManePowerSensorEntityDescription,
    EcoManeUsageSensorEntityDescription,
)
from .name_to_id import ja_to_entity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities from a config entry."""
    # Access data stored in hass.data
    coordinator: EcoManeDataCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    sensor_dict = coordinator.dict
    power_sensor_total = coordinator.power_sensor_total

    ecomane_energy_sensors_descs = coordinator.usage_sensor_descs

    sensors: list[SensorEntity] = []
    _LOGGER.debug("sensor.py sensors: %s", sensors)
    # 使用量センサーのエンティティのリストを作成
    for usage_sensor_desc in ecomane_energy_sensors_descs:
        sensor = EcoManeUsageSensorEntity(coordinator, usage_sensor_desc)
        sensors.append(sensor)

    # 電力センサーのエンティティのリストを作成
    for sensor_num in range(power_sensor_total):
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

    # センサーが見つからない場合はエラー
    if not sensors:
        raise ConfigEntryNotReady("No sensors found")

    # エンティティを追加 (update_before_add=False でオーバービューに自動で登録されないようにする)
    async_add_entities(sensors, update_before_add=False)
    _LOGGER.debug("sensor.py async_setup_entry has finished async_add_entities")


class EcoManeUsageSensorEntity(CoordinatorEntity, SensorEntity):
    """EcoManeUsageSensor."""

    _attr_has_entity_name = True
    # _attr_name = None # Noneでも値を設定するとtranslationがされない
    # _attr_id = None　# Noneでも値を設定しない
    _attr_div_id: str = ""
    _attr_description: str | None = None
    _attr_native_unit_of_measurement: str | None = None
    _attr_device_class: SensorDeviceClass | None = None
    _attr_state_class: str | None = None
    _attr_entity_description: EcoManeUsageSensorEntityDescription | None = None
    _attr_state = None
    _attr_unique_id: str | None = None
    _ip_address: str | None = None

    def __init__(
        self,
        coordinator: EcoManeDataCoordinator,
        usage_sensor_desc: EcoManeUsageSensorEntityDescription,
    ) -> None:
        """Pass coordinator to CoordinatorEntity."""

        super().__init__(coordinator)

        sensor_id = usage_sensor_desc.key
        self._attr_div_id = sensor_id
        self._attr_description = description = usage_sensor_desc.description
        self._attr_native_unit_of_measurement = (
            usage_sensor_desc.native_unit_of_measurement
        )
        self._attr_device_class = usage_sensor_desc.device_class
        self._attr_state_class = usage_sensor_desc.state_class
        self._attr_entity_description = usage_sensor_desc

        self._attr_translation_key = usage_sensor_desc.translation_key
        self.translation_key = usage_sensor_desc.translation_key
        self.entity_id = f"{SENSOR_DOMAIN}.{DOMAIN}_{usage_sensor_desc.translation_key}"
        self._ip_address = coordinator.ip_address

        # _attr_unique_id を設定
        if (
            coordinator is not None
            and coordinator.config_entry is not None
            and description is not None
        ):
            self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{usage_sensor_desc.translation_key}"

        _LOGGER.debug(
            "usage_sensor_desc.name: %s, _attr_translation_key: %s, _attr_div_id: %s, entity_id: %s, _attr_unique_id: %s",
            usage_sensor_desc.name,
            self._attr_translation_key,
            self._attr_div_id,
            self.entity_id,
            self._attr_unique_id,
        )

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
    def device_info(
        self,
    ) -> DeviceInfo:  # エンティティ群をデバイスに分類するための情報を提供
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, "daily_usage_" + (self._ip_address or ""))},
            name="Daily Usage",
            manufacturer="Panasonic",
            translation_key="daily_usage",
        )


class EcoManePowerSensorEntity(CoordinatorEntity, SensorEntity):
    """EcoManeUsageSensor."""

    _attr_has_entity_name = True
    # _attr_name = None　# Noneでも値を設定するとtranslationがされない
    # _attr_unique_id: str | None = None　# Noneでも値を設定しない
    _attr_translation_key: str
    _attr_attribution = "Data provided by Panasonic ECO Mane HEMS"
    _attr_entity_description: EcoManePowerSensorEntityDescription | None = None
    _attr_device_class = SensorDeviceClass.POWER
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _ip_address: str | None = None

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

        name = f"{place} {circuit}"
        # self._attr_name = name　# Noneでも値を設定するとtranslationがされない
        self._attr_translation_key = ja_to_entity(name)
        self._ip_address = coordinator.ip_address
        self._power = power

        # entity_description を設定
        self.entity_description = description = EcoManePowerSensorEntityDescription(
            service_type=SENSOR_POWER_SERVICE_TYPE, key=sensor_id
        )

        # entity_id を設定
        self.entity_id = (
            f"{SENSOR_DOMAIN}.{DOMAIN}_{sensor_id}_{self._attr_translation_key}"
        )

        # _attr_unique_id を設定
        if (
            coordinator is not None
            and coordinator.config_entry is not None
            and description is not None
        ):
            self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.service_type}_{description.key}"

    @property
    def native_value(self) -> str | None:
        """State."""
        return self._power

    @property
    def device_info(
        self,
    ) -> DeviceInfo:  # エンティティ群をデバイスに分類するための情報を提供
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, "power_consumption_" + (self._ip_address or ""))},
            name="Power Consumption",
            manufacturer="Panasonic",
            translation_key="power_consumption",
        )
