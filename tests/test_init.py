"""Tests for Paseo integration setup and teardown."""

from unittest.mock import AsyncMock, patch

import pytest

from custom_components.paseo import (
    async_reload_entry,
    async_setup,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.paseo.const import DOMAIN


@pytest.mark.asyncio
async def test_async_setup(mock_hass):
    """Test general async_setup."""
    result = await async_setup(mock_hass, {})
    assert result is True
    assert mock_hass.services.async_register.call_count >= 5


@pytest.mark.asyncio
async def test_async_setup_entry(mock_hass, mock_config_entry, mock_client):
    """Test async_setup_entry."""
    mock_hass.data = {}
    with (
        patch("custom_components.paseo.PaseoClient", return_value=mock_client),
        patch(
            "custom_components.paseo.PaseoDataUpdateCoordinator.async_config_entry_first_refresh",
            new=AsyncMock(),
        ),
    ):
        result = await async_setup_entry(mock_hass, mock_config_entry)
        assert result is True
        assert DOMAIN in mock_hass.data
        assert mock_config_entry.entry_id in mock_hass.data[DOMAIN]
        assert "client" in mock_hass.data[DOMAIN][mock_config_entry.entry_id]
        assert "coordinator" in mock_hass.data[DOMAIN][mock_config_entry.entry_id]
        mock_hass.config_entries.async_forward_entry_setups.assert_awaited_once()


@pytest.mark.asyncio
async def test_async_unload_entry(mock_hass, mock_config_entry, mock_client):
    """Test async_unload_entry."""
    coordinator = AsyncMock()
    mock_hass.data = {
        DOMAIN: {
            mock_config_entry.entry_id: {
                "client": mock_client,
                "coordinator": coordinator,
            }
        }
    }
    result = await async_unload_entry(mock_hass, mock_config_entry)
    assert result is True
    assert mock_config_entry.entry_id not in mock_hass.data[DOMAIN]
    mock_client.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_async_reload_entry(mock_hass, mock_config_entry):
    """Test async_reload_entry."""
    await async_reload_entry(mock_hass, mock_config_entry)
    mock_hass.config_entries.async_reload.assert_awaited_once_with(
        mock_config_entry.entry_id
    )
