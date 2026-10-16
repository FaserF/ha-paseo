"""Support for Paseo switches."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_AUTO_ACCEPT,
    DEFAULT_AUTO_ACCEPT,
    DOMAIN,
)
from .coordinator import PaseoDataUpdateCoordinator
from .helpers import get_device_info


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Paseo switches based on a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: PaseoDataUpdateCoordinator = data["coordinator"]

    async_add_entities(
        [
            PaseoAutonomousExecutionSwitch(coordinator, entry),
        ]
    )


class PaseoAutonomousExecutionSwitch(
    CoordinatorEntity[PaseoDataUpdateCoordinator], SwitchEntity
):
    """Switch to toggle autonomous execution (auto-accept tool commands)."""

    _attr_has_entity_name = True
    _attr_translation_key = "autonomous_execution"
    _attr_name = "Autonomous Execution"
    _attr_icon = "mdi:shield-bug"

    def __init__(
        self, coordinator: PaseoDataUpdateCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_autonomous_execution"
        sw_version = coordinator.data.get("version") if coordinator.data else None
        self._attr_device_info = get_device_info(entry, sw_version)

    @property
    def is_on(self) -> bool:
        """Return true if autonomous execution is enabled."""
        return bool(self.entry.options.get(CONF_AUTO_ACCEPT, DEFAULT_AUTO_ACCEPT))

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on autonomous execution."""
        new_options = dict(self.entry.options)
        new_options[CONF_AUTO_ACCEPT] = True
        self.hass.config_entries.async_update_entry(self.entry, options=new_options)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off autonomous execution."""
        new_options = dict(self.entry.options)
        new_options[CONF_AUTO_ACCEPT] = False
        self.hass.config_entries.async_update_entry(self.entry, options=new_options)
        self.async_write_ha_state()
