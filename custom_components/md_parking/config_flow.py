"""Pairing and provider SMS authentication flow."""

from __future__ import annotations

import time

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import BridgeApiError, BridgeClient, normalize_bridge_url
from .const import CONF_API_TOKEN, CONF_BRIDGE_URL, DOMAIN

PHONE_SCHEMA = vol.Schema({vol.Required("phone"): vol.All(str, vol.Length(min=10))})
OBJECT_SCHEMA = vol.Schema({vol.Required("object_id"): vol.All(str, vol.Length(min=1))})
CODE_SCHEMA = vol.Schema({vol.Required("code"): vol.All(str, vol.Length(min=1))})


class AuthFlowMixin:
    """Shared SMS flow used for initial setup and reauthentication."""

    _client: BridgeClient
    _phone: str
    _object_id: str

    async def _auth_post(self, operation, *args) -> str | None:
        try:
            await operation(*args)
        except BridgeApiError as exc:
            if exc.code == "cannot_connect":
                return "cannot_connect"
            return "auth_failed"
        return None

    async def async_step_phone(self, user_input=None) -> FlowResult:
        errors = {}
        if user_input is not None:
            self._phone = user_input["phone"].strip()
            error = await self._auth_post(self._client.request_code, self._phone)
            if error is None:
                return await self.async_step_object()
            errors["base"] = error
        return self.async_show_form(
            step_id="phone", data_schema=PHONE_SCHEMA, errors=errors
        )

    async def async_step_object(self, user_input=None) -> FlowResult:
        errors = {}
        if user_input is not None:
            self._object_id = user_input["object_id"].strip()
            error = await self._auth_post(
                self._client.request_code, self._phone, self._object_id
            )
            if error is None:
                return await self.async_step_code()
            errors["base"] = error
        return self.async_show_form(
            step_id="object", data_schema=OBJECT_SCHEMA, errors=errors
        )


class ConfigFlow(AuthFlowMixin, config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 2

    def __init__(self) -> None:
        self._url = ""
        self._token = ""
        self._phone = ""
        self._object_id = ""

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}
        if user_input is not None:
            try:
                self._url = normalize_bridge_url(user_input[CONF_BRIDGE_URL])
                self._token = user_input.get(CONF_API_TOKEN, "").strip()
                self._client = BridgeClient(
                    async_get_clientsession(self.hass), self._url, self._token
                )
                if not self._token:
                    self._token = await self._client.pair()
                diagnostics = await self._client.diagnostics()
            except ValueError:
                errors["base"] = "invalid_url"
            except BridgeApiError as exc:
                errors["base"] = (
                    "pairing_disabled"
                    if exc.code == "pairing_unavailable"
                    else "cannot_connect"
                )
            else:
                await self.async_set_unique_id(self._url)
                self._abort_if_unique_id_configured()
                if diagnostics.get("auth_state") == "authenticated":
                    return self._create_entry()
                return await self.async_step_phone()
        return self.async_show_form(
            step_id="user", data_schema=self._url_schema(), errors=errors
        )

    async def async_step_code(self, user_input=None) -> FlowResult:
        errors = {}
        if user_input is not None:
            error = await self._auth_post(
                self._client.authorize,
                self._phone,
                self._object_id,
                user_input["code"].strip(),
            )
            if error is None:
                return self._create_entry()
            errors["base"] = error
        return self.async_show_form(
            step_id="code", data_schema=CODE_SCHEMA, errors=errors
        )

    def _create_entry(self) -> FlowResult:
        return self.async_create_entry(
            title="MD Parking",
            data={CONF_BRIDGE_URL: self._url, CONF_API_TOKEN: self._token},
        )

    @staticmethod
    def _url_schema() -> vol.Schema:
        return vol.Schema(
            {
                vol.Required(CONF_BRIDGE_URL): str,
                vol.Optional(CONF_API_TOKEN, default=""): str,
            }
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return MdParkingOptionsFlow(config_entry)


class MdParkingOptionsFlow(AuthFlowMixin, config_entries.OptionsFlow):
    def __init__(self, entry) -> None:
        self._client_data = entry.data
        self._phone = ""
        self._object_id = ""

    async def async_step_init(self, user_input=None) -> FlowResult:
        self._client = BridgeClient(
            async_get_clientsession(self.hass),
            self._client_data[CONF_BRIDGE_URL],
            self._client_data[CONF_API_TOKEN],
        )
        return await self.async_step_phone(user_input)

    async def async_step_code(self, user_input=None) -> FlowResult:
        errors = {}
        if user_input is not None:
            error = await self._auth_post(
                self._client.authorize,
                self._phone,
                self._object_id,
                user_input["code"].strip(),
            )
            if error is None:
                return self.async_create_entry(
                    title="", data={"authenticated_at": int(time.time())}
                )
            errors["base"] = error
        return self.async_show_form(
            step_id="code", data_schema=CODE_SCHEMA, errors=errors
        )
