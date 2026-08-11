"""Camera entities served from stable bridge/go2rtc sources."""
from __future__ import annotations

from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from urllib.parse import urlsplit

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    session=async_get_clientsession(hass)
    try:
        async with session.get(entry.data['bridge_url'].rstrip('/')+'/v1/cameras',headers={'Authorization':'Bearer '+entry.data['api_token']},timeout=10) as response:
            payload=await response.json()
    except Exception:
        return
    host=urlsplit(entry.data['bridge_url']).hostname
    async_add_entities([MdParkingCamera(item['name'],f'rtsp://{host}:8554/{item["stream_name"]}') for item in payload.get('cameras',[])])


class MdParkingCamera(Camera):
    _attr_has_entity_name = True
    def __init__(self, name: str, stream_source: str) -> None:
        self._attr_name = name
        self._stream_source = stream_source
        self._attr_unique_id = stream_source.rsplit('/',1)[-1]
    @property
    def is_on(self) -> bool: return True
    async def stream_source(self) -> str: return self._stream_source
