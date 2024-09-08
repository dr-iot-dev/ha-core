"""Constants for the Eco Mane HEMS integration."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.const import Platform

DOMAIN = "ecomane"
DEFAULT_ENCODING = "UTF-8"
DEFAULT_NAME = "Panasonic Eco Mane HEMS"
DEFAULT_VERIFY_SSL = True
DEFAULT_SCAN_INTERVAL = timedelta(minutes=1)
DEFAULT_IP_ADDRESS = "192.168.168.220"

ENCODING = "shift-jis"

PLATFORMS = [Platform.SENSOR]
PLATFORM = Platform.SENSOR

# CONF_ENCODING = "encoding"
# CONF_SELECT = "select"
# CONF_INDEX = "index"

ENTITY_NAME = "EcoManeHEMS"
SENSOR_POWER_SERVICE_TYPE = "electricity"

SENSOR_POWER_SELECTOR_PREFIX = "ojt"
SENSOR_POWER_PREFIX = "em_power"
SENSOR_POWER_ATTR_PREFIX = "power"

SENSOR_POWER_CGI = "elecCheck_6000.cgi?disp=2"
SENSOR_ENERGY_CGI = "ecoTopMoni.cgi"

SELECTOR_IP = "ip"
SELECTOR_NAME = "name"
SELECTOR_PLACE = "txt"
SELECTOR_CIRCUIT = "txt2"
SELECTOR_POWER = "num"


RETRY_INTERVAL = 120
POLLING_INTERVAL = 60


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
