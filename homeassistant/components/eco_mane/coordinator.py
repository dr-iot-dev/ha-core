"""Coordinator for Eco Mane component."""

from datetime import timedelta
import logging

from bs4 import BeautifulSoup
import requests

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import CONF_IDS

_LOGGER = logging.getLogger(__name__)


class EcoTopMoniDataCoordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(self, hass: HomeAssistant, ip: str, config: ConfigType) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="My Sensor",
            update_interval=timedelta(minutes=5),
        )
        self._ip = ip
        self._config = config
        self._result_dict: dict[str, str] = {}

    # def set_config(self, config: ConfigType) -> None:
    #     """Set Config."""
    #     self._config = config

    async def _async_update_data(self):
        """Update info."""
        result_dict = {}
        try:
            # デバイスからデータを取得
            url = "http://" + self._ip + "/ecoTopMoni.cgi"
            # _LOGGER.debug(f"{url=}")
            response = await self.hass.async_add_executor_job(requests.get, url)
            html_response = response.text

            # BeautifulSoupを使用してHTMLを解析
            soup = BeautifulSoup(html_response, "html.parser")

            # 指定したIDを持つdivタグの値を取得して辞書に格納
            # _LOGGER.debug(f"self._config={self._config}")
            div_ids = self._config[CONF_IDS]
            for div_id in div_ids:
                div = soup.find("div", id=div_id)
                if div:
                    value = div.text.strip()
                    result_dict[div_id] = value
                    # _LOGGER.debug(f"id:{div_id} value:{value}")
            self._result_dict = result_dict
        except Exception as err:
            _LOGGER.error("Error updating sensor data: %s", err)
            raise
        return result_dict
