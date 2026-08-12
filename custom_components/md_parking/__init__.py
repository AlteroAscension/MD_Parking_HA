"""MD Parking integration.

The integration is intentionally a local bridge client. It never stores or
uses provider credentials, signed sources, or barrier-provider identifiers.
"""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS
from .coordinator import MdParkingCoordinator
from .dashboard import async_ensure_dashboard


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate the original paired bridge entry to the SMS-auth flow schema."""
    if entry.version < 2:
        hass.config_entries.async_update_entry(entry, version=2)
        return True
    return entry.version == 2


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = MdParkingCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    task = hass.async_create_task(
        async_ensure_dashboard(hass, entry), "create MD Parking dashboard"
    )
    entry.async_on_unload(task.cancel)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    hass.data[DOMAIN].pop(entry.entry_id, None)
    if not hass.data[DOMAIN]:
        hass.data.pop(DOMAIN, None)
    return True
