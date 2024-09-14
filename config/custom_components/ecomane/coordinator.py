"""Coordinator for Eco Mane HEMS component."""

import asyncio
from collections.abc import Generator
from dataclasses import dataclass
from datetime import timedelta
import logging

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
    RETRY_INTERVAL,
    SELECTOR_CIRCUIT,
    SELECTOR_PLACE,
    SELECTOR_POWER,
    SENSOR_POWER_CGI,
    SENSOR_POWER_PREFIX,
    SENSOR_POWER_SELECTOR_PREFIX,
    SENSOR_TODAY_CGI,
)

_LOGGER = logging.getLogger(__name__)


# 電力センサーのエンティティのディスクリプション
@dataclass(frozen=True, kw_only=True)
class EcoManePowerSensorEntityDescription(SensorEntityDescription):
    """Describes EcoManePower sensor entity."""

    service_type: str


# 使用量センサーのエンティティのディスクリプション
@dataclass(frozen=True, kw_only=True)
class EcoManeUsageSensorEntityDescription(SensorEntityDescription):
    """Describes EcoManeEnergy sensor entity."""

    description: str


# 使用量センサーのエンティティのディスクリプションのリストを作成
ecomane_usage_sensors_descs = [
    EcoManeUsageSensorEntityDescription(
        name="electricity_purchased",
        translation_key="electricity_purchased",
        description="Electricity purchased 購入電気量",
        key="num_L1",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    EcoManeUsageSensorEntityDescription(
        name="solar_power_energy",
        translation_key="solar_power_energy",
        description="Solar Power Energy / 太陽光発電量",
        key="num_L2",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    EcoManeUsageSensorEntityDescription(
        name="gas_consumption",
        translation_key="gas_consumption",
        description="Gas Consumption / ガス消費量",
        key="num_L4",
        device_class=SensorDeviceClass.GAS,
        native_unit_of_measurement=UnitOfVolume.CUBIC_METERS,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    EcoManeUsageSensorEntityDescription(
        name="water_consumption",
        translation_key="water_consumption",
        description="Water Consumption / 水消費量",
        key="num_L5",
        device_class=SensorDeviceClass.WATER,
        native_unit_of_measurement=UnitOfVolume.CUBIC_METERS,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    EcoManeUsageSensorEntityDescription(
        name="co2_emissions",
        translation_key="co2_emissions",
        description="CO2 Emissions / CO2排出量",
        key="num_R1",
        device_class=SensorDeviceClass.WEIGHT,
        native_unit_of_measurement=UnitOfMass.KILOGRAMS,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    EcoManeUsageSensorEntityDescription(
        name="co2_reduction",
        translation_key="co2_reduction",
        description="CO2 Reduction / CO2削減量",
        key="num_R2",
        device_class=SensorDeviceClass.WEIGHT,
        native_unit_of_measurement=UnitOfMass.KILOGRAMS,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    EcoManeUsageSensorEntityDescription(
        name="electricity_sales",
        translation_key="electricity_sales",
        description="Electricity sales / 売電量",
        key="num_R3",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
]


class EcoManeDataCoordinator(DataUpdateCoordinator):
    """EcoMane Data coordinator."""

    _attr_power_sensor_total: int
    _attr_usage_sensor_descs: list[EcoManeUsageSensorEntityDescription]
    data_dict: dict[str, str]

    def __init__(self, hass: HomeAssistant, ip_address: str) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=ENTITY_NAME,
            update_interval=timedelta(
                seconds=POLLING_INTERVAL
            ),  # data polling interval
        )

        self._data_dict = {"ip_address": ip_address}
        self._session = None
        self._power_sensor_count = 0
        self._ip_address = ip_address

        self._attr_power_sensor_total = 0
        self._attr_usage_sensor_descs = ecomane_usage_sensors_descs

    def natural_number_generator(self) -> Generator:
        """Natural number generator."""
        count = 1
        while True:
            yield count
            count += 1

    async def _async_update_data(self) -> dict[str, str]:
        """Update Eco Mane Data."""
        _LOGGER.debug("_async_update_data: Updating EcoMane data")  # debug
        await self.update_usage_data()
        await self.update_power_data()
        return self._data_dict

    async def update_usage_data(self) -> None:
        """Update usage data."""
        _LOGGER.debug("update_usage_data")
        try:
            # デバイスからデータを取得
            url = f"http://{self._ip_address}/{SENSOR_TODAY_CGI}"
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
                await self.parse_usage_data(text_data)
                _LOGGER.debug("EcoMane usage data updated successfully")
        except Exception as err:
            _LOGGER.error("Error updating usage data: %s", err)
            raise UpdateFailed("update_usage_data failed") from err
        # finally:

    async def parse_usage_data(self, text: str) -> dict:
        """Parse data from the content."""

        # BeautifulSoupを使用してHTMLを解析
        soup = BeautifulSoup(text, "html.parser")
        # 指定したIDを持つdivタグの値を取得して辞書に格納
        for usage_sensor_desc in ecomane_usage_sensors_descs:
            key = usage_sensor_desc.key
            div = soup.find("div", id=key)
            if div:
                value = div.text.strip()
                self._data_dict[key] = value
        return self._data_dict

    async def update_power_data(self) -> dict:
        """Update power data."""
        _LOGGER.debug("update_power_data")
        try:
            # デバイスからデータを取得
            url = f"http://{self._ip_address}/{SENSOR_POWER_CGI}"
            async with aiohttp.ClientSession() as session:
                self._power_sensor_count = 0
                for (
                    page_num
                ) in self.natural_number_generator():  # 1ページ目から順に取得
                    url = (
                        f"http://{self._ip_address}/{SENSOR_POWER_CGI}&page={page_num}"
                    )
                    response: aiohttp.ClientResponse = await session.get(url)
                    if response.status != 200:
                        _LOGGER.error(
                            "Error fetching data from %s. Status code: %s",
                            url,
                            response.status,
                        )
                        raise UpdateFailed(
                            f"Error fetching data from {url}. Page: {page_num} Status code: {response.status}"
                        )
                    # テキストデータを取得する際に shift-jis エンコーディングを指定
                    text_data = await response.text(encoding="shift-jis")
                    # text_data からデータを取得, 最大ページ total_page に達したら終了
                    total_page = await self.parse_power_data(text_data, page_num)
                    if page_num >= total_page:
                        break
                self._attr_power_sensor_total = self._power_sensor_count
                _LOGGER.debug(
                    "Total number of power sensors = %s", self._attr_power_sensor_total
                )
        except Exception as err:
            _LOGGER.error("Error updating power data: %s", err)
            raise UpdateFailed("update_power_data failed") from err
        # finally:

        _LOGGER.debug("EcoMane power data updated successfully")
        return self._data_dict

    async def parse_power_data(self, text: str, page_num: int) -> int:
        """Parse data from the content."""
        # BeautifulSoupを使用してHTMLを解析
        soup = BeautifulSoup(text, "html.parser")
        # 最大ページ数を取得
        maxp = soup.find("input", {"name": "maxp"})
        total_page = 0
        if isinstance(maxp, Tag):
            value = maxp.get("value", "0")
            # Ensure value is a string before converting to int
            if isinstance(value, str):
                total_page = int(value)

        # ページ内の各センサーエンティティのデータを取得
        for button_num in range(1, 9):
            div_id = f"{SENSOR_POWER_SELECTOR_PREFIX}_{button_num:02d}"
            prefix = f"{SENSOR_POWER_PREFIX}_{self._power_sensor_count:02d}"

            div_element: Tag | NavigableString | None = soup.find("div", id=div_id)
            if isinstance(div_element, Tag):
                # 要素を取得
                element: Tag | NavigableString | int | None = div_element.find(
                    "div",
                    class_=SELECTOR_PLACE,  # txt
                )

                # 場所
                if isinstance(element, Tag):
                    self._data_dict[f"{prefix}_{SELECTOR_PLACE}"] = (
                        element.get_text()
                    )  # txt

                # 回路
                element = div_element.find("div", class_=SELECTOR_CIRCUIT)  # txt2
                if isinstance(element, Tag):
                    self._data_dict[f"{prefix}_{SELECTOR_CIRCUIT}"] = (
                        element.get_text()
                    )  # txt2

                # 電力
                element = div_element.find("div", class_=SELECTOR_POWER)  # num
                if isinstance(element, Tag):
                    self._data_dict[prefix] = element.get_text().split("W")[0]

                # 電力センサーエンティティ数をカウント
                self._power_sensor_count += 1

                # デバッグログ
                _LOGGER.debug(
                    "page:%s id:%s prefix:%s power:%s",
                    page_num,
                    div_id,
                    prefix,
                    self._data_dict[prefix],
                )
            else:
                _LOGGER.debug("div_element not found div_id:%s", div_id)
                break

        return total_page

    async def async_config_entry_first_refresh(self) -> None:
        """Perform the first refresh with retry logic."""
        while True:
            try:
                self.data = await self._async_update_data()
                break
            except UpdateFailed as err:
                _LOGGER.warning(
                    "Initial data fetch failed, retrying in %d seconds: %s",
                    RETRY_INTERVAL,
                    err,
                )
                await asyncio.sleep(RETRY_INTERVAL)  # Retry interval

    @property
    def power_sensor_total(self) -> int:
        """Total number of power sensors."""
        return self._attr_power_sensor_total

    @property
    def usage_sensor_descs(self) -> list[EcoManeUsageSensorEntityDescription]:
        """Usage sensor descriptions."""
        return self._attr_usage_sensor_descs

    @property
    def ip_address(self) -> str:
        """IP address."""
        return self._data_dict["ip_address"]
