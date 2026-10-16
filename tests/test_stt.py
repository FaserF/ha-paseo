"""Tests for Paseo STT platform."""

from unittest.mock import AsyncMock, MagicMock
import pytest
from homeassistant.components.stt import SpeechMetadata, SpeechResultState
from custom_components.paseo.const import DOMAIN
from custom_components.paseo.coordinator import PaseoDataUpdateCoordinator
from custom_components.paseo.stt import PaseoSpeechToTextEntity, async_setup_entry


@pytest.mark.asyncio
async def test_stt_setup_and_transcribe(mock_hass, mock_config_entry, mock_client):
    """Test STT entity setup and audio transcription."""
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

    stt_entity = entities[0]
    assert isinstance(stt_entity, PaseoSpeechToTextEntity)
    assert "en" in stt_entity.supported_languages

    async def sample_audio_stream():
        yield b"chunk_1"
        yield b"chunk_2"

    metadata = MagicMock(spec=SpeechMetadata)
    res = await stt_entity.async_process_audio_stream(metadata, sample_audio_stream())

    assert res.result == SpeechResultState.SUCCESS
    assert res.text == "Transcribed speech text"
    mock_client.async_speech_to_text.assert_called_once()
