"""Tests for Paseo AI Task platform."""

from unittest.mock import AsyncMock

import pytest

from custom_components.paseo.ai_task import (
    PaseoAITaskEntity,
    async_setup_entry,
)
from custom_components.paseo.const import DOMAIN
from custom_components.paseo.coordinator import PaseoDataUpdateCoordinator


@pytest.mark.asyncio
async def test_ai_task_execution(mock_hass, mock_config_entry, mock_client):
    """Test AI Task entity executing autonomous task."""
    coordinator = PaseoDataUpdateCoordinator(mock_hass, mock_config_entry, mock_client)
    coordinator.async_request_refresh = AsyncMock()

    mock_hass.data[DOMAIN] = {
        mock_config_entry.entry_id: {"coordinator": coordinator, "client": mock_client}
    }

    entities = []

    def mock_add_entities(new_entities):
        entities.extend(new_entities)

    await async_setup_entry(mock_hass, mock_config_entry, mock_add_entities)
    assert len(entities) == 1

    ai_task = entities[0]
    assert isinstance(ai_task, PaseoAITaskEntity)
    assert ai_task.state == "idle"

    res = await ai_task.async_execute_task(
        prompt="Fix automations in /config",
        title="Fix Automations",
        workspace="/config",
        role="code",
    )
    assert res["status"] == "created"
    assert ai_task.state == "completed"
    assert ai_task.extra_state_attributes["last_execution"]["status"] == "success"
