"""Config flow for connecting Home Assistant to the local bridge."""

from __future__ import annotations

import voluptuous as vol
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_API_TOKEN, CONF_BRIDGE_URL, DOMAIN


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Only bridge credentials are accepted; provider credentials remain in the add-on."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        if user_input is not None:
            if not user_input.get(CONF_API_TOKEN):
                try:
                    session=async_get_clientsession(self.hass)
                    async with session.post(user_input[CONF_BRIDGE_URL].rstrip('/')+'/v1/pair',timeout=10) as response:
                        user_input[CONF_API_TOKEN]=(await response.json())['api_token']
                except Exception:
                    return self.async_show_form(step_id='user',data_schema=self._schema(),errors={'base':'cannot_connect'})
            await self.async_set_unique_id(user_input[CONF_BRIDGE_URL])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title="MD Parking Bridge", data=user_input)
        return self.async_show_form(
            step_id="user",
            data_schema=self._schema(),
        )

    @staticmethod
    def _schema():
        return vol.Schema(
                {
                    vol.Required(CONF_BRIDGE_URL): str,
                    vol.Optional(CONF_API_TOKEN, default=''): str,
                }
        )
