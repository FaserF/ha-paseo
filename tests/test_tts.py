"""Tests for Paseo TTS platform."""

from unittest.mock import AsyncMock
import pytest
from custom_components.paseo.const import DOMAIN
from custom_components.paseo.coordinator import PaseoDataUpdateCoordinator
from custom_components.paseo.tts import PaseoTextToSpeechEntity, async_setup_entry


@pytest.mark.asyncio
async def test_tts_setup_and_synthesis(mock_hass, mock_config_entry, mock_client):
    """Test TTS entity setup and speech synthesis."""
    coordinator = PaseoDataUpdateCoordinator(mock_hass, mock_config_entry, mock_client)
    await coordinator.async_refresh()

    mock_hass.data[DOMAIN] = {
        mock_config_entry.entry_id: {"coordinator": coordinator, "client": mock_client}
    }

    entities = []

    def mock_add_entities(new_entities):
        entities.extend(new_entities)

    await async_setup_entry(mock_hass, mock_config_entry, mock_add_entities)
    assert len(entities) == 1

    tts_entity = entities[0]
    assert isinstance(tts_entity, PaseoTextToSpeechEntity)
    assert "en" in tts_entity.supported_languages
    assert tts_entity.default_language == "en"

    fmt, audio_bytes = await tts_entity.async_get_tts_audio(
        message="Hello world", language="en", options={"voice": "af_heart", "speed": 1.0}
    )

    assert fmt == "mp3"
    assert audio_bytes == b"fake-mp3-bytes"
    mock_client.async_text_to_speech.assert_called_once()
