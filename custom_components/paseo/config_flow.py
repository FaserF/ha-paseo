"""Config flow for the Paseo integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .client import CannotConnect, InvalidAuth, PaseoClient
from .const import (
    CONF_AI_TASK_MODEL,
    CONF_AI_TASK_PROMPT,
    CONF_API_KEY,
    CONF_AUTO_ACCEPT,
    CONF_NAME,
    CONF_POLL_INTERVAL,
    CONF_URL,
    CONF_WORKSPACE,
    DEFAULT_AI_TASK_MODEL,
    DEFAULT_AI_TASK_PROMPT,
    DEFAULT_AUTO_ACCEPT,
    DEFAULT_NAME,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_URL,
    DEFAULT_WORKSPACE,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class PaseoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Paseo."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            url = user_input[CONF_URL].rstrip("/")
            api_key = user_input.get(CONF_API_KEY)
            name = user_input.get(CONF_NAME, DEFAULT_NAME)

            session = async_get_clientsession(self.hass)
            client = PaseoClient(url, api_key=api_key, session=session)

            try:
                status = await client.async_get_status()
                server_id = status.get("serverId")
                hostname = status.get("hostname", name)

                if server_id:
                    await self.async_set_unique_id(server_id)
                    self._abort_if_unique_id_configured()

                title = name if name != DEFAULT_NAME else hostname
                return self.async_create_entry(
                    title=title,
                    data={
                        CONF_URL: url,
                        CONF_API_KEY: api_key,
                        CONF_NAME: title,
                        "server_id": server_id,
                        "hostname": hostname,
                    },
                    options={
                        CONF_AI_TASK_MODEL: DEFAULT_AI_TASK_MODEL,
                        CONF_AI_TASK_PROMPT: DEFAULT_AI_TASK_PROMPT,
                        CONF_WORKSPACE: DEFAULT_WORKSPACE,
                        CONF_AUTO_ACCEPT: DEFAULT_AUTO_ACCEPT,
                        CONF_POLL_INTERVAL: DEFAULT_POLL_INTERVAL,
                    },
                )
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception as exc:  # noqa: BLE001
                _LOGGER.exception("Unexpected exception connecting to Paseo: %s", exc)
                errors["base"] = "unknown"

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Required(CONF_URL, default=DEFAULT_URL): str,
                vol.Optional(CONF_API_KEY): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_hassio(self, discovery_info: dict[str, Any]) -> FlowResult:
        """Handle Supervisor Add-on discovery."""
        url = f"http://{discovery_info.get('host', 'edfe50eb-paseo')}:6767"
        name = "Paseo (Edge Add-on)"

        await self.async_set_unique_id("edfe50eb_paseo_addon")
        self._abort_if_unique_id_configured()

        return await self.async_step_user(
            {
                CONF_NAME: name,
                CONF_URL: url,
                CONF_API_KEY: "",
            }
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> PaseoOptionsFlow:
        """Get the options flow for this handler."""
        return PaseoOptionsFlow(config_entry)


class PaseoOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Paseo integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self.config_entry.options

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_AI_TASK_MODEL,
                    default=options.get(CONF_AI_TASK_MODEL, DEFAULT_AI_TASK_MODEL),
                ): str,
                vol.Optional(
                    CONF_AI_TASK_PROMPT,
                    default=options.get(CONF_AI_TASK_PROMPT, DEFAULT_AI_TASK_PROMPT),
                ): str,
                vol.Optional(
                    CONF_WORKSPACE,
                    default=options.get(CONF_WORKSPACE, DEFAULT_WORKSPACE),
                ): str,
                vol.Optional(
                    CONF_AUTO_ACCEPT,
                    default=options.get(CONF_AUTO_ACCEPT, DEFAULT_AUTO_ACCEPT),
                ): bool,
                vol.Optional(
                    CONF_POLL_INTERVAL,
                    default=options.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL),
                ): vol.All(vol.Coerce(int), vol.Range(min=10, max=3600)),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
