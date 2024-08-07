"""Coordinator for Eco Mane ElecCheck component."""

from datetime import timedelta
import logging

# import re
import aiohttp

# from pyppeteer import launch
# import time
# import requests
from bs4 import BeautifulSoup, NavigableString
from bs4.element import Tag

# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import WebDriverWait
# from webdriver_manager.chrome import ChromeDriverManager
# from requests_html import AsyncHTMLSession
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# # ChromeDriverのインストールと設定
# service = Service(ChromeDriverManager().install())
# # async def get_chrome_driver() -> Service:
# #     """Get Chrome Driver."""
# #     loop = asyncio.get_running_loop()
# #     driver_path = await loop.run_in_executor(None, ChromeDriverManager().install)
# #     return Service(driver_path)

# # Create options object
# options = webdriver.ChromeOptions()


# # Async method to initialize WebDriver
# async def init_webdriver():
#     """Initialize webdriver."""
#     # Add any required options here


#     # Run the WebDriver initialization in a separate thread
#     loop = asyncio.get_running_loop()
#     driver = await loop.run_in_executor(
#         None, lambda: webdriver.Chrome(service=service, options=options)
#     )
#     return driver
# async def launch_browser_async():
#     """Launch browser."""
#     return await launch(
#         headless=True,
#         executablePath="/home/vscode/.local/share/pyppeteer/local-chromium/1181205/chrome-linux/chrome",
#     )


class ElecCheckDataCoordinator(DataUpdateCoordinator):
    """ElecCheck_6000 coordinator."""

    def __init__(self, hass: HomeAssistant, ip: str, config: ConfigType) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="ElecCheck",
            update_interval=timedelta(minutes=5),
        )
        self._ip = ip
        self._config = config
        self._elec_dict: dict[str, str] = {}
        self._session = None
        self._total = 0
        self._count = 0

    # def set_config(self, config: ConfigType) -> None:
    #     """Set Config."""
    #     self._config = config
    # def launch_browser(self):
    #     """Launch browser."""
    #     # return asyncio.run(
    #     return launch(
    #         headless=True,
    #         executablePath="/home/vscode/.local/share/pyppeteer/local-chromium/1181205/chrome-linux/chrome",
    #     )
    #     # )
    async def fetch(self, session, url):
        """Fetch data."""
        async with session.get(url) as response:
            return await response.text()

    async def _async_update_data(self):
        """Update ElecCheck."""

        response = None
        try:
            # デバイスからデータを取得
            url = f"http://{self._ip}/elecCheck_6000.cgi?disp=2"
            # driver.get(url)
            # await page.goto(url)
            # loop.run_until_complete(page.goto(url))
            async with aiohttp.ClientSession() as session:
                response = await session.get(url)
                if response.status != 200:
                    _LOGGER.error(
                        "Error fetching data from %s. Status code: %s",
                        url,
                        response.status,
                    )
                    return None
                response.encoding = "shift-jis"
                raw_content = await response.read()
                # _LOGGER.debug("raw_content: %s", raw_content)
                text = raw_content.decode("shift-jis")
                # _LOGGER.debug("text: %s", text)
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
                        return None
                    response.encoding = "shift-jis"
                    await self.parse_data(response)
                self._total = self._count
                _LOGGER.debug("Total number of entries = %s", self._total)
        except Exception as err:
            _LOGGER.error("Error updating sensor data: %s", err)
            raise
        # finally:

        return self._elec_dict

    async def parse_data(self, response) -> None:
        """Parse data from the content."""

        for button_num in range(1, 9):
            div_id = f"ojt_{button_num:02d}"
            prefix = f"elecCheck_{self._count}"

            _LOGGER.debug("id:%s prefix:%s", div_id, prefix)

            response.encoding = "shift-jis"
            raw_content = await response.read()
            # _LOGGER.debug("raw_content: %s", raw_content)
            text = raw_content.decode("shift-jis")
            # _LOGGER.debug("text: %s", text)
            soup = BeautifulSoup(text, "html.parser")
            # div_element = content.querySelector("#" + div_id)
            div_element: Tag | NavigableString | None = soup.find("div", id=div_id)
            if isinstance(div_element, Tag):
                # 要素を取得
                element: Tag | NavigableString | int | None = div_element.find(
                    "div", class_="txt"
                )
                if isinstance(element, Tag):
                    self._elec_dict[prefix + "_txt"] = element.get_text()

                element = div_element.find("div", class_="txt2")
                if isinstance(element, Tag):
                    self._elec_dict[prefix + "_txt2"] = element.get_text()

                element = div_element.find("div", class_="num")
                if isinstance(element, Tag):
                    self._elec_dict[prefix] = element.get_text().split("W")[0]

                self._count = self._count + 1
                _LOGGER.debug("count:%s", self._count)
            else:
                _LOGGER.debug("div_element not found div_id:%s", div_id)

    @property
    def elec_dict(self) -> dict[str, str]:
        """ElecCheck Dictionary."""
        return self._elec_dict

    @property
    def total(self) -> int:
        """ElecCheck total number of entries."""
        return self._total
