"""Tests for Paseo diagnostics."""

import pytest

from custom_components.paseo.const import DOMAIN
from custom_components.paseo.coordinator import PaseoDataUpdateCoordinator
from custom_components.paseo.diagnostics import async_get_config_entry_diagnostics


@pytest.mark.asyncio
async def test_diagnostics_redaction(mock_hass, mock_config_entry, mock_client):
    """Test diagnostics export redacts sensitive keys."""
    coordinator = PaseoDataUpdateCoordinator(mock_hass, mock_config_entry, mock_client)
    await coordinator.async_refresh()

    mock_hass.data[DOMAIN] = {
        mock_config_entry.entry_id: {"coordinator": coordinator, "client": mock_client}
    }

    diag = await async_get_config_entry_diagnostics(mock_hass, mock_config_entry)

    assert diag["entry"]["entry_id"] == mock_config_entry.entry_id
    assert diag["entry"]["data"]["api_key"] == "**REDACTED**"
    assert diag["coordinator_data"]["serverId"] == "srv_test123"
