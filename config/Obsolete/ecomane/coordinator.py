"""Coordinator for Eco Mane ElecCheck component."""

from collections.abc import Generator
from dataclasses import dataclass
from datetime import timedelta
import logging
from typing import Any

import aiohttp
from bs4 import BeautifulSoup, NavigableString
from bs4.element import Tag

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfEnergy, UnitOfMass, UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    ENTITY_NAME,
    POLLING_INTERVAL,
    SELECTOR_CIRCUIT,
    SELECTOR_PLACE,
    SELECTOR_POWER,
    SENSOR_ENERGY_CGI,
    SENSOR_POWER_CGI,
    SENSOR_POWER_PREFIX,
    SENSOR_POWER_SELECTOR_PREFIX,
)

_LOGGER = logging.getLogger(__name__)

# retry_interval = 120
# polling_interval = 300


# def get_mac_address(ip_address: str) -> str:
#     """Get the MAC address for the given IP address."""
#     try:
#         output = subprocess.check_output(["arp", "-n", ip_address]).decode("utf-8")
#         mac_address = output.split()[3]
#     except Exception as err:  # noqa: BLE001
#         mac_address = str(err)
#     return mac_address


@dataclass(frozen=True, kw_only=True)
class EcoManePowerSensorEntityDescription(SensorEntityDescription):
    """Describes EcoManePower sensor entity."""

    service_type: str


@dataclass(frozen=True, kw_only=True)
class EcoManeEnergySensorEntityDescription(SensorEntityDescription):
    """Describes EcoManeEnergy sensor entity."""

    description: str
    div_id: str


