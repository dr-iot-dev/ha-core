"""The Eco Mane HEMS integration."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

# from homeassistant.helpers.typing import ConfigType
from .const import (
    CONF_IP,
    DOMAIN,  # Import your domain constant
    PLATFORMS,
)
from .coordinator import ElecCheckDataCoordinator

_LOGGER = logging.getLogger(__name__)

# async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
#     # hass.states.async_set("ECO Mane Elect HEMS", "Paulus")
#     """Set up the custom component."""
#     _LOGGER.info("Setting up %s component", DOMAIN)

#     hass.data.setdefault(DOMAIN, {})
#     hass.data[DOMAIN][config.entry_id] = config.data

#     # Forward the setup to the sensor platform
#     await hass.config_entries.async_forward_entry_setups(config, ["sensor"])

#     return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up eco_mane_elec from a config entry."""

    _LOGGER.info(
        "Setting up %s component from config entry: %s", DOMAIN, config_entry.data
    )
    # Perform the setup tasks here

    ip = config_entry.data[CONF_IP]

    # DataCoordinatorを作成
    coordinator = ElecCheckDataCoordinator(hass, ip)
    # 初期データ取得
    await coordinator.async_config_entry_first_refresh()
    if not coordinator.last_update_success:
        raise ConfigEntryNotReady("async_config_entry_first_refresh() failed")

    # elec_dict = coordinator.elec_dict
    total = coordinator.total
    _LOGGER.debug("total: %s", total)

    # データを hass.data に保存
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = coordinator
    _LOGGER.debug("__init__.py config_entry.entry_id: %s", config_entry.entry_id)

    # エンティティの追加
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    # # センサーのエンティティのリストを作成
    # sensors = []
    # for _i in range(int(total)):
    #     prefix = f"elecCheck_{_i}"
    #     txt = elec_dict[prefix + "_txt"]
    #     txt2 = elec_dict[prefix + "_txt2"]
    #     num = elec_dict[prefix]
    #     sensors.append(ElecCheckEntity(coordinator, prefix, txt, txt2, num))

    # # エンティティを追加
    # hass.data.setdefault(DOMAIN, {})[entry.entry_id] = entities

    # #  Example: Store the config entry data
    # component = hass.data[DOMAIN].get("component")
    # if component is None:
    #     component = hass.data[DOMAIN]["component"] = EntityComponent(_LOGGER, DOMAIN, hass)

    # # エンティティを追加
    # async_add_entities(sensors, update_before_add=True)

    # # Forward the setup to the sensor platform
    # await hass.config_entries.async_forward_entry_setups(config_entry, ["sensor"])

    # Return True if setup was successful
    _LOGGER.debug(
        "__init__.py async_setup_entry has finished setting up %s with config entry (Platform.SENSOR:%s)",
        DOMAIN,
        Platform.SENSOR,
    )
    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # # Perform the unload tasks here
    # await hass.config_entries.async_forward_entry_unload(config_entry, ["sensor"])
    # hass.data[DOMAIN].pop(config_entry.entry_id)

    _LOGGER.info(
        "Unloading %s with config entry (%s): %s",
        DOMAIN,
        config_entry.entry_id,
        config_entry.data,
    )

    # エンティティのアンロード
    # unload_ok = await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)
    _LOGGER.debug("Unloading platforms: %s", Platform.SENSOR)
    unload_ok = await hass.config_entries.async_forward_entry_unload(
        config_entry, Platform.SENSOR
    )

    # クリーンアップ処理
    if unload_ok:
        # ElecCheckDataCoordinatorを削除
        hass.data[DOMAIN].pop(config_entry.entry_id, None)

    # unload_ok = all(await component.async_remove_entity(entity.entity_id) for entity in entities)
    # # エントリのデータを削除
    # if unload_ok:
    #     hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok
    # Return True if unload was successful
    # return True
