"""Camera entities served from stable bridge/go2rtc sources."""
from __future__ import annotations

from urllib.parse import urlsplit

from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_BRIDGE_URL, DOMAIN
from .coordinator import MdParkingCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: MdParkingCoordinator = hass.data[DOMAIN][entry.entry_id]
    host = urlsplit(entry.data[CONF_BRIDGE_URL]).hostname
    async_add_entities(
        MdParkingCamera(coordinator, entry, item, host)
        for item in coordinator.data["cameras"]
    )


class MdParkingCamera(CoordinatorEntity[MdParkingCoordinator], Camera):
    """A stable local camera managed by the bridge coordinator."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MdParkingCoordinator,
        entry: ConfigEntry,
        camera: dict,
        host: str,
    ) -> None:
        super().__init__(coordinator)
        self._camera_id = camera["id"]
        self._attr_name = camera["name"]
        self._attr_unique_id = camera["id"]
        self._stream_source = f'rtsp://{host}:8554/{camera["stream_name"]}'
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="MD Parking",
            manufacturer="MD Parking",
            model="Camera Bridge",
        )

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success and any(
            item.get("id") == self._camera_id
            for item in self.coordinator.data.get("cameras", [])
        )

    @property
    def is_on(self) -> bool:
        return self.available

    async def stream_source(self) -> str:
        return self._stream_source