# センサーのエンティティのディスクリプションのリストを作成
ecomane_energy_sensors_descs = [
    EcoManeEnergySensorEntityDescription(
        name="購入電気量",
        key="Electricity_purchased",
        translation_key="electricity_purchased",
        description="Electricity purchased 購入電気量",
        div_id="num_L1",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    EcoManeEnergySensorEntityDescription(
        name="太陽光発電量",
        key="Solar_power_energy",
        translation_key="solar_power_energy",
        description="Solar Power Energy 太陽光発電量",
        div_id="num_L2",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    EcoManeEnergySensorEntityDescription(
        name="ガス消費量",
        key="Gas_consumption",
        translation_key="gas_consumption",
        description="Gas Consumption ガス消費量",
        div_id="num_L4",
        device_class=SensorDeviceClass.GAS,
        native_unit_of_measurement=UnitOfVolume.CUBIC_METERS,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    EcoManeEnergySensorEntityDescription(
        name="水消費量",
        key="Water_consumption",
        translation_key="water_consumption",
        description="Water Consumption 水消費量",
        div_id="num_L5",
        device_class=SensorDeviceClass.WATER,
        native_unit_of_measurement=UnitOfVolume.CUBIC_METERS,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    EcoManeEnergySensorEntityDescription(
        name="CO2排出量",
        key="Co2_emissions",
        translation_key="co2_emissions",
        description="CO2 Emissions CO2排出量",
        div_id="num_R1",
        device_class=SensorDeviceClass.WEIGHT,
        native_unit_of_measurement=UnitOfMass.KILOGRAMS,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    EcoManeEnergySensorEntityDescription(
        name="CO2削減量",
        key="Co2_reduction",
        translation_key="co2_reduction",
        description="CO2 Reduction CO2削減量",
        div_id="num_R2",
        device_class=SensorDeviceClass.WEIGHT,
        native_unit_of_measurement=UnitOfMass.KILOGRAMS,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    EcoManeEnergySensorEntityDescription(
        name="売電量",
        key="electricity_sales",
        translation_key="electricity_sales",
        # description="Electricity sales",
        description="Electricity sales 売電量",
        div_id="num_R3",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
]


def get_sensor_power_prefix(sensor_num: int) -> str:
    """Get power sensor prefix."""
    return f"{SENSOR_POWER_PREFIX}_{sensor_num:02d}"


class EcoManeDataUpdateCoordinator(DataUpdateCoordinator):
    """ElecCheck_6000 coordinator."""

    def __init__(self, hass: HomeAssistant, ip: str) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=ENTITY_NAME,
            update_interval=timedelta(
                seconds=POLLING_INTERVAL
            ),  # data polling interval
            update_method=self._async_update_data,
        )
        self._ip = ip
        # self._mac_address = get_mac_address(ip)
        # _LOGGER.debug("MAC address: %s", self._mac_address)
        self._dict: dict[str, Any] = {}
        self._session = None
        self._sensor_total = 0
        self._sensor_count = 0
        self._sensor_descs = ecomane_energy_sensors_descs

    def natural_number_generator(self) -> Generator:
        """Natural number generator."""
        count = 1
        while True:
            yield count
            count += 1

    async def _async_update_data(self) -> dict:
        """Update ElecCheck."""
        # _LOGGER.debug("Updating EcoMane data")  # debug
        await self.update_energy_data()
        await self.update_power_data()
        return self._dict

    async def update_energy_data(self) -> None:
        """Update energy data."""

        # _LOGGER.debug("update_energy_data")
        try:
            # デバイスからデータを取得
            url = f"http://{self._ip}/{SENSOR_ENERGY_CGI}"
            async with aiohttp.ClientSession() as session:
                response: aiohttp.ClientResponse = await session.get(url)
                if response.status != 200:
                    _LOGGER.error(
                        "Error fetching data from %s. Status code: %s",
                        url,
                        response.status,
                    )
                    raise UpdateFailed(
                        f"Error fetching data from {url}. Status code: {response.status}"
                    )
                # テキストデータを取得する際にエンコーディングを指定
                text_data = await response.text(encoding="shift-jis")
                await self.parse_energy_data(text_data)
        except Exception as err:
            _LOGGER.error("Error updating sensor data: %s", err)
            raise

    async def parse_energy_data(self, text: str) -> dict:
        """Parse data from the content."""

        # BeautifulSoupを使用してHTMLを解析
        soup = BeautifulSoup(text, "html.parser")
        for sensor_desc in ecomane_energy_sensors_descs:
            div_id = sensor_desc.div_id
            # value = self.get_value_from_div(soup, key)
            div = soup.find("div", id=div_id)
            if div:
                value = div.text.strip()
                self._dict[div_id] = value
            # _LOGGER.debug("div_id=%s, value=%s", div_id, value)  # debug
            self._dict[div_id] = value

        return self._dict

    async def update_power_data(self) -> dict:
        """Update power data."""

        # _LOGGER.debug("update_power_data")
        try:
            # デバイスからデータを取得
            url = f"http://{self._ip}/{SENSOR_POWER_CGI}"
            async with aiohttp.ClientSession() as session:
                self._sensor_count = 0
                # for page_num in range(1, total_page + 1):
                for page_num in self.natural_number_generator():
                    url = f"http://{self._ip}/{SENSOR_POWER_CGI}&page={page_num}"
                    response: aiohttp.ClientResponse = await session.get(url)
                    if response.status != 200:
                        _LOGGER.error(
                            "Error fetching data from %s. Status code: %s",
                            url,
                            response.status,
                        )
                        raise UpdateFailed(
                            f"Error fetching data from {url}. Page:{page_num} Status code: {response.status}"
                        )
                    # テキストデータを取得する際にエンコーディングを指定
                    text_data = await response.text(encoding="shift-jis")
                    total_page = await self.parse_power_data(text_data, page_num)
                    if page_num >= total_page:
                        break
                self._sensor_total = self._sensor_count
                # _LOGGER.debug("Total number of sensors = %s", self._sensor_total)
        except Exception as err:
            _LOGGER.error("Error updating sensor data: %s", err)
            raise UpdateFailed("_async_update_data failed") from err
        # finally:

        return self._dict

    async def parse_power_data(self, text: str, page_num: int) -> int:
        """Parse data from the content."""

        soup = BeautifulSoup(text, "html.parser")
        maxp = soup.find("input", {"name": "maxp"})
        total_page = 0
        if isinstance(maxp, Tag):
            value = maxp.get("value", "0")
            # Ensure value is a string before converting to int
            if isinstance(value, str):
                total_page = int(value)

        for button_num in range(1, 9):
            div_id = f"{SENSOR_POWER_SELECTOR_PREFIX}_{button_num:02d}"
            prefix = get_sensor_power_prefix(self._sensor_count)

            # _LOGGER.debug("page:%s id:%s prefix:%s", page_num, div_id, prefix)

            div_element: Tag | NavigableString | None = soup.find("div", id=div_id)
            if isinstance(div_element, Tag):
                # 要素を取得
                element: Tag | NavigableString | int | None = div_element.find(
                    "div",
                    class_=SELECTOR_PLACE,  # txt
                )
                if isinstance(element, Tag):
                    self._dict[f"{prefix}_{SELECTOR_PLACE}"] = element.get_text()  # txt
                    # _LOGGER.debug("%s:%s", SELECTOR_PLACE, element.get_text())

                element = div_element.find("div", class_=SELECTOR_CIRCUIT)  # txt2
                if isinstance(element, Tag):
                    self._dict[f"{prefix}_{SELECTOR_CIRCUIT}"] = (
                        element.get_text()
                    )  # txt2
                    # _LOGGER.debug("%s:%s", SELECTOR_CIRCUIT, element.get_text())

                element = div_element.find("div", class_=SELECTOR_POWER)  # num
                if isinstance(element, Tag):
                    self._dict[prefix] = element.get_text().split("W")[0]

                # _LOGGER.debug(
                #     "%s:%s, %s:%s, %s:%s",
                #     SELECTOR_PLACE,
                #     self._dict[f"{prefix}_{SELECTOR_PLACE}"],
                #     SELECTOR_CIRCUIT,
                #     self._dict[f"{prefix}_{SELECTOR_CIRCUIT}"],
                #     SELECTOR_POWER,
                #     self._dict[prefix],
                # )

                self._sensor_count += 1
            else:
                _LOGGER.debug("div_element not found div_id:%s", div_id)
                break

        return total_page

    # async def async_config_entry_first_refresh(self) -> None:
    #     """Perform the first refresh with retry logic."""

    #     _LOGGER.debug("async_config_entry_first_refresh")
    #     while True:
    #         try:
    #             self.data = await self._async_update_data()
    #             break
    #         except UpdateFailed as err:
    #             _LOGGER.warning(
    #                 "Initial data fetch failed, retrying in %d seconds: %s",
    #                 RETRY_INTERVAL,
    #                 err,
    #             )
    #             await asyncio.sleep(RETRY_INTERVAL)  # Retry interval

    @property
    def dict(self) -> dict[str, Any]:
        """EcoManeDataUpdateCoordinator Dictionary."""
        return self._dict

    @property
    def sensor_total(self) -> int:
        """Total number of sensors."""
        return self._sensor_total

    @property
    def sensor_descs(self) -> list[EcoManeEnergySensorEntityDescription]:
        """Sensor descriptions."""
        return self._sensor_descs

    # @property
    # def mac_address(self) -> str:
    #     """Return the MAC address."""
    #     return self._mac_address
