"""The Eco Mane Config Flow."""

from homeassistant import config_entries

from .const import DOMAIN


# エラークラスの定義
class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


class InvalidAuth(Exception):
    """Error to indicate there is invalid auth."""


class EcoTopMoniConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Example config flow."""

    # The schema version of the entries that it creates
    # Home Assistant will call your migrate method if the version changes
    VERSION = 0
    MINOR_VERSION = 1
