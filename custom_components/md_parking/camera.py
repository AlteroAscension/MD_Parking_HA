"""Camera entities served from stable bridge/go2rtc sources."""

from __future__ import annotations

import asyncio
import logging
import time
from urllib.parse import urlsplit

from haffmpeg.tools import ImageFrame
from homeassistant.components.camera import Camera, CameraEntityFeature
from homeassistant.components.ffmpeg import DATA_FFMPEG
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_BRIDGE_URL, DOMAIN
from .coordinator import MdParkingCoordinator

LOGGER = logging.getLogger(__name__)
SNAPSHOT_CACHE_SECONDS = 8


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: MdParkingCoordinator = hass.data[DOMAIN][entry.entry_id]
    host = urlsplit(entry.data[CONF_BRIDGE_URL]).hostname
    known: set[str] = set()

    def add_new_entities() -> None:
        entities = []
        for item in coordinator.data.get("cameras", []):
            camera_id = item.get("id")
            if not isinstance(camera_id, str) or camera_id in known:
                continue
            known.add(camera_id)
            entities.append(MdParkingCamera(coordinator, entry, item, host))
        if entities:
            async_add_entities(entities)

    add_new_entities()
    entry.async_on_unload(coordinator.async_add_listener(add_new_entities))


class MdParkingCamera(CoordinatorEntity[MdParkingCoordinator], Camera):
    """A stable local camera managed by the bridge coordinator."""

    _attr_has_entity_name = True
    _attr_supported_features = CameraEntityFeature.STREAM

    def __init__(
        self,
        coordinator: MdParkingCoordinator,
        entry: ConfigEntry,
        camera: dict,
        host: str | None,
    ) -> None:
        Camera.__init__(self)
        CoordinatorEntity.__init__(self, coordinator)
        self._camera_id = camera["id"]
        self._attr_name = str(camera.get("name") or "Камера")
        self._attr_unique_id = camera["id"]
        self._stream_source = f"rtsp://{host}:8554/{camera['stream_name']}"
        self.stream_options["rtsp_transport"] = "tcp"
        self._snapshot: bytes | None = None
        self._snapshot_at = 0.0
        self._snapshot_lock = asyncio.Lock()
        version = coordinator.data.get("diagnostics", {}).get("version")
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="MD Parking",
            manufacturer="MD Parking",
            model="Camera Bridge",
            sw_version=str(version) if version else None,
        )

    def _camera_data(self) -> dict | None:
        return next(
            (
                item
                for item in self.coordinator.data.get("cameras", [])
                if item.get("id") == self._camera_id
            ),
            None,
        )

    @property
    def available(self) -> bool:
        item = self._camera_data()
        return (
            self.coordinator.last_update_success
            and item is not None
            and item.get("available", True) is not False
        )

    @property
    def is_on(self) -> bool:
        return self.available

    @property
    def extra_state_attributes(self) -> dict:
        status = next(
            (
                item
                for item in self.coordinator.data.get("diagnostics", {}).get(
                    "cameras", []
                )
                if item.get("id") == self._camera_id
            ),
            {},
        )
        return {
            "source_age_seconds": status.get("source_age_seconds"),
            "last_refresh_error": status.get("last_error"),
        }

    async def stream_source(self) -> str:
        return self._stream_source

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return a short-lived cached still; opened cards use native streaming."""
        now = time.monotonic()
        if (
            self._snapshot is not None
            and now - self._snapshot_at < SNAPSHOT_CACHE_SECONDS
        ):
            return self._snapshot
        async with self._snapshot_lock:
            now = time.monotonic()
            if (
                self._snapshot is not None
                and now - self._snapshot_at < SNAPSHOT_CACHE_SECONDS
            ):
                return self._snapshot
            try:
                image = ImageFrame(self.hass.data[DATA_FFMPEG].binary)
                snapshot = await image.get_image(
                    self._stream_source,
                    extra_cmd="-rtsp_transport tcp",
                    timeout=12,
                )
            except Exception:
                LOGGER.warning("camera snapshot failed for %s", self._camera_id)
                return self._snapshot
            if snapshot:
                self._snapshot = snapshot
                self._snapshot_at = time.monotonic()
            return self._snapshot
