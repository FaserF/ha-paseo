"""Support for Paseo model and mode select entities."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    AVAILABLE_MODELS,
    AVAILABLE_STT_MODELS,
    AVAILABLE_TTS_VOICES,
    CONF_AI_TASK_MODEL,
    CONF_CONVERSATION_MODEL,
    CONF_STT_MODEL,
    CONF_TTS_VOICE,
    DEFAULT_AI_TASK_MODEL,
    DEFAULT_CONVERSATION_MODEL,
    DEFAULT_STT_MODEL,
    DEFAULT_TTS_VOICE,
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
            PaseoTTSVoiceSelect(coordinator, entry),
            PaseoSTTModelSelect(coordinator, entry),
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


class PaseoTTSVoiceSelect(
    CoordinatorEntity[PaseoDataUpdateCoordinator], SelectEntity
):
    """Select entity for the active TTS voice."""

    _attr_has_entity_name = True
    _attr_translation_key = "tts_voice"
    _attr_name = "TTS Voice"
    _attr_icon = "mdi:account-voice"
    _attr_options = AVAILABLE_TTS_VOICES

    def __init__(
        self, coordinator: PaseoDataUpdateCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_tts_voice"
        sw_version = coordinator.data.get("version") if coordinator.data else None
        self._attr_device_info = get_device_info(entry, sw_version)

    @property
    def current_option(self) -> str:
        """Return current selected voice."""
        return str(self.entry.options.get(CONF_TTS_VOICE, DEFAULT_TTS_VOICE))

    async def async_select_option(self, option: str) -> None:
        """Change selected voice."""
        new_options = dict(self.entry.options)
        new_options[CONF_TTS_VOICE] = option
        self.hass.config_entries.async_update_entry(self.entry, options=new_options)
        self.async_write_ha_state()


class PaseoSTTModelSelect(
    CoordinatorEntity[PaseoDataUpdateCoordinator], SelectEntity
):
    """Select entity for the active STT model."""

    _attr_has_entity_name = True
    _attr_translation_key = "stt_model"
    _attr_name = "STT Model"
    _attr_icon = "mdi:microphone"
    _attr_options = AVAILABLE_STT_MODELS

    def __init__(
        self, coordinator: PaseoDataUpdateCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_stt_model"
        sw_version = coordinator.data.get("version") if coordinator.data else None
        self._attr_device_info = get_device_info(entry, sw_version)

    @property
    def current_option(self) -> str:
        """Return current selected STT model."""
        return str(self.entry.options.get(CONF_STT_MODEL, DEFAULT_STT_MODEL))

    async def async_select_option(self, option: str) -> None:
        """Change selected STT model."""
        new_options = dict(self.entry.options)
        new_options[CONF_STT_MODEL] = option
        self.hass.config_entries.async_update_entry(self.entry, options=new_options)
        self.async_write_ha_state()
