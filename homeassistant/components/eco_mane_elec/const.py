"""Constants for the Eco Mane HEMS integration."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.const import Platform

DOMAIN = "eco_mane_elec"
DEFAULT_ENCODING = "UTF-8"
DEFAULT_NAME = "Eco Mane ElecCheck"
DEFAULT_VERIFY_SSL = True
DEFAULT_SCAN_INTERVAL = timedelta(minutes=1)

PLATFORMS = [Platform.SENSOR]
PLATFORM = Platform.SENSOR

CONF_ENCODING = "encoding"
# CONF_SELECT = "select"
# CONF_INDEX = "index"

CONF_IP = "ip"
CONF_NAME = "name"
# CONF_IDS = "div_ids"
# CONF_SELECTOR = "selector"

SERVICE_TYPE_DEVICE_NAMES = {
    "electricity": "Electric power",
    "solar": "Solar power",
    "electric energy": "Electric energy",
    "solar energy": "Solar energy",
    "gas": "Gas",
    "water": "Water",
}
