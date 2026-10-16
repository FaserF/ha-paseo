"""Tests for Paseo select platform."""

import pytest
from custom_components.paseo.const import (
    CONF_AI_TASK_MODEL,
    CONF_CONVERSATION_MODEL,
    DOMAIN,
)
from custom_components.paseo.coordinator import PaseoDataUpdateCoordinator
from custom_components.paseo.select import (
    PaseoAiTaskModelSelect,
    PaseoConversationModelSelect,
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
    assert len(entities) == 2

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
