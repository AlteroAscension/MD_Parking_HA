"""Bridge state coordinator for MD Parking."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_API_TOKEN, CONF_BRIDGE_URL, DOMAIN


class MdParkingCoordinator(DataUpdateCoordinator[dict]):
    """Poll only the local bridge; provider secrets never enter HA Core."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            logger=__import__("logging").getLogger(__name__),
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )
        self._base_url = entry.data[CONF_BRIDGE_URL].rstrip("/")
        self._headers = {"Authorization": f"Bearer {entry.data[CONF_API_TOKEN]}"}

    async def _async_update_data(self) -> dict:
        session = async_get_clientsession(self.hass)
        try:
            async with session.get(
                self._base_url + "/diagnostics", headers=self._headers, timeout=10
            ) as response:
                if response.status != 200:
                    raise UpdateFailed(f"bridge diagnostics HTTP {response.status}")
                diagnostics = await response.json()
            async with session.get(
                self._base_url + "/v1/cameras", headers=self._headers, timeout=10
            ) as response:
                if response.status != 200:
                    raise UpdateFailed(f"bridge cameras HTTP {response.status}")
                cameras = (await response.json()).get("cameras", [])
        except UpdateFailed:
            raise
        except Exception as exc:
            raise UpdateFailed("cannot connect to MD Parking Bridge") from exc

        if diagnostics.get("auth_state") != "authenticated":
            raise UpdateFailed("MD Parking Bridge is not authenticated")
        if not isinstance(cameras, list) or not cameras:
            raise UpdateFailed("MD Parking Bridge returned no cameras")
        return {"diagnostics": diagnostics, "cameras": cameras}
