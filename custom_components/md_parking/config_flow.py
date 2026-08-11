"""Pairing and provider SMS authentication flow."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_API_TOKEN, CONF_BRIDGE_URL, DOMAIN


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION=2
    def __init__(self): self._url=''; self._token=''; self._phone=''; self._object_id=''

    async def _post(self,path,payload):
        session=async_get_clientsession(self.hass)
        async with session.post(self._url+path,json=payload,headers={'Authorization':f'Bearer {self._token}'},timeout=25) as response:
            if response.status != 200: raise ValueError(await response.text())
            return await response.json()

    async def async_step_user(self,user_input=None)->FlowResult:
        if user_input is not None:
            self._url=user_input[CONF_BRIDGE_URL].rstrip('/')
            self._token=user_input.get(CONF_API_TOKEN,'')
            try:
                if not self._token:
                    session=async_get_clientsession(self.hass)
                    async with session.post(self._url+'/v1/pair',timeout=10) as response:
                        if response.status != 200: raise ValueError(await response.text())
                        self._token=(await response.json())['api_token']
            except Exception: return self.async_show_form(step_id='user',data_schema=self._url_schema(),errors={'base':'cannot_connect'})
            return await self.async_step_phone()
        return self.async_show_form(step_id='user',data_schema=self._url_schema())

    async def async_step_phone(self,user_input=None)->FlowResult:
        if user_input is not None:
            self._phone=user_input['phone']
            try: await self._post('/v1/auth/request-code',{'phone':self._phone})
            except Exception: return self.async_show_form(step_id='phone',data_schema=self._phone_schema(),errors={'base':'auth_failed'})
            return await self.async_step_object()
        return self.async_show_form(step_id='phone',data_schema=self._phone_schema())

    async def async_step_object(self,user_input=None)->FlowResult:
        if user_input is not None:
            self._object_id=user_input['object_id']
            try: await self._post('/v1/auth/request-code',{'phone':self._phone,'object_id':self._object_id})
            except Exception: return self.async_show_form(step_id='object',data_schema=self._object_schema(),errors={'base':'auth_failed'})
            return await self.async_step_code()
        return self.async_show_form(step_id='object',data_schema=self._object_schema())

    async def async_step_code(self,user_input=None)->FlowResult:
        if user_input is not None:
            try: await self._post('/v1/auth/authorize',{'phone':self._phone,'object_id':self._object_id,'code':user_input['code']})
            except Exception: return self.async_show_form(step_id='code',data_schema=self._code_schema(),errors={'base':'auth_failed'})
            await self.async_set_unique_id(self._url); self._abort_if_unique_id_configured()
            return self.async_create_entry(title='MD Parking',data={CONF_BRIDGE_URL:self._url,CONF_API_TOKEN:self._token})
        return self.async_show_form(step_id='code',data_schema=self._code_schema())

    @staticmethod
    def _url_schema(): return vol.Schema({vol.Required(CONF_BRIDGE_URL):str,vol.Optional(CONF_API_TOKEN,default=''):str})
    @staticmethod
    def _phone_schema(): return vol.Schema({vol.Required('phone'):str})
    @staticmethod
    def _object_schema(): return vol.Schema({vol.Required('object_id'):str})
    @staticmethod
    def _code_schema(): return vol.Schema({vol.Required('code'):str})

    @staticmethod
    def async_get_options_flow(config_entry):
        return MdParkingOptionsFlow(config_entry)


class MdParkingOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, entry):
        self._url=entry.data[CONF_BRIDGE_URL].rstrip('/')
        self._token=entry.data[CONF_API_TOKEN]
        self._phone=''; self._object_id=''

    async def _post(self,path,payload):
        session=async_get_clientsession(self.hass)
        async with session.post(self._url+path,json=payload,headers={'Authorization':f'Bearer {self._token}'},timeout=25) as response:
            if response.status != 200: raise ValueError(await response.text())
            return await response.json()

    async def async_step_init(self,user_input=None): return await self.async_step_phone(user_input)

    async def async_step_phone(self,user_input=None):
        if user_input is not None:
            self._phone=user_input['phone']
            try: await self._post('/v1/auth/request-code',{'phone':self._phone})
            except Exception: return self.async_show_form(step_id='phone',data_schema=ConfigFlow._phone_schema(),errors={'base':'auth_failed'})
            return await self.async_step_object()
        return self.async_show_form(step_id='phone',data_schema=ConfigFlow._phone_schema())

    async def async_step_object(self,user_input=None):
        if user_input is not None:
            self._object_id=user_input['object_id']
            try: await self._post('/v1/auth/request-code',{'phone':self._phone,'object_id':self._object_id})
            except Exception: return self.async_show_form(step_id='object',data_schema=ConfigFlow._object_schema(),errors={'base':'auth_failed'})
            return await self.async_step_code()
        return self.async_show_form(step_id='object',data_schema=ConfigFlow._object_schema())

    async def async_step_code(self,user_input=None):
        if user_input is not None:
            try: await self._post('/v1/auth/authorize',{'phone':self._phone,'object_id':self._object_id,'code':user_input['code']})
            except Exception: return self.async_show_form(step_id='code',data_schema=ConfigFlow._code_schema(),errors={'base':'auth_failed'})
            return self.async_create_entry(title='',data={'authenticated_at':int(__import__('time').time())})
        return self.async_show_form(step_id='code',data_schema=ConfigFlow._code_schema())
