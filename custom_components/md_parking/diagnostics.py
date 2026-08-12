"""Secret-safe diagnostics for MD Parking."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    diagnostics = coordinator.data.get("diagnostics", {})
    return {
        "entry_version": entry.version,
        "coordinator_update_success": coordinator.last_update_success,
        "bridge": {
            "version": diagnostics.get("version"),
            "ready": diagnostics.get("ready"),
            "auth_state": diagnostics.get("auth_state"),
            "control_enabled": diagnostics.get("control_enabled"),
            "camera_count": diagnostics.get("camera_count", 0),
            "barrier_count": diagnostics.get("barrier_count", 0),
            "last_failure": diagnostics.get("last_failure"),
            "last_success_age_seconds": diagnostics.get("last_success_age_seconds"),
            "uptime_seconds": diagnostics.get("uptime_seconds"),
            "audit_event_count": diagnostics.get("audit_event_count", 0),
            "cameras": diagnostics.get("cameras", []),
        },
    }
