"""The Eco Mane Sensor."""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.components.sensor import (
    PLATFORM_SCHEMA as SENSOR_PLATFORM_SCHEMA,
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfEnergy, UnitOfMass, UnitOfVolume
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_IDS, CONF_IP, CONF_NAME
from .coordinator import EcoTopMoniDataCoordinator

_LOGGER = logging.getLogger(__name__)

""" SENSOR_PLATFORM_SCHEMAがどこで参照されるのかよくわからない。"""
PLATFORM_SCHEMA = SENSOR_PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_IP): cv.string,
        vol.Optional(CONF_NAME, default="Eco Mane HEMS System"): cv.string,
    }
)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:  # noqa: D103
    """Set up the sensor platform."""

    ip = config[CONF_IP]
    config[CONF_IDS] = [
        "num_L1",
        "num_L2",
        # "num_L3",
        "num_L4",
        "num_L5",
        "num_R1",
        "num_R2",
        "num_R3",
    ]

    coordinator = EcoTopMoniDataCoordinator(hass, ip, config)
    await coordinator.async_config_entry_first_refresh()

    # センサーのエンティティのリストを作成
    sensors = [
        EcoTopMoniEntity(
            coordinator,
            "num_L1",
            "Electricity purchased",
            SensorDeviceClass.ENERGY,
            UnitOfEnergy.KILO_WATT_HOUR,
            SensorStateClass.TOTAL_INCREASING,
        ),
        EcoTopMoniEntity(
            coordinator,
            "num_L2",
            "Solar Power Energy",
            SensorDeviceClass.ENERGY,
            UnitOfEnergy.KILO_WATT_HOUR,
            SensorStateClass.TOTAL_INCREASING,
        ),
        EcoTopMoniEntity(
            coordinator,
            "num_L4",
            "Gas Consumpotion",
            SensorDeviceClass.GAS,
            UnitOfVolume.CUBIC_METERS,
            SensorStateClass.TOTAL_INCREASING,
        ),
        EcoTopMoniEntity(
            coordinator,
            "num_L5",
            "Water Consumpotion",
            SensorDeviceClass.WATER,
            UnitOfVolume.CUBIC_METERS,
            SensorStateClass.TOTAL_INCREASING,
        ),
        EcoTopMoniEntity(
            coordinator,
            "num_R1",
            "CO2 Emissions",
            SensorDeviceClass.WEIGHT,
            UnitOfMass.KILOGRAMS,
            SensorStateClass.TOTAL_INCREASING,
        ),
        EcoTopMoniEntity(
            coordinator,
            "num_R2",
            "CO2 Reduction ",
            SensorDeviceClass.WEIGHT,
            UnitOfMass.KILOGRAMS,
            SensorStateClass.TOTAL_INCREASING,
        ),
        EcoTopMoniEntity(
            coordinator,
            "num_R3",
            "Electricity sales",
            SensorDeviceClass.ENERGY,
            UnitOfEnergy.KILO_WATT_HOUR,
            SensorStateClass.TOTAL_INCREASING,
        ),
    ]
    # config[CONF_IDS] = [sensor.div_id() for sensor in sensors]
    # _LOGGER.debug(f"{config=}")
    # coordinator.set_config(config)

    async_add_entities(sensors)
    # config[CONF_SENSORS] = sensors


class EcoTopMoniEntity(CoordinatorEntity, SensorEntity):
    """EcoTopMoni."""

    def __init__(
        self,
        coordinator: EcoTopMoniDataCoordinator,
        div_id: str,
        name: str,
        device_class: SensorDeviceClass,
        unit_of_measurement,
        state_class: SensorStateClass,
    ) -> None:
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self.id = div_id
        self._div_id = div_id
        self._name = name
        self._device_class = device_class
        self._unit_of_measurement = unit_of_measurement
        self._state_class = state_class
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

    @property
    def div_id(self):
        """Division id."""
        return self._div_id

    @property
    def name(self) -> str:
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
    def native_unit_of_measurement(self) -> str:
        """Unit of measurement."""
        return self._unit_of_measurement


# class EcoManeSensor(SensorEntity):
#     """EcoManeSensor."""

#     _attr_has_entity_name = True
#     _attr_name = "Example Energy Measurement"
#     _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
#     _attr_device_class = SensorDeviceClass.ENERGY
#     _attr_state_class = SensorStateClass.TOTAL_INCREASING

#     def __init__(self, ip, selector, name) -> None:
#         """Init EcoManeSensor."""
#         self._ip = ip
#         self._selector = selector
#         self._name = name
#         self._state = None

#     @property
#     def name(self) -> str:
#         """Get name."""
#         return self._name

#     @property
#     def state(self) -> str:
#         """Get state."""
#         return self._state

#     def update(self) -> None:
#         """Update info."""
#         url = "http://" + self._ip + "/ecoTopMoni.cgi"
#         _LOGGER.debug(f"{url=}")
#         response = requests.get(url, timeout=60)
#         # text = response.text
#         # _LOGGER.debug(f"response.{text=}")
#         soup = BeautifulSoup(response.text, "html.parser")
#         # element = soup.select_one(self._selector)
#         element = soup.find("div", id="num_L1")
#         # text = element.text.strip() if element else "N/A"
#         # _LOGGER.debug(f"element.{text=}")
#         self._state = element.text.strip() if element else "N/A"
