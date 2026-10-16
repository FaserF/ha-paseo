"""Custom services for the Paseo integration."""

from __future__ import annotations

import base64
import logging
from typing import Any

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .client import PaseoClient
from .const import (
    DOMAIN,
    SERVICE_CREATE_AGENT,
    SERVICE_EXECUTE_TASK,
    SERVICE_GENERATE_IMAGE,
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

SCHEMA_GENERATE_IMAGE = vol.Schema(
    {
        vol.Required("prompt"): cv.string,
        vol.Optional("model", default="omniroute/flux-schnell"): cv.string,
        vol.Optional("size", default="1024x1024"): cv.string,
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

    async def handle_generate_image(call: ServiceCall) -> None:
        """Handle generating an AI image via Paseo / OmniRoute."""
        client, coordinator = _get_entry_client(hass, call)
        prompt = call.data["prompt"]
        model = call.data.get("model", "omniroute/flux-schnell")
        size = call.data.get("size", "1024x1024")

        _LOGGER.info("Generating AI image for prompt: '%s'", prompt[:60])
        images = await client.async_generate_image(prompt=prompt, model=model, size=size)
        if images:
            img_val = images[0]
            img_bytes: bytes | None = None
            if img_val.startswith("http"):
                session = await client._get_session()
                async with session.get(img_val) as resp:
                    if resp.status == 200:
                        img_bytes = await resp.read()
            else:
                img_bytes = base64.b64decode(img_val)

            if img_bytes:
                entry_data = hass.data[DOMAIN].get(coordinator.entry.entry_id, {})
                image_entity = entry_data.get("latest_image_entity")
                if image_entity:
                    image_entity.set_image(img_bytes)

    hass.services.async_register(
        DOMAIN, SERVICE_CREATE_AGENT, handle_create_agent, schema=SCHEMA_CREATE_AGENT
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SEND_PROMPT, handle_send_prompt, schema=SCHEMA_SEND_PROMPT
    )
    hass.services.async_register(
        DOMAIN, SERVICE_STOP_AGENT, handle_stop_agent, schema=SCHEMA_STOP_AGENT
    )
    hass.services.async_register(
        DOMAIN, SERVICE_EXECUTE_TASK, handle_execute_task, schema=SCHEMA_EXECUTE_TASK
    )
    hass.services.async_register(
        DOMAIN, SERVICE_VALIDATE_CONFIG, handle_validate_config, schema=SCHEMA_TARGET
    )
    hass.services.async_register(
        DOMAIN, SERVICE_REFRESH_STATUS, handle_refresh_status, schema=SCHEMA_TARGET
    )
    hass.services.async_register(
        DOMAIN, SERVICE_GENERATE_IMAGE, handle_generate_image, schema=SCHEMA_GENERATE_IMAGE
    )
