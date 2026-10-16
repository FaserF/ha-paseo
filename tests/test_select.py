"""Tests for Paseo select platform."""

import pytest
from custom_components.paseo.const import (
    CONF_AI_TASK_MODEL,
    CONF_CONVERSATION_MODEL,
    CONF_STT_MODEL,
    CONF_TTS_VOICE,
    DOMAIN,
)
from custom_components.paseo.coordinator import PaseoDataUpdateCoordinator
from custom_components.paseo.select import (
    PaseoAiTaskModelSelect,
    PaseoConversationModelSelect,
    PaseoSTTModelSelect,
    PaseoTTSVoiceSelect,
    async_setup_entry,
)


@pytest.mark.asyncio
async def test_select_entities(mock_hass, mock_config_entry, mock_client):
    """Test select entities for model switching."""
    coordinator = PaseoDataUpdateCoordinator(mock_hass, mock_config_entry, mock_client)

    mock_hass.data[DOMAIN] = {
        mock_config_entry.entry_id: {"coordinator": coordinator, "client": mock_client}
    }

    entities = []

    def mock_add_entities(new_entities):
        entities.extend(new_entities)

    await async_setup_entry(mock_hass, mock_config_entry, mock_add_entities)
    assert len(entities) == 4

    conv_select = next(e for e in entities if isinstance(e, PaseoConversationModelSelect))
    assert conv_select.current_option == "omniroute/coding-cascade"

    await conv_select.async_select_option("omniroute/fast-cascade")
    call_args = mock_hass.config_entries.async_update_entry.call_args[1]
    assert call_args["options"][CONF_CONVERSATION_MODEL] == "omniroute/fast-cascade"

    ai_select = next(e for e in entities if isinstance(e, PaseoAiTaskModelSelect))
    assert ai_select.current_option == "omniroute/reasoning-latest"

    await ai_select.async_select_option("omniroute/coding-cascade")
    call_args2 = mock_hass.config_entries.async_update_entry.call_args[1]
    assert call_args2["options"][CONF_AI_TASK_MODEL] == "omniroute/coding-cascade"

    voice_select = next(e for e in entities if isinstance(e, PaseoTTSVoiceSelect))
    assert voice_select.current_option == "af_heart"
    await voice_select.async_select_option("am_adam")
    call_args3 = mock_hass.config_entries.async_update_entry.call_args[1]
    assert call_args3["options"][CONF_TTS_VOICE] == "am_adam"

    stt_select = next(e for e in entities if isinstance(e, PaseoSTTModelSelect))
    assert stt_select.current_option == "parakeet-tdt-0.6b-v2-int8"
    await stt_select.async_select_option("whisper-large-v3")
    call_args4 = mock_hass.config_entries.async_update_entry.call_args[1]
    assert call_args4["options"][CONF_STT_MODEL] == "whisper-large-v3"
