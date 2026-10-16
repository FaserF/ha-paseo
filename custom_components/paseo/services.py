"""Custom services for the Paseo integration."""

from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .client import PaseoClient
from .const import (
    DOMAIN,
    SERVICE_CREATE_AGENT,
    SERVICE_EXECUTE_TASK,
    SERVICE_REFRESH_STATUS,
    SERVICE_SEND_PROMPT,
    SERVICE_STOP_AGENT,
    SERVICE_VALIDATE_CONFIG,
)
from .coordinator import PaseoDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

SCHEMA_CREATE_AGENT = vol.Schema(
    {
        vol.Required("title"): cv.string,
        vol.Required("prompt"): cv.string,
        vol.Optional("workspace", default="/config"): cv.string,
        vol.Optional("role", default="code"): vol.In(["code", "plan", "build", "ask"]),
        vol.Optional("provider"): cv.string,
        vol.Optional("config_entry_id"): cv.string,
    }
)

SCHEMA_SEND_PROMPT = vol.Schema(
    {
        vol.Required("agent_id"): cv.string,
        vol.Required("prompt"): cv.string,
        vol.Optional("config_entry_id"): cv.string,
    }
)

SCHEMA_STOP_AGENT = vol.Schema(
    {
        vol.Required("agent_id"): cv.string,
        vol.Optional("config_entry_id"): cv.string,
    }
)

SCHEMA_EXECUTE_TASK = vol.Schema(
    {
        vol.Required("prompt"): cv.string,
        vol.Optional("title", default="Home Assistant Automation Task"): cv.string,
        vol.Optional("workspace"): cv.string,
        vol.Optional("role", default="code"): cv.string,
        vol.Optional("config_entry_id"): cv.string,
    }
)

SCHEMA_TARGET = vol.Schema(
    {
        vol.Optional("config_entry_id"): cv.string,
    }
)


def _get_entry_client(
    hass: HomeAssistant, call: ServiceCall
) -> tuple[PaseoClient, PaseoDataUpdateCoordinator]:
    """Retrieve the targeted PaseoClient and coordinator."""
    entries = hass.data.get(DOMAIN, {})
    if not entries:
        raise HomeAssistantError("No Paseo instances are configured.")

    entry_id = call.data.get("config_entry_id")
    if entry_id:
        if entry_id not in entries:
            raise HomeAssistantError(f"Paseo config entry '{entry_id}' not found.")
        return entries[entry_id]["client"], entries[entry_id]["coordinator"]

    # Default to first available entry
    first_entry_id = next(iter(entries))
    return entries[first_entry_id]["client"], entries[first_entry_id]["coordinator"]


async def async_setup_services(hass: HomeAssistant) -> None:
    """Register Paseo services with Home Assistant."""

    async def handle_create_agent(call: ServiceCall) -> None:
        """Handle spawning an autonomous Paseo agent."""
        client, coordinator = _get_entry_client(hass, call)
        title = call.data["title"]
        prompt = call.data["prompt"]
        workspace = call.data.get("workspace", "/config")
        role = call.data.get("role", "code")
        provider = call.data.get("provider", "omniroute/coding-cascade")

        _LOGGER.info("Spawning Paseo agent: '%s' in workspace '%s'", title, workspace)
        await client.async_create_agent(
            title=title,
            initial_prompt=prompt,
            workspace=workspace,
            role=role,
            provider=provider,
        )
        await coordinator.async_request_refresh()

    async def handle_send_prompt(call: ServiceCall) -> None:
        """Handle sending a message to a running agent."""
        client, coordinator = _get_entry_client(hass, call)
        agent_id = call.data["agent_id"]
        prompt = call.data["prompt"]

        _LOGGER.info("Sending prompt to Paseo agent '%s'", agent_id)
        await client.async_send_agent_prompt(agent_id=agent_id, prompt=prompt)
        await coordinator.async_request_refresh()

    async def handle_stop_agent(call: ServiceCall) -> None:
        """Handle stopping an active agent."""
        client, coordinator = _get_entry_client(hass, call)
        agent_id = call.data["agent_id"]

        _LOGGER.info("Stopping Paseo agent '%s'", agent_id)
        await client.async_stop_agent(agent_id=agent_id)
        await coordinator.async_request_refresh()

    async def handle_execute_task(call: ServiceCall) -> None:
        """Handle executing an autonomous smart home coding task."""
        client, coordinator = _get_entry_client(hass, call)
        title = call.data.get("title", "Home Assistant Automation Task")
        prompt = call.data["prompt"]
        workspace = call.data.get("workspace", "/config")
        role = call.data.get("role", "code")

        _LOGGER.info("Executing Paseo AI Task '%s'", title)
        await client.async_create_agent(
            title=title,
            initial_prompt=prompt,
            workspace=workspace,
            role=role,
        )
        await coordinator.async_request_refresh()

    async def handle_validate_config(call: ServiceCall) -> None:
        """Handle triggering configuration validation."""
        _, coordinator = _get_entry_client(hass, call)
        _LOGGER.info("Triggering Home Assistant configuration check via Paseo")
        try:
            await hass.services.async_call("homeassistant", "check_config")
        except Exception as exc:  # noqa: BLE001
            _LOGGER.warning("Could not invoke native check_config: %s", exc)
        await coordinator.async_request_refresh()

    async def handle_refresh_status(call: ServiceCall) -> None:
        """Handle forcing coordinator refresh."""
        _, coordinator = _get_entry_client(hass, call)
        await coordinator.async_request_refresh()

    for name, handler, schema in [
        (SERVICE_CREATE_AGENT, handle_create_agent, SCHEMA_CREATE_AGENT),
        (SERVICE_SEND_PROMPT, handle_send_prompt, SCHEMA_SEND_PROMPT),
        (SERVICE_STOP_AGENT, handle_stop_agent, SCHEMA_STOP_AGENT),
        (SERVICE_EXECUTE_TASK, handle_execute_task, SCHEMA_EXECUTE_TASK),
        (SERVICE_VALIDATE_CONFIG, handle_validate_config, SCHEMA_TARGET),
        (SERVICE_REFRESH_STATUS, handle_refresh_status, SCHEMA_TARGET),
    ]:
        if not (hass.services.has_service(DOMAIN, name) is True):
            hass.services.async_register(DOMAIN, name, handler, schema=schema)
