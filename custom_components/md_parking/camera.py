"""Camera entities served from stable bridge/go2rtc sources."""
from __future__ import annotations

from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    # The bridge inventory endpoint supplies only stable local go2rtc URLs.
    # Entity discovery is enabled when the bridge API implementation is active.
    return


class MdParkingCamera(Camera):
    _attr_has_entity_name = True
    def __init__(self, name: str, stream_source: str) -> None:
        self._attr_name = name
        self._stream_source = stream_source
    @property
    def is_on(self) -> bool: return True
    async def stream_source(self) -> str: return self._stream_source
