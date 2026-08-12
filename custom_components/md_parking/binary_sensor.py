"""Diagnostic connectivity entity for MD Parking."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MdParkingCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: MdParkingCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MdParkingBridgeStatus(coordinator, entry)])


class MdParkingBridgeStatus(
    CoordinatorEntity[MdParkingCoordinator], BinarySensorEntity
):
    _attr_has_entity_name = True
    _attr_name = "Связь"
    _attr_unique_id = "bridge_connectivity"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: MdParkingCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        version = coordinator.data.get("diagnostics", {}).get("version")
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="MD Parking",
            manufacturer="MD Parking",
            model="Camera Bridge",
            sw_version=str(version) if version else None,
        )

    @property
    def is_on(self) -> bool:
        return self.coordinator.last_update_success

    @property
    def extra_state_attributes(self) -> dict:
        diagnostics = self.coordinator.data.get("diagnostics", {})
        return {
            "bridge_version": diagnostics.get("version"),
            "camera_count": diagnostics.get("camera_count", 0),
            "barrier_count": diagnostics.get("barrier_count", 0),
            "control_enabled": diagnostics.get("control_enabled", False),
            "last_failure": diagnostics.get("last_failure"),
            "last_success_age_seconds": diagnostics.get("last_success_age_seconds"),
        }
