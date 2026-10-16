"""Support for Paseo AI Task platform."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .client import PaseoClient
from .const import (
    CONF_AI_TASK_MODEL,
    CONF_AI_TASK_PROMPT,
    CONF_WORKSPACE,
    DEFAULT_AI_TASK_MODEL,
    DEFAULT_AI_TASK_PROMPT,
    DEFAULT_WORKSPACE,
    DOMAIN,
)
from .coordinator import PaseoDataUpdateCoordinator
from .helpers import get_device_info

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AI Task entities from config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    client: PaseoClient = data["client"]
    coordinator: PaseoDataUpdateCoordinator = data["coordinator"]

    async_add_entities([PaseoAITaskEntity(entry, client, coordinator)])


class PaseoAITaskEntity(CoordinatorEntity[PaseoDataUpdateCoordinator], Entity):
    """Paseo AI Task entity for smart home reasoning and autonomous code tasks."""

    _attr_has_entity_name = True
    _attr_name = "Task Engine"
    _attr_icon = "mdi:auto-fix"

    def __init__(
        self,
        entry: ConfigEntry,
        client: PaseoClient,
        coordinator: PaseoDataUpdateCoordinator,
    ) -> None:
        """Initialize the AI Task entity."""
        super().__init__(coordinator)
        self.entry = entry
        self.client = client
        self._attr_unique_id = f"{entry.entry_id}_ai_task"
        sw_version = coordinator.data.get("version") if coordinator.data else None
        self._attr_device_info = get_device_info(entry, sw_version)

        self._state = "idle"
        self._last_execution: dict[str, Any] = {}

    @property
    def state(self) -> str:
        """Return the current task engine state."""
        return self._state

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return task execution details."""
        options = self.entry.options
        return {
            "model": options.get(CONF_AI_TASK_MODEL, DEFAULT_AI_TASK_MODEL),
            "workspace": options.get(CONF_WORKSPACE, DEFAULT_WORKSPACE),
            "last_execution": self._last_execution,
        }

    async def async_execute_task(
        self,
        prompt: str,
        title: str = "Home Assistant Automation Task",
        workspace: str | None = None,
        role: str = "code",
        model: str | None = None,
    ) -> dict[str, Any]:
        """Execute an autonomous AI task on Paseo."""
        options = self.entry.options
        target_workspace = workspace or options.get(CONF_WORKSPACE, DEFAULT_WORKSPACE)
        target_model = model or options.get(CONF_AI_TASK_MODEL, DEFAULT_AI_TASK_MODEL)
        system_prompt = options.get(CONF_AI_TASK_PROMPT, DEFAULT_AI_TASK_PROMPT)

        self._state = "running"
        self.async_write_ha_state()

        start_time = datetime.now(UTC).isoformat()
        try:
            # First attempt to spawn an autonomous Paseo agent
            result = await self.client.async_create_agent(
                title=title,
                initial_prompt=f"{system_prompt}\n\nTask:\n{prompt}",
                workspace=target_workspace,
                role=role,
                provider=target_model,
            )
            self._state = "completed"
            self._last_execution = {
                "title": title,
                "status": "success",
                "started_at": start_time,
                "finished_at": datetime.now(UTC).isoformat(),
                "result": result,
            }
            return result
        except Exception as exc:  # noqa: BLE001
            _LOGGER.error("Failed executing Paseo task '%s': %s", title, exc)
            self._state = "error"
            self._last_execution = {
                "title": title,
                "status": "failed",
                "error": str(exc),
                "started_at": start_time,
                "finished_at": datetime.now(UTC).isoformat(),
            }
            raise
        finally:
            self.async_write_ha_state()
            await self.coordinator.async_request_refresh()
