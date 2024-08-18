"""The Simple Sensor Example integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN

# _TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.SENSOR]

# _TODO Create ConfigEntry type alias with API object
# _TODO Rename type alias and update all entry annotations
type New_NameConfigEntry = ConfigEntry  # [MyApi]  # noqa: F821

# ログのフォーマットを設定
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] [%(process)d] [%(filename)s:%(lineno)d] [%(levelname)s] %(message)s",
)

_LOGGER = logging.getLogger(__name__)


# _TODO Update entry annotation
async def async_setup_entry(hass: HomeAssistant, entry: New_NameConfigEntry) -> bool:
    """Set up Simple Sensor Example from a config entry."""

    # _TODO 1. Create API instance
    # _TODO 2. Validate the API connection (and authentication)
    # _TODO 3. Store an API object for your platforms to access
    # entry.runtime_data = MyAPI(...)

    # データを hass.data に保存
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # エンティティの追加
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _LOGGER.info("エンティティの追加完了: %s", entry.entry_id)

    return True


# _TODO Update entry annotation
async def async_unload_entry(hass: HomeAssistant, entry: New_NameConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
