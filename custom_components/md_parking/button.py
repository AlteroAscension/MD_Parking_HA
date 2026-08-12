"""Explicit MD Parking barrier buttons."""

from __future__ import annotations

from datetime import datetime

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util.dt import utcnow

from .api import BridgeApiError
from .const import DOMAIN
from .coordinator import MdParkingCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: MdParkingCoordinator = hass.data[DOMAIN][entry.entry_id]
    known: set[str] = set()

    def add_new_entities() -> None:
        entities = []
        for item in coordinator.data.get("barriers", []):
            barrier_id = item.get("id")
            if not isinstance(barrier_id, str) or barrier_id in known:
                continue
            known.add(barrier_id)
            entities.append(MdParkingOpenButton(coordinator, entry, item))
        if entities:
            async_add_entities(entities)

    add_new_entities()
    entry.async_on_unload(coordinator.async_add_listener(add_new_entities))


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
        self._attr_name = f"Открыть {barrier.get('name') or 'шлагбаум'}"
        self._last_triggered: datetime | None = None
        version = coordinator.data.get("diagnostics", {}).get("version")
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="MD Parking",
            manufacturer="MD Parking",
            model="Camera Bridge",
            sw_version=str(version) if version else None,
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

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "last_triggered": self._last_triggered.isoformat()
            if self._last_triggered
            else None
        }

    async def async_press(self) -> None:
        try:
            payload = await self.coordinator.client.open_barrier(self._barrier_id)
        except BridgeApiError as exc:
            if exc.code == "rate_limited":
                raise HomeAssistantError(
                    "Повторное открытие временно ограничено"
                ) from exc
            raise HomeAssistantError(
                f"Команда открытия не выполнена: {exc.code}"
            ) from exc
        if payload.get("status") != "accepted":
            raise HomeAssistantError("MD Parking не подтвердил команду открытия")
        self._last_triggered = utcnow()
        self.async_write_ha_state()
