"""Coordinator for Eco Mane ElecCheck component."""

import asyncio
from datetime import timedelta
import logging

import aiohttp
from bs4 import BeautifulSoup, NavigableString
from bs4.element import Tag

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

retry_interval = 120
polling_interval = 300


class ElecCheckDataCoordinator(DataUpdateCoordinator):
    """ElecCheck_6000 coordinator."""

    def __init__(self, hass: HomeAssistant, ip: str) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="ElecCheck",
            update_interval=timedelta(
                seconds=polling_interval
            ),  # data polling interval
        )
        self._ip = ip
        self._elec_dict: dict[str, str] = {}
        self._session = None
        self._total = 0
        self._count = 0

    async def _async_update_data(self):
        """Update ElecCheck."""
        _LOGGER.debug("Updating ElecCheck data")  # debug
        response = None
        try:
            # デバイスからデータを取得
            url = f"http://{self._ip}/elecCheck_6000.cgi?disp=2"
            async with aiohttp.ClientSession() as session:
                response = await session.get(url)
                if response.status != 200:
                    _LOGGER.error(
                        "Error fetching data from %s. Status code: %s",
                        url,
                        response.status,
                    )
                    raise UpdateFailed(
                        f"Error fetching data from {url}. Status code: {response.status}"
                    )
                response.encoding = "shift-jis"
                raw_content = await response.read()
                text = raw_content.decode("shift-jis")
                soup = BeautifulSoup(text, "html.parser")
                maxp_value = soup.find("input", {"name": "maxp"})["value"]
                total_page = int(maxp_value)

                self._count = 0
                for page_num in range(1, total_page + 1):
                    url = f"http://{self._ip}/elecCheck_6000.cgi?page={page_num}&disp=2"
                    response = await session.get(url)
                    if response.status != 200:
                        _LOGGER.error(
                            "Error fetching data from %s. Status code: %s",
                            url,
                            response.status,
                        )
                        raise UpdateFailed(
                            f"Error fetching data from {url}. Page:{page_num} Total Page:{total_page} Status code: {response.status}"
                        )
                    response.encoding = "shift-jis"
                    await self.parse_data(response, page_num)
                self._total = self._count
                _LOGGER.debug("Total number of entries = %s", self._total)
        except Exception as err:
            _LOGGER.error("Error updating sensor data: %s", err)
            raise UpdateFailed("_async_update_data failed") from err
        # finally:

        return self._elec_dict

    async def parse_data(self, response, page_num) -> None:
        """Parse data from the content."""

        for button_num in range(1, 9):
            div_id = f"ojt_{button_num:02d}"
            prefix = f"elecCheck_{self._count}"

            _LOGGER.debug("page:%s id:%s prefix:%s", page_num, div_id, prefix)

            response.encoding = "shift-jis"
            raw_content = await response.read()
            text = raw_content.decode("shift-jis")
            soup = BeautifulSoup(text, "html.parser")
            div_element: Tag | NavigableString | None = soup.find("div", id=div_id)
            if isinstance(div_element, Tag):
                # 要素を取得
                element: Tag | NavigableString | int | None = div_element.find(
                    "div", class_="txt"
                )
                if isinstance(element, Tag):
                    self._elec_dict[prefix + "_txt"] = element.get_text()
                    _LOGGER.debug("txt:%s", element.get_text())

                element = div_element.find("div", class_="txt2")
                if isinstance(element, Tag):
                    self._elec_dict[prefix + "_txt2"] = element.get_text()
                    _LOGGER.debug("txt2:%s", element.get_text())

                element = div_element.find("div", class_="num")
                if isinstance(element, Tag):
                    self._elec_dict[prefix] = element.get_text().split("W")[0]
                    _LOGGER.debug("num:%s", element.get_text().split("W")[0])

                self._count = self._count + 1
            else:
                _LOGGER.debug("div_element not found div_id:%s", div_id)

    async def async_config_entry_first_refresh(self):
        """Perform the first refresh with retry logic."""
        while True:
            try:
                await self._async_update_data()
                break
            except UpdateFailed as err:
                _LOGGER.warning(
                    "Initial data fetch failed, retrying in %d seconds: %s",
                    retry_interval,
                    err,
                )
                await asyncio.sleep(retry_interval)  # Retry interval

    @property
    def elec_dict(self) -> dict[str, str]:
        """ElecCheck Dictionary."""
        return self._elec_dict

    @property
    def total(self) -> int:
        """ElecCheck total number of entries."""
        return self._total
