"""DataUpdateCoordinator for the Paseo integration."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .client import CannotConnect, InvalidAuth, PaseoClient
from .const import CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class PaseoDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Paseo data from the endpoint."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        client: PaseoClient,
    ) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        self.client = client
        poll_interval = entry.options.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.title}",
            update_interval=timedelta(seconds=poll_interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch status, tool catalog, and active agents from Paseo."""
        try:
            status = await self.client.async_get_status()
        except InvalidAuth as err:
            raise UpdateFailed(f"Authentication failed: {err}") from err
        except CannotConnect as err:
            raise UpdateFailed(f"Error communicating with Paseo daemon: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error updating Paseo: {err}") from err

        # Optionally fetch tool catalog and agent counts
        tools: list[dict[str, Any]] = []
        agents: list[dict[str, Any]] = []
        try:
            tools = await self.client.async_list_mcp_tools()
        except Exception as exc:  # noqa: BLE001
            _LOGGER.debug("Failed to fetch tool catalog during update: %s", exc)

        try:
            agents = await self.client.async_list_agents()
        except Exception as exc:  # noqa: BLE001
            _LOGGER.debug("Failed to fetch active agents during update: %s", exc)

        return {
            "connected": True,
            "status": status.get("status", "unknown"),
            "serverId": status.get("serverId", ""),
            "hostname": status.get("hostname", ""),
            "version": status.get("version", ""),
            "listen": status.get("listen", ""),
            "latency_ms": status.get("latency_ms", 0.0),
            "tools_count": len(tools),
            "tools": tools,
            "agents_count": len(agents),
            "agents": agents,
        }
