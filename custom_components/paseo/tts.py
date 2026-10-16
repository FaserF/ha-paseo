"""Support for Paseo Text-to-Speech (TTS)."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.tts import (
    TextToSpeechEntity,
    TtsAudioType,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .client import PaseoClient
from .const import (
    CONF_TTS_FORMAT,
    CONF_TTS_MODEL,
    CONF_TTS_SPEED,
    CONF_TTS_VOICE,
    DATA_CLIENT,
    DATA_COORDINATOR,
    DEFAULT_TTS_FORMAT,
    DEFAULT_TTS_MODEL,
    DEFAULT_TTS_SPEED,
    DEFAULT_TTS_VOICE,
    DOMAIN,
    SUPPORTED_TTS_FORMATS,
)
from .coordinator import PaseoDataUpdateCoordinator
from .helpers import get_device_info

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Paseo TTS platform from config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    client: PaseoClient = data[DATA_CLIENT]
    coordinator: PaseoDataUpdateCoordinator = data[DATA_COORDINATOR]

    async_add_entities([PaseoTextToSpeechEntity(entry, client, coordinator)])


class PaseoTextToSpeechEntity(
    CoordinatorEntity[PaseoDataUpdateCoordinator], TextToSpeechEntity
):
    """Paseo Text-to-Speech entity."""

    _attr_has_entity_name = True
    _attr_name = "Text-to-Speech"
    _attr_icon = "mdi:account-voice"

    def __init__(
        self,
        entry: ConfigEntry,
        client: PaseoClient,
        coordinator: PaseoDataUpdateCoordinator,
    ) -> None:
        """Initialize TTS entity."""
        super().__init__(coordinator)
        self.entry = entry
        self.client = client
        self._attr_unique_id = f"{entry.entry_id}_tts"
        sw_version = coordinator.data.get("version") if coordinator.data else None
        self._attr_device_info = get_device_info(entry, sw_version)

    @property
    def supported_languages(self) -> list[str]:
        """Return supported languages."""
        return ["en", "de", "es", "fr", "it", "nl", "pt", "ru", "zh", "ja"]

    @property
    def default_language(self) -> str:
        """Return default language."""
        return "en"

    @property
    def supported_options(self) -> list[str]:
        """Return supported options."""
        return ["voice", "speed"]

    async def async_get_tts_audio(
        self, message: str, language: str, options: dict[str, Any] | None = None
    ) -> TtsAudioType:
        """Synthesize text into speech audio bytes."""
        cfg_options = self.entry.options
        model = cfg_options.get(CONF_TTS_MODEL, DEFAULT_TTS_MODEL)
        voice = (options or {}).get("voice") or cfg_options.get(
            CONF_TTS_VOICE, DEFAULT_TTS_VOICE
        )
        speed = float(
            (options or {}).get("speed")
            or cfg_options.get(CONF_TTS_SPEED, DEFAULT_TTS_SPEED)
        )
        response_format = cfg_options.get(CONF_TTS_FORMAT, DEFAULT_TTS_FORMAT)
        if response_format not in SUPPORTED_TTS_FORMATS:
            response_format = "mp3"

        try:
            audio_bytes = await self.client.async_text_to_speech(
                text=message,
                model=model,
                voice=voice,
                response_format=response_format,
                speed=speed,
            )
            return response_format, audio_bytes
        except Exception as err:  # noqa: BLE001
            _LOGGER.error("Paseo TTS synthesis failed: %s", err)
            return None, None
