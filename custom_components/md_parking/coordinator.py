"""Bridge state coordinator for MD Parking."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import BridgeApiError, BridgeClient
from .const import CONF_API_TOKEN, CONF_BRIDGE_URL, DOMAIN

LOGGER = logging.getLogger(__name__)


class MdParkingCoordinator(DataUpdateCoordinator[dict]):
    """Poll only the local bridge; provider secrets never enter HA Core."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=20),
        )
        self.client = BridgeClient(
            async_get_clientsession(hass),
            entry.data[CONF_BRIDGE_URL],
            entry.data[CONF_API_TOKEN],
        )

    async def _async_update_data(self) -> dict:
        try:
            diagnostics, cameras, barrier_payload = await asyncio.gather(
                self.client.diagnostics(),
                self.client.cameras(),
                self.client.barriers(),
            )
        except BridgeApiError as exc:
            raise UpdateFailed(f"bridge unavailable: {exc.code}") from exc

        if diagnostics.get("auth_state") != "authenticated":
            raise UpdateFailed("MD Parking Bridge is not authenticated")
        if not cameras:
            raise UpdateFailed("MD Parking Bridge returned no cameras")
        barriers = barrier_payload.get("barriers", [])
        if not isinstance(barriers, list):
            raise UpdateFailed("MD Parking Bridge returned invalid barriers")
        return {
            "diagnostics": diagnostics,
            "cameras": cameras,
            "barriers": [item for item in barriers if isinstance(item, dict)],
            "control_enabled": barrier_payload.get("control_enabled") is True,
        }
