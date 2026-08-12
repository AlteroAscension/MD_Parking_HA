"""Constants for the MD Parking integration."""

DOMAIN = "md_parking"
CONF_BRIDGE_URL = "bridge_url"
CONF_API_TOKEN = "api_token"
PLATFORMS: list[str] = ["binary_sensor", "camera", "button"]
DEFAULT_BRIDGE_URL = "http://homeassistant.local:8099"
