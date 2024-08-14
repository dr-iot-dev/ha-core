"""Coordinator for Eco Mane ElecCheck component."""

import asyncio
from datetime import timedelta
import logging

import aiohttp
from bs4 import BeautifulSoup, NavigableString
from bs4.element import Tag

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    ENCODING,
    ENTITY_NAME,
    POLLING_INTERVAL,
    RETRY_INTERVAL,
    SELECTOR_CIRCUIT,
    SELECTOR_PLACE,
    SELECTOR_POWER,
    SENSOR_POWER_CGI,
    SENSOR_POWER_PREFIX,
    SENSOR_POWER_SELECTOR_PREFIX,
)

_LOGGER = logging.getLogger(__name__)

# retry_interval = 120
# polling_interval = 300


class ElecCheckDataCoordinator(DataUpdateCoordinator):
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
        )
        self._ip = ip
        self._power_dict: dict[str, str] = {}
        self._session = None
        self._sensor_total = 0
        self._sensor_count = 0

    def natural_number_generator(self):
        """Natural number generator."""
        count = 1
        while True:
            yield count
            count += 1

    async def _async_update_data(self):
        """Update ElecCheck."""
        _LOGGER.debug("Updating ElecCheck data")  # debug
        response = None
        try:
            # デバイスからデータを取得
            url = f"http://{self._ip}/{SENSOR_POWER_CGI}"
            async with aiohttp.ClientSession() as session:
                self._sensor_count = 0
                # for page_num in range(1, total_page + 1):
                for page_num in self.natural_number_generator():
                    url = f"http://{self._ip}/{SENSOR_POWER_CGI}&page={page_num}"
                    response = await session.get(url)
                    if response.status != 200:
                        _LOGGER.error(
                            "Error fetching data from %s. Status code: %s",
                            url,
                            response.status,
                        )
                        raise UpdateFailed(
                            f"Error fetching data from {url}. Page:{page_num} Status code: {response.status}"
                        )
                    response.encoding = ENCODING
                    total_page = await self.parse_data(response, page_num)
                    if page_num >= total_page:
                        break
                self._sensor_total = self._sensor_count
                _LOGGER.debug("Total number of sensors = %s", self._sensor_total)
        except Exception as err:
            _LOGGER.error("Error updating sensor data: %s", err)
            raise UpdateFailed("_async_update_data failed") from err
        # finally:

        return self._power_dict

    async def parse_data(self, response, page_num) -> int:
        """Parse data from the content."""

        response.encoding = ENCODING
        raw_content = await response.read()
        text = raw_content.decode(ENCODING)
        soup = BeautifulSoup(text, "html.parser")
        maxp = soup.find("input", {"name": "maxp"})
        # if maxp is None:
        #     total_page = 0
        # else:
        #     total_page = int(maxp["value"])

        total_page = 0
        if isinstance(maxp, Tag):
            value = maxp.get("value", "0")
            # Ensure value is a string before converting to int
            if isinstance(value, str):
                total_page = int(value)

        for button_num in range(1, 9):
            div_id = f"{SENSOR_POWER_SELECTOR_PREFIX}_{button_num:02d}"
            prefix = f"{SENSOR_POWER_PREFIX}_{self._sensor_count}"

            _LOGGER.debug("page:%s id:%s prefix:%s", page_num, div_id, prefix)

            div_element: Tag | NavigableString | None = soup.find("div", id=div_id)
            if isinstance(div_element, Tag):
                # 要素を取得
                element: Tag | NavigableString | int | None = div_element.find(
                    "div",
                    class_=SELECTOR_PLACE,  # txt
                )
                if isinstance(element, Tag):
                    self._power_dict[f"{prefix}_{SELECTOR_PLACE}"] = (
                        element.get_text()
                    )  # txt
                    # _LOGGER.debug("%s:%s", SELECTOR_PLACE, element.get_text())

                element = div_element.find("div", class_=SELECTOR_CIRCUIT)  # txt2
                if isinstance(element, Tag):
                    self._power_dict[f"{prefix}_{SELECTOR_CIRCUIT}"] = (
                        element.get_text()
                    )  # txt2
                    # _LOGGER.debug("%s:%s", SELECTOR_CIRCUIT, element.get_text())

                element = div_element.find("div", class_=SELECTOR_POWER)  # num
                if isinstance(element, Tag):
                    self._power_dict[prefix] = element.get_text().split("W")[0]

                _LOGGER.debug(
                    "%s:%s, %s:%s, %s:%s",
                    SELECTOR_PLACE,
                    self._power_dict[f"{prefix}_{SELECTOR_PLACE}"],
                    SELECTOR_CIRCUIT,
                    self._power_dict[f"{prefix}_{SELECTOR_CIRCUIT}"],
                    SELECTOR_POWER,
                    self._power_dict[prefix],
                )

                self._sensor_count += 1
            else:
                _LOGGER.debug("div_element not found div_id:%s", div_id)
                break

        return total_page

    async def async_config_entry_first_refresh(self):
        """Perform the first refresh with retry logic."""
        while True:
            try:
                await self._async_update_data()
                break
            except UpdateFailed as err:
                _LOGGER.warning(
                    "Initial data fetch failed, retrying in %d seconds: %s",
                    RETRY_INTERVAL,
                    err,
                )
                await asyncio.sleep(RETRY_INTERVAL)  # Retry interval

    @property
    def power_dict(self) -> dict[str, str]:
        """ElecCheck Dictionary."""
        return self._power_dict

    @property
    def sensor_total(self) -> int:
        """ElecCheck total number of entries."""
        return self._sensor_total
