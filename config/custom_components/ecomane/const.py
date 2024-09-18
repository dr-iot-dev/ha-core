"""Constants for the Eco Mane HEMS integration."""

from __future__ import annotations

# from datetime import timedelta
from homeassistant.const import Platform

DOMAIN = "ecomane"
DEFAULT_ENCODING = "UTF-8"  # デフォルトエンコーディング
DEFAULT_NAME = "Panasonic Eco Mane HEMS"
# DEFAULT_VERIFY_SSL = True
# DEFAULT_SCAN_INTERVAL = timedelta(minutes=1)
DEFAULT_IP_ADDRESS = "192.168.1.220"

ENCODING = "shift-jis"  # ECOマネのエンコーディング

PLATFORMS = [Platform.SENSOR]
PLATFORM = Platform.SENSOR

ENTITY_NAME = "EcoManeHEMS"

# 回路別電力
SENSOR_CIRCUIT_POWER_SERVICE_TYPE = "power"

SENSOR_POWER_SELECTOR_PREFIX = "ojt"
SENSOR_CIRCUIT_PREFIX = "em_circuit"
# SENSOR_POWER_ATTR_PREFIX = "power"

SENSOR_CIRCUIT_POWER_CGI = "elecCheck_6000.cgi?disp=2"

SENSOR_CIRCUIT_ENERGY_SERVICE_TYPE = "energy"
SENSOR_CIRCUIT_ENERGY_CGI = "resultGraphDiv_4242.cgi"

# 本日の使用量
SENSOR_TODAY_CGI = "ecoTopMoni.cgi"

SELECTOR_IP = "ip"
SELECTOR_NAME = "name"
SELECTOR_PLACE = "txt"
SELECTOR_CIRCUIT = "txt2"
SELECTOR_CIRCUIT_POWER = "num"
SELECTOR_CIRCUIT_BUTTON = "btn btn_58"
SELECTOR_CIRCUIT_ENERGY = "ttx_01"

RETRY_INTERVAL = 120  # 再試行間隔: 120秒
POLLING_INTERVAL = 60  # ECOマネへのpolling間隔: 60秒
