"""Tests for Paseo sensor platform."""

import pytest
from custom_components.paseo.const import DOMAIN
from custom_components.paseo.coordinator import PaseoDataUpdateCoordinator
from custom_components.paseo.sensor import (
    PaseoActiveAgentsSensor,
    PaseoHostnameSensor,
    PaseoLatencySensor,
    PaseoStatusSensor,
    PaseoToolsCountSensor,
    PaseoVersionSensor,
    PaseoWorkspaceSensor,
    async_setup_entry,
)


@pytest.mark.asyncio
async def test_sensor_setup_and_properties(mock_hass, mock_config_entry, mock_client):
    """Test setting up Paseo sensors and reading properties."""
    coordinator = PaseoDataUpdateCoordinator(mock_hass, mock_config_entry, mock_client)
    await coordinator.async_refresh()

    mock_hass.data[DOMAIN] = {
        mock_config_entry.entry_id: {"coordinator": coordinator, "client": mock_client}
    }

    entities = []

    def mock_add_entities(new_entities):
        entities.extend(new_entities)

    await async_setup_entry(mock_hass, mock_config_entry, mock_add_entities)
    assert len(entities) == 7

    status_sensor = next(e for e in entities if isinstance(e, PaseoStatusSensor))
    assert status_sensor.native_value == "server_info"
    assert status_sensor.extra_state_attributes["serverId"] == "srv_test123"

    latency_sensor = next(e for e in entities if isinstance(e, PaseoLatencySensor))
    assert latency_sensor.native_value == 5.4

    version_sensor = next(e for e in entities if isinstance(e, PaseoVersionSensor))
    assert version_sensor.native_value == "0.11.4"

    hostname_sensor = next(e for e in entities if isinstance(e, PaseoHostnameSensor))
    assert hostname_sensor.native_value == "test-paseo"

    active_agents = next(e for e in entities if isinstance(e, PaseoActiveAgentsSensor))
    assert active_agents.native_value == 1

    tools_count = next(e for e in entities if isinstance(e, PaseoToolsCountSensor))
    assert tools_count.native_value == 2

    workspace_sensor = next(e for e in entities if isinstance(e, PaseoWorkspaceSensor))
    assert workspace_sensor.native_value == "/config"
