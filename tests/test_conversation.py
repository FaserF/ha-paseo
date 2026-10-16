"""Tests for Paseo conversation entity."""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from homeassistant.components.conversation import ConversationInput
from custom_components.paseo.const import DOMAIN
from custom_components.paseo.conversation import (
    PaseoConversationEntity,
    async_setup_entry,
)
from custom_components.paseo.coordinator import PaseoDataUpdateCoordinator


@pytest.mark.asyncio
async def test_conversation_entity_process(mock_hass, mock_config_entry, mock_client):
    """Test conversation entity processing user input."""
    coordinator = PaseoDataUpdateCoordinator(mock_hass, mock_config_entry, mock_client)

    mock_hass.data[DOMAIN] = {
        mock_config_entry.entry_id: {"coordinator": coordinator, "client": mock_client}
    }

    entities = []

    def mock_add_entities(new_entities):
        entities.extend(new_entities)

    await async_setup_entry(mock_hass, mock_config_entry, mock_add_entities)
    assert len(entities) == 1

    conv_entity = entities[0]
    assert isinstance(conv_entity, PaseoConversationEntity)
    assert conv_entity.supported_languages == ["*"]

    user_input = ConversationInput(
        text="Turn on living room light",
        context=MagicMock(),
        conversation_id="conv_123",
        device_id=None,
        language="en",
        agent_id="test_agent",
    )

    with patch("homeassistant.helpers.llm.async_get_api", new=AsyncMock(return_value=None)):
        result = await conv_entity.async_process(user_input)
        assert result.response.speech["plain"]["speech"] == "Paseo response text"
        assert result.conversation_id == "conv_123"
