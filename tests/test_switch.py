"""Tests for Paseo switch platform."""

import pytest
from custom_components.paseo.const import CONF_AUTO_ACCEPT, DOMAIN
from custom_components.paseo.coordinator import PaseoDataUpdateCoordinator
from custom_components.paseo.switch import (
    PaseoAutonomousExecutionSwitch,
    async_setup_entry,
)


@pytest.mark.asyncio
async def test_switch_toggle_actions(mock_hass, mock_config_entry, mock_client):
    """Test switch turn on / turn off toggles auto_accept option."""
    coordinator = PaseoDataUpdateCoordinator(mock_hass, mock_config_entry, mock_client)

    mock_hass.data[DOMAIN] = {
        mock_config_entry.entry_id: {"coordinator": coordinator, "client": mock_client}
    }

    entities = []

    def mock_add_entities(new_entities):
        entities.extend(new_entities)

    await async_setup_entry(mock_hass, mock_config_entry, mock_add_entities)
    assert len(entities) == 1

    switch = entities[0]
    assert isinstance(switch, PaseoAutonomousExecutionSwitch)
    assert switch.is_on is True

    await switch.async_turn_off()
    assert mock_hass.config_entries.async_update_entry.call_count == 1
    call_args = mock_hass.config_entries.async_update_entry.call_args[1]
    assert call_args["options"][CONF_AUTO_ACCEPT] is False

    await switch.async_turn_on()
    call_args2 = mock_hass.config_entries.async_update_entry.call_args[1]
    assert call_args2["options"][CONF_AUTO_ACCEPT] is True
