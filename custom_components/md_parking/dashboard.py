"""Create and safely migrate the MD Parking dashboard."""

from __future__ import annotations

import asyncio
import logging
import re
from urllib.parse import urlsplit

from homeassistant.components import frontend
from homeassistant.components.lovelace import LOVELACE_DATA, MODE_STORAGE
from homeassistant.components.lovelace import dashboard as lovelace_dashboard
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .const import CONF_BRIDGE_URL

LOGGER = logging.getLogger(__name__)
DASHBOARD_PATH = "md-parking"


def _digest(unique_id: str) -> str | None:
    match = re.search(r"([0-9a-f]{12})(?:_open)?$", unique_id)
    return match.group(1) if match else None


def _legacy_button_card(entity_id: str) -> dict:
    return {
        "type": "button",
        "entity": entity_id,
        "name": "Открыть шлагбаум",
        "icon": "mdi:gate-open",
        "show_state": False,
        "tap_action": {
            "action": "call-service",
            "service": "button.press",
            "service_data": {"entity_id": entity_id},
            "confirmation": {"text": "Открыть этот шлагбаум?"},
        },
        "hold_action": {"action": "none"},
    }


def _button_card(entity_id: str) -> dict:
    return {
        "type": "tile",
        "entity": entity_id,
        "name": "Открыть шлагбаум",
        "icon": "mdi:gate-open",
        "hide_state": True,
        "tap_action": {
            "action": "call-service",
            "service": "button.press",
            "service_data": {"entity_id": entity_id},
            "confirmation": {"text": "Открыть этот шлагбаум?"},
        },
        "icon_tap_action": {"action": "none"},
        "hold_action": {"action": "none"},
    }


def _recorder_info_card(status_id: str | None) -> dict:
    action = {
        "action": "navigate",
        "navigation_path": f"/{DASHBOARD_PATH}/info",
    }
    if status_id:
        return {
            "type": "tile",
            "entity": status_id,
            "name": "Подключение к видеорегистратору",
            "icon": "mdi:information-outline",
            "hide_state": True,
            "tap_action": action,
            "icon_tap_action": action,
            "hold_action": {"action": "none"},
        }
    return {
        "type": "button",
        "name": "Подключение к видеорегистратору",
        "icon": "mdi:information-outline",
        "show_state": False,
        "tap_action": action,
        "hold_action": {"action": "none"},
    }


def _safe_markdown_label(value: str) -> str:
    return value.replace("`", "'").replace("\r", " ").replace("\n", " ").strip()


def _recorder_view(
    cameras: list[tuple[str, str]], camera_names: dict[str, str], host: str
) -> dict:
    sections = []
    for number, (entity_id, stream_name) in enumerate(cameras, start=1):
        name = _safe_markdown_label(camera_names.get(entity_id) or f"Камера {number}")
        sections.append(
            f"### {name}\n\n"
            "Скопируйте адрес целиком:\n\n"
            f"```text\nrtsp://{host}:8554/{stream_name}\n```"
        )
    content = (
        "## Подключение к видеорегистратору\n\n"
        "Эти стабильные локальные RTSP-адреса подходят для NVR, VLC, "
        "Frigate, Blue Iris и другого ПО с поддержкой RTSP.\n\n"
        + "\n\n".join(sections)
        + "\n\n---\n\n"
        "- видеокодек: **H.264**;\n"
        "- транспорт: **RTSP over TCP**;\n"
        "- аудиодорожки нет;\n"
        "- логин и пароль не требуются внутри доверенной локальной сети.\n\n"
        "Не публикуйте порт **8554** в интернете. Для удалённого просмотра "
        "используйте защищённый доступ к Home Assistant или VPN."
    )
    return {
        "title": "Подключение",
        "path": "info",
        "icon": "mdi:information-outline",
        "subview": True,
        "back_path": f"/{DASHBOARD_PATH}/cameras",
        "cards": [{"type": "markdown", "content": content}],
    }


def _dashboard_config(
    cameras: list[tuple[str, str]],
    buttons: list[tuple[str, str]],
    status_ids: list[str],
    recorder_host: str | None = None,
    camera_names: dict[str, str] | None = None,
    button_factory=_button_card,
    include_car_view: bool = True,
    car_panel: bool = True,
) -> dict:
    button_by_digest = {
        digest: entity_id
        for entity_id, unique_id in buttons
        if (digest := _digest(unique_id)) is not None
    }
    used_buttons: set[str] = set()
    cards: list[dict] = []
    if status_ids:
        cards.append(
            {
                "type": "entities",
                "title": "Состояние MD Parking",
                "show_header_toggle": False,
                "entities": status_ids,
            }
        )
    if recorder_host:
        cards.append(_recorder_info_card(status_ids[0] if status_ids else None))
    for entity_id, unique_id in cameras:
        camera_card = {
            "type": "picture-entity",
            "entity": entity_id,
            "camera_view": "auto",
            "show_name": True,
            "show_state": True,
            "tap_action": {"action": "more-info"},
        }
        digest = _digest(unique_id)
        button_id = button_by_digest.get(digest) if digest else None
        if button_id:
            used_buttons.add(button_id)
            cards.append(
                {
                    "type": "vertical-stack",
                    "cards": [camera_card, button_factory(button_id)],
                }
            )
        else:
            cards.append(camera_card)
    unused_buttons = [
        entity_id for entity_id, _ in buttons if entity_id not in used_buttons
    ]
    if unused_buttons:
        cards.append(
            {
                "type": "horizontal-stack",
                "cards": [button_factory(entity_id) for entity_id in unused_buttons],
            }
        )
    views = [
        {
            "title": "MD Parking",
            "path": "cameras",
            "icon": "mdi:cctv",
            "cards": cards,
        }
    ]
    if recorder_host:
        views.append(_recorder_view(cameras, camera_names or {}, recorder_host))
    if include_car_view:
        car_cards: list[dict] = []
        for entity_id, unique_id in cameras:
            camera_card = {
                "type": "picture-entity",
                "entity": entity_id,
                "camera_view": "auto",
                "show_name": True,
                "show_state": False,
                "tap_action": {"action": "more-info"},
            }
            digest = _digest(unique_id)
            button_id = button_by_digest.get(digest) if digest else None
            if button_id:
                used_buttons.add(button_id)
                car_cards.append(
                    {
                        "type": "vertical-stack",
                        "cards": [camera_card, button_factory(button_id)],
                    }
                )
            else:
                car_cards.append(camera_card)
        remaining_buttons = [
            entity_id for entity_id, _ in buttons if entity_id not in used_buttons
        ]
        if remaining_buttons:
            car_cards.extend(button_factory(entity_id) for entity_id in remaining_buttons)
        views.append(
            {
                "title": "Авто",
                "path": "car",
                "icon": "mdi:car",
                "panel": car_panel,
                "cards": [
                    {
                        "type": "grid",
                        "columns": 2,
                        "square": False,
                        "cards": car_cards,
                    }
                ],
            }
        )
    return {"views": views}


