"""Tests for Paseo button platform."""

from unittest.mock import AsyncMock
import pytest
from custom_components.paseo.button import (
    PaseoRefreshButton,
    PaseoValidateConfigButton,
    async_setup_entry,
)
from custom_components.paseo.const import DOMAIN
from custom_components.paseo.coordinator import PaseoDataUpdateCoordinator


@pytest.mark.asyncio
async def test_button_press_actions(mock_hass, mock_config_entry, mock_client):
    """Test button entities and async_press."""
    coordinator = PaseoDataUpdateCoordinator(mock_hass, mock_config_entry, mock_client)
    coordinator.async_request_refresh = AsyncMock()

    mock_hass.data[DOMAIN] = {
        mock_config_entry.entry_id: {"coordinator": coordinator, "client": mock_client}
    }

    entities = []

    def mock_add_entities(new_entities):
        entities.extend(new_entities)

    await async_setup_entry(mock_hass, mock_config_entry, mock_add_entities)
    assert len(entities) == 2

    refresh_btn = next(e for e in entities if isinstance(e, PaseoRefreshButton))
    await refresh_btn.async_press()
    coordinator.async_request_refresh.assert_awaited_once()

    validate_btn = next(e for e in entities if isinstance(e, PaseoValidateConfigButton))
    await validate_btn.async_press()
    mock_hass.services.async_call.assert_awaited_with("homeassistant", "check_config")
