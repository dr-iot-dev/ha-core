"""Coordinator for Eco Mane ElecCheck component."""

from datetime import timedelta
import logging

# import re
# import aiohttp
# from pyppeteer import launch
# import time
# from bs4 import BeautifulSoup
# import requests
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import WebDriverWait
# from webdriver_manager.chrome import ChromeDriverManager
from requests_html import AsyncHTMLSession

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

    async def _async_update_data(self):
        """Update ElecCheck."""
        # loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(loop)

        # # browser = await asyncio.to_thread(
        # #     self.launch_browser
        # # )  # launch_browserを別スレッドで実行
        # # browser = await launch_browser_async()  # 直接awaitして結果を取得
        # browser = loop.run_until_complete(
        #     launch(
        #         headless=True,
        #         executablePath="/home/vscode/.local/share/pyppeteer/local-chromium/1181205/chrome-linux/chrome",
        #     )
        # )
        # page = loop.run_until_complete(browser.newPage())
        # page = await browser.newPage()
        # # service = await get_chrome_driver()
        # # Initialize WebDriver with service and options
        # # driver = webdriver.Chrome(service=service, options=options)
        # # Initialize WebDriver asynchronously
        # driver = await init_webdriver()

        # # Selenium WebDriverをセットアップ
        # options = webdriver.ChromeOptions()
        # options.add_argument("--headless")  # ヘッドレスモードを使用
        # driver = webdriver.Chrome(options=options)

        self._session = AsyncHTMLSession()
        try:
            # デバイスからデータを取得
            url = f"http://{self._ip}/elecCheck_6000.cgi&disp=2"
            # driver.get(url)
            # await page.goto(url)
            # loop.run_until_complete(page.goto(url))
            response = await self._session.get(url)

            # 新しいページが読み込まれるまで待つ
            # content = await page.content()
            # content = loop.run_until_complete(page.content())
            await response.html.arender()
            # await run_in_executor(response.html.arender)

            # self.parse_data(content)
            title_element = response.html.title.text
            total_page = title_element.text.split("/")[1]

            for page_num in range(1, total_page + 1):
                url = f"http://{self._ip}/elecCheck_6000.cgi?page={page_num}&disp=2"
                response = await self._session.get(url)
                self.parse_data(response)
        except Exception as err:
            _LOGGER.error("Error updating sensor data: %s", err)
            raise
        # finally:
        #     # ブラウザを閉じる
        #     # await browser.close()
        #     loop.run_until_complete(browser.close())
        # parse data
        # elec_dict = self.parse_data(content)

    async def parse_data(self, response) -> None:
        """Parse data from the content."""

        for button_num in range(1, 9):
            div_id = f"ojt_{button_num:02d}"
            prefix = f"elecCheck_{self._count}"

            _LOGGER.debug("id:%s prefix:%s", div_id, prefix)
            # div_element = content.querySelector("#" + div_id)
            div_element = response.html.find("#" + div_id, first=True)
            if div_element:
                # 要素を取得
                # txt_element = div_element.querySelector("#txt")
                # txt2_element = div_element.querySelector("#txt2")
                # num_element = div_element.querySelector("#num").split("W")[0]
                # div要素のテキストを取得
                # elec_dict[prefix + "_txt"] = await content.evaluate(
                #     "(element) => element.textContent", txt_element
                # )
                # elec_dict[prefix + "_txt2"] = await content.evaluate(
                #     "(element) => element.textContent", txt2_element
                # )
                # elec_dict[prefix] = await content.evaluate(
                #     "(element) => element.textContent", num_element
                # ).split("W")[0]
                self._elec_dict[prefix + "_txt"] = div_element.find(
                    "#txt", first=True
                ).text
                self._elec_dict[prefix + "_txt2"] = div_element.find(
                    "#txt2", first=True
                ).text
                self._elec_dict[prefix] = div_element.find(
                    "#num", first=True
                ).text.split("W")[0]
                self._count = self._count + 1

    @property
    def elec_dict(self) -> dict[str, str]:
        """ElecCheck Dictionary."""
        return self._elec_dict
