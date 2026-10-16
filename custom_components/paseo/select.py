"""Support for Paseo model and mode select entities."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    AVAILABLE_MODELS,
    CONF_AI_TASK_MODEL,
    CONF_CONVERSATION_MODEL,
    DEFAULT_AI_TASK_MODEL,
    DEFAULT_CONVERSATION_MODEL,
    DOMAIN,
)
from .coordinator import PaseoDataUpdateCoordinator
from .helpers import get_device_info


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Paseo selects based on a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: PaseoDataUpdateCoordinator = data["coordinator"]

    async_add_entities(
        [
            PaseoConversationModelSelect(coordinator, entry),
            PaseoAiTaskModelSelect(coordinator, entry),
        ]
    )


class PaseoConversationModelSelect(
    CoordinatorEntity[PaseoDataUpdateCoordinator], SelectEntity
):
    """Select entity for the conversation model."""

    _attr_has_entity_name = True
    _attr_translation_key = "conversation_model"
    _attr_name = "Conversation Model"
    _attr_icon = "mdi:brain"
    _attr_options = AVAILABLE_MODELS

    def __init__(
        self, coordinator: PaseoDataUpdateCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_conversation_model"
        sw_version = coordinator.data.get("version") if coordinator.data else None
        self._attr_device_info = get_device_info(entry, sw_version)

    @property
    def current_option(self) -> str:
        """Return the current selected model."""
        return str(
            self.entry.options.get(
                CONF_CONVERSATION_MODEL, DEFAULT_CONVERSATION_MODEL
            )
        )

    async def async_select_option(self, option: str) -> None:
        """Change the selected model."""
        new_options = dict(self.entry.options)
        new_options[CONF_CONVERSATION_MODEL] = option
        self.hass.config_entries.async_update_entry(self.entry, options=new_options)
        self.async_write_ha_state()


class PaseoAiTaskModelSelect(
    CoordinatorEntity[PaseoDataUpdateCoordinator], SelectEntity
):
    """Select entity for the AI task model."""

    _attr_has_entity_name = True
    _attr_translation_key = "ai_task_model"
    _attr_name = "AI Task Model"
    _attr_icon = "mdi:chip"
    _attr_options = AVAILABLE_MODELS

    def __init__(
        self, coordinator: PaseoDataUpdateCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_ai_task_model"
        sw_version = coordinator.data.get("version") if coordinator.data else None
        self._attr_device_info = get_device_info(entry, sw_version)

    @property
    def current_option(self) -> str:
        """Return the current selected AI task model."""
        return str(
            self.entry.options.get(CONF_AI_TASK_MODEL, DEFAULT_AI_TASK_MODEL)
        )

    async def async_select_option(self, option: str) -> None:
        """Change the selected model."""
        new_options = dict(self.entry.options)
        new_options[CONF_AI_TASK_MODEL] = option
        self.hass.config_entries.async_update_entry(self.entry, options=new_options)
        self.async_write_ha_state()
