"""Tests for the Paseo DataUpdateCoordinator."""

import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.paseo.client import CannotConnect, InvalidAuth
from custom_components.paseo.coordinator import PaseoDataUpdateCoordinator


@pytest.mark.asyncio
async def test_coordinator_update_success(mock_hass, mock_config_entry, mock_client):
    """Test successful coordinator update."""
    coordinator = PaseoDataUpdateCoordinator(mock_hass, mock_config_entry, mock_client)
    data = await coordinator._async_update_data()

    assert data["connected"] is True
    assert data["serverId"] == "srv_test123"
    assert data["hostname"] == "test-paseo"
    assert data["version"] == "0.11.4"
    assert data["tools_count"] == 2
    assert data["agents_count"] == 1


@pytest.mark.asyncio
async def test_coordinator_update_auth_failure(
    mock_hass, mock_config_entry, mock_client
):
    """Test coordinator update with auth failure."""
    mock_client.async_get_status.side_effect = InvalidAuth("bad key")
    coordinator = PaseoDataUpdateCoordinator(mock_hass, mock_config_entry, mock_client)

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()


@pytest.mark.asyncio
async def test_coordinator_update_connect_failure(
    mock_hass, mock_config_entry, mock_client
):
    """Test coordinator update with connection failure."""
    mock_client.async_get_status.side_effect = CannotConnect("down")
    coordinator = PaseoDataUpdateCoordinator(mock_hass, mock_config_entry, mock_client)

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()
