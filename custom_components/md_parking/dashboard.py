"""Create the MD Parking camera dashboard once."""
from __future__ import annotations

import asyncio

from homeassistant.components import frontend
from homeassistant.components.lovelace import LOVELACE_DATA, MODE_STORAGE
from homeassistant.components.lovelace import dashboard as lovelace_dashboard
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN

DASHBOARD_PATH = "md-parking"


def _dashboard_config(entity_ids: list[str]) -> dict:
    return {
        "views": [
            {
                "title": "MD Parking",
                "path": "cameras",
                "icon": "mdi:cctv",
                "cards": [
                    {
                        "type": "picture-entity",
                        "entity": entity_id,
                        "camera_view": "live",
                        "show_name": True,
                        "show_state": True,
                    }
                    for entity_id in entity_ids
                ],
            }
        ]
    }


async def async_ensure_dashboard(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Create a sidebar dashboard without overwriting an existing one."""
    await asyncio.sleep(2)
    registry = er.async_get(hass)
    entity_ids = sorted(
        item.entity_id
        for item in registry.entities.values()
        if item.config_entry_id == entry.entry_id and item.domain == "camera"
    )
    if not entity_ids or LOVELACE_DATA not in hass.data:
        return

    collection = lovelace_dashboard.DashboardsCollection(hass)
    await collection.async_load()
    if any(item.get("url_path") == DASHBOARD_PATH for item in collection.async_items()):
        return

    item = await collection.async_create_item(
        {
            "url_path": DASHBOARD_PATH,
            "title": "MD Parking",
            "icon": "mdi:gate",
            "show_in_sidebar": True,
            "require_admin": False,
        }
    )
    config = lovelace_dashboard.LovelaceStorage(hass, item)
    await config.async_save(_dashboard_config(entity_ids))
    hass.data[LOVELACE_DATA].dashboards[DASHBOARD_PATH] = config
    frontend.async_register_built_in_panel(
        hass,
        "lovelace",
        sidebar_title="MD Parking",
        sidebar_icon="mdi:gate",
        frontend_url_path=DASHBOARD_PATH,
        config={"mode": MODE_STORAGE},
        require_admin=False,
        show_in_sidebar=True,
    )
