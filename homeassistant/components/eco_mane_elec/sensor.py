"""The Eco Mane ElecCheck Sensor."""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.components.sensor import (
    PLATFORM_SCHEMA as SENSOR_PLATFORM_SCHEMA,
    SensorEntity,
)
from homeassistant.const import UnitOfPower
from homeassistant.core import HomeAssistant

# from homeassistant.exceptions import ConfigEntryNotReady
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_IP, CONF_NAME
from .coordinator import ElecCheckDataCoordinator

_LOGGER = logging.getLogger(__name__)

""" SENSOR_PLATFORM_SCHEMAがどこで参照されるのかよくわからない。"""
PLATFORM_SCHEMA = SENSOR_PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_IP): cv.string,
        vol.Optional(CONF_NAME, default="Eco Mane HEMS System Elec"): cv.string,
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

    coordinator = ElecCheckDataCoordinator(hass, ip, config)
    await coordinator.async_config_entry_first_refresh()

    # if not coordinator.last_update_success:
    #     raise ConfigEntryNotReady
    elec_dict = coordinator.elec_dict
    count = elec_dict["count"]

    # センサーのエンティティのリストを作成
    sensors = []
    for _i in range(int(count)):
        prefix = f"elecCheck_{count}"
        txt = elec_dict[prefix + "_txt"]
        txt2 = elec_dict[prefix + "_txt2"]
        num = elec_dict[prefix + "_num"]
        sensors.append(ElecCheckEntity(prefix, txt, txt2, num, coordinator))

    async_add_entities(sensors)
    # config[CONF_SENSORS] = sensors


class ElecCheckEntity(CoordinatorEntity, SensorEntity):
    """EcoTopMoni."""

    def __init__(
        self,
        id: str,
        txt: str,
        txt2: str,
        num: str,
        coordinator: ElecCheckDataCoordinator,
    ) -> None:
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self._id = id
        self._name = txt + " " + txt2
        self._num = num
        self._state = None

    # @callback
    # def _handle_coordinator_update(self) -> None:
    #     """Handle updated data from the coordinator."""
    #     self._attr_is_on = self.coordinator.data[self.idx]["state"]
    #     self.async_write_ha_state()

    @property
    def name(self) -> str:
        """Name."""
        return self._name

    @property
    def native_value(self) -> str:
        """Instead of state."""
        value = self.coordinator.data.get(self._id)
        if value is None:
            return ""
        return str(value)

    @property
    def native_unit_of_measurement(self) -> str:
        """Unit of measurement."""
        return UnitOfPower.WATT


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