def _is_legacy_generated(
    current: object, camera_ids: set[str], button_ids: set[str]
) -> bool:
    """Recognize only layouts generated by releases 0.2.8 through 0.3.2."""
    if not isinstance(current, dict):
        return False
    views = current.get("views")
    if not isinstance(views, list) or len(views) != 1:
        return False
    view = views[0]
    if not isinstance(view, dict) or view.get("path") != "cameras":
        return False
    cards = view.get("cards")
    if not isinstance(cards, list):
        return False
    seen_cameras: set[str] = set()
    seen_buttons: set[str] = set()
    for card in cards:
        if not isinstance(card, dict):
            return False
        if card.get("type") == "picture-entity":
            entity_id = card.get("entity")
            if entity_id not in camera_ids:
                return False
            seen_cameras.add(entity_id)
            continue
        if card.get("type") != "horizontal-stack":
            return False
        children = card.get("cards")
        if not isinstance(children, list):
            return False
        for child in children:
            if not isinstance(child, dict) or child.get("type") != "button":
                return False
            entity_id = child.get("entity")
            if entity_id not in button_ids:
                return False
            seen_buttons.add(entity_id)
    return seen_cameras == camera_ids and seen_buttons in (set(), button_ids)


async def _entry_entities(
    hass: HomeAssistant, entry: ConfigEntry
) -> tuple[list[tuple[str, str]], list[tuple[str, str]], list[str]]:
    registry = er.async_get(hass)
    for _ in range(10):
        entities = [
            item
            for item in registry.entities.values()
            if item.config_entry_id == entry.entry_id
        ]
        cameras = sorted(
            (item.entity_id, item.unique_id)
            for item in entities
            if item.domain == "camera"
        )
        if cameras:
            break
        await asyncio.sleep(1)
    else:
        return [], [], []
    buttons = sorted(
        (item.entity_id, item.unique_id) for item in entities if item.domain == "button"
    )
    status_ids = sorted(
        item.entity_id for item in entities if item.domain == "binary_sensor"
    )
    return cameras, buttons, status_ids


async def async_ensure_dashboard(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Create a sidebar dashboard without overwriting user changes."""
    try:
        cameras, buttons, status_ids = await _entry_entities(hass, entry)
        if not cameras or LOVELACE_DATA not in hass.data:
            return
        host = urlsplit(entry.data[CONF_BRIDGE_URL]).hostname
        if not host:
            return
        recorder_host = f"[{host}]" if ":" in host else host
        camera_names = {
            entity_id: state.name
            for entity_id, _ in cameras
            if (state := hass.states.get(entity_id)) is not None
        }
        desired = _dashboard_config(
            cameras,
            buttons,
            status_ids,
            recorder_host,
            camera_names,
        )
        previous_release = _dashboard_config(
            cameras,
            buttons,
            status_ids,
            recorder_host,
            camera_names,
            include_car_view=False,
        )
        release_051 = _dashboard_config(
            cameras,
            buttons,
            status_ids,
            recorder_host,
            camera_names,
            car_panel=False,
        )
        release_042 = _dashboard_config(cameras, buttons, status_ids)
        early_040 = _dashboard_config(
            cameras, buttons, status_ids, button_factory=_legacy_button_card
        )
        camera_ids = {entity_id for entity_id, _ in cameras}
        button_ids = {entity_id for entity_id, _ in buttons}

        collection = lovelace_dashboard.DashboardsCollection(hass)
        await collection.async_load()
        existing = next(
            (
                item
                for item in collection.async_items()
                if item.get("url_path") == DASHBOARD_PATH
            ),
            None,
        )
        if existing:
            config = hass.data[LOVELACE_DATA].dashboards.get(DASHBOARD_PATH)
            if config is None:
                return
            current = await config.async_load(False)
            if current == desired:
                return
            if current in (release_051, previous_release, release_042, early_040) or _is_legacy_generated(
                current, camera_ids, button_ids
            ):
                await config.async_save(desired)
                LOGGER.info("migrated generated MD Parking dashboard")
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
        await config.async_save(desired)
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
    except asyncio.CancelledError:
        raise
    except Exception:
        LOGGER.exception("could not create or migrate MD Parking dashboard")
