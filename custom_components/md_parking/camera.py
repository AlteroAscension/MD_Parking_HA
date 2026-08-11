"""Camera entities served from stable bridge/go2rtc sources."""
from __future__ import annotations

from urllib.parse import urlsplit

from homeassistant.components.camera import Camera
from homeassistant.components.ffmpeg import DATA_FFMPEG
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from haffmpeg.tools import ImageFrame

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
        # CoordinatorEntity does not continue cooperative initialization into
        # Camera on all supported HA releases. Camera.__init__ prepares the
        # WebRTC provider fields used while the entity is added to HA.
        Camera.__init__(self)
        CoordinatorEntity.__init__(self, coordinator)
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

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Capture a still preview from the stable local RTSP stream."""
        image = ImageFrame(self.hass.data[DATA_FFMPEG].binary)
        return await image.get_image(
            self._stream_source,
            extra_cmd="-rtsp_transport tcp",
            timeout=15,
        )
