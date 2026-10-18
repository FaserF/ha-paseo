"""The Paseo integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .client import PaseoClient
from .const import (
    CONF_API_KEY,
    CONF_URL,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import PaseoDataUpdateCoordinator
from .services import async_setup_services

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up the Paseo component."""
    hass.data.setdefault(DOMAIN, {})
    await async_setup_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Paseo from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    url = entry.data[CONF_URL]
    api_key = entry.data.get(CONF_API_KEY)
    session = async_get_clientsession(hass)

    client = PaseoClient(url, api_key=api_key, session=session)
    coordinator = PaseoDataUpdateCoordinator(hass, entry, client)

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "client": client,
        "coordinator": coordinator,
    }

    await async_setup_services(hass)

    # Set up enabled platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        data = hass.data[DOMAIN].pop(entry.entry_id, {})
        client: PaseoClient | None = data.get("client")
        if client:
            await client.close()

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update — avoid full reload when possible.

    A full reload is only triggered when the poll interval changes (as the
    coordinator cannot update its interval at runtime). All other option
    changes (e.g. model selection, display settings) only trigger a
    coordinator refresh so entities stay available.
    """
    from .const import CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL

    entry_data = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})
    coordinator = entry_data.get("coordinator")

    # Check whether the poll interval changed — if so, full reload is required
    # because DataUpdateCoordinator.update_interval cannot be changed at runtime.
    new_poll_interval = entry.options.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)
    if coordinator is not None:
        current_interval = coordinator.update_interval
        from datetime import timedelta

        new_interval = timedelta(seconds=new_poll_interval)
        if current_interval != new_interval:
            # Poll interval changed — full reload required
            await hass.config_entries.async_reload(entry.entry_id)
            return
        # Only a soft refresh needed
        await coordinator.async_request_refresh()
    else:
        await hass.config_entries.async_reload(entry.entry_id)
