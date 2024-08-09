"""The Eco Mane Config Flow."""

import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.translation import async_get_translations

from .const import DOMAIN  # Import your domain constant

_LOGGER = logging.getLogger(__name__)


@callback
def configured_instances(hass: HomeAssistant):
    """Return a set of configured instances."""
    return {entry.data["name"] for entry in hass.config_entries.async_entries(DOMAIN)}


class EcoManeElecConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Eco Mane Elec."""

    VERSION = 0
    MINOR_VERSION = 1

    async def async_step_user(self, user_input=None) -> ConfigFlowResult:
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            # Validate user input here
            if user_input["name"] in configured_instances(self.hass):
                errors["base"] = "name_exists"
            else:
                return self.async_create_entry(
                    title=user_input["name"], data=user_input
                )
        data_schema = vol.Schema(
            {
                vol.Required(
                    "name",
                    default="ECO_MANE_ELEC",
                ): str,
                vol.Required("ip", default="192.168.168.220"): str,
            }
        )

        if user_input is not None:
            if user_input["name"] in configured_instances(self.hass):
                errors["base"] = "name_exists"
            else:
                # Additional custom validation can be added here
                return self.async_create_entry(
                    title=user_input["name"], data=user_input
                )

        # strings.json から description_placeholders を取得
        translations = await async_get_translations(
            self.hass,
            "en",
            "config",
            [DOMAIN],
        )
        _name_description = translations.get(
            f"component.{DOMAIN}.config.step.user.description_placeholders.name_description",
            "Name of the Eco Mane Elec HEMS System",
        )
        _LOGGER.debug("_name_description=%s", _name_description)

        _ip_description = translations.get(
            f"component.{DOMAIN}.config.step.user.description_placeholders.ip_description",
            "IP address of the Eco Mane Elec HEMS System",
        )
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            # description_placeholders={
            #     "name_description": _name_description,
            #     "ip": _ip_description,
            # },
        )
