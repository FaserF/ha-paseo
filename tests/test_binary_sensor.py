"""Tests for Paseo binary sensor platform."""

import pytest

from custom_components.paseo.binary_sensor import (
    PaseoBusyBinarySensor,
    PaseoConnectedBinarySensor,
    PaseoEdgeAddonBinarySensor,
    PaseoProblemBinarySensor,
    async_setup_entry,
)
from custom_components.paseo.const import DOMAIN
from custom_components.paseo.coordinator import PaseoDataUpdateCoordinator


@pytest.mark.asyncio
async def test_binary_sensor_setup_and_states(
    mock_hass, mock_config_entry, mock_client
):
    """Test setting up Paseo binary sensors and checking states."""
    coordinator = PaseoDataUpdateCoordinator(mock_hass, mock_config_entry, mock_client)
    await coordinator.async_refresh()

    mock_hass.data[DOMAIN] = {
        mock_config_entry.entry_id: {"coordinator": coordinator, "client": mock_client}
    }

    entities = []

    def mock_add_entities(new_entities):
        entities.extend(new_entities)

    await async_setup_entry(mock_hass, mock_config_entry, mock_add_entities)
    assert len(entities) == 4

    connected = next(e for e in entities if isinstance(e, PaseoConnectedBinarySensor))
    assert connected.is_on is True

    problem = next(e for e in entities if isinstance(e, PaseoProblemBinarySensor))
    assert problem.is_on is False

    busy = next(e for e in entities if isinstance(e, PaseoBusyBinarySensor))
    assert busy.is_on is True

    edge = next(e for e in entities if isinstance(e, PaseoEdgeAddonBinarySensor))
    # Hostname is test-paseo, so edge add-on detection evaluates false
    assert edge.is_on is False
