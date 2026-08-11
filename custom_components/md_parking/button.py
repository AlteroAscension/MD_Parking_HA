"""Explicit MD Parking barrier buttons."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_API_TOKEN, CONF_BRIDGE_URL, DOMAIN
from .coordinator import MdParkingCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: MdParkingCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        MdParkingOpenButton(coordinator, entry, item)
        for item in coordinator.data.get("barriers", [])
    )


class MdParkingOpenButton(CoordinatorEntity[MdParkingCoordinator], ButtonEntity):
    """A deliberate one-shot barrier action, never called by camera refresh."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:gate-open"

    def __init__(
        self, coordinator: MdParkingCoordinator, entry: ConfigEntry, barrier: dict
    ) -> None:
        super().__init__(coordinator)
        self._barrier_id = barrier["id"]
        self._attr_unique_id = barrier["id"] + "_open"
        self._attr_name = f'Открыть {barrier["name"]}'
        self._url = entry.data[CONF_BRIDGE_URL].rstrip("/")
        self._headers = {"Authorization": f"Bearer {entry.data[CONF_API_TOKEN]}"}
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="MD Parking",
            manufacturer="MD Parking",
            model="Camera Bridge",
        )

    @property
    def available(self) -> bool:
        return (
            self.coordinator.last_update_success
            and self.coordinator.data.get("control_enabled") is True
            and any(
                item.get("id") == self._barrier_id
                for item in self.coordinator.data.get("barriers", [])
            )
        )

    async def async_press(self) -> None:
        session = async_get_clientsession(self.hass)
        async with session.post(
            f"{self._url}/v1/barriers/{self._barrier_id}/open",
            json={"confirm": True},
            headers=self._headers,
            timeout=20,
        ) as response:
            payload = await response.json()
            if response.status != 200 or payload.get("status") != "accepted":
                reason = payload.get("error", "control_failed")
                raise HomeAssistantError(f"MD Parking barrier action failed: {reason}")
