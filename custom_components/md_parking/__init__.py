"""MD Parking integration.

The integration is intentionally a local bridge client. It never stores or
uses provider credentials, signed sources, or barrier-provider identifiers.
"""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = dict(entry.data)
    await hass.config_entries.async_forward_entry_setups(entry, ['camera'])
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    await hass.config_entries.async_unload_platforms(entry, ['camera'])
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True
