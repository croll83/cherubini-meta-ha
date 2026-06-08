"""Config flow per Cherubini META."""
from __future__ import annotations
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_HOST, CONF_USERNAME, CONF_PASSWORD
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import CherubiniMetaApi, CherubiniAuthError, CherubiniApiError
from .const import DOMAIN


class CherubiniMetaConfigFlow(ConfigFlow, domain=DOMAIN):
    """Flusso di configurazione guidato."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors: dict[str, str] = {}
        if user_input is not None:
            session = async_get_clientsession(self.hass)
            api = CherubiniMetaApi(
                session, user_input[CONF_HOST],
                user_input[CONF_USERNAME], user_input[CONF_PASSWORD],
            )
            try:
                info = await api.login()
            except CherubiniAuthError:
                errors["base"] = "invalid_auth"
            except CherubiniApiError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                errors["base"] = "unknown"
            else:
                gw = info.get("gatewayId") or user_input[CONF_HOST]
                await self.async_set_unique_id(gw)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Cherubini META ({gw})", data=user_input)

        schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_USERNAME): str,
            vol.Required(CONF_PASSWORD): str,
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
