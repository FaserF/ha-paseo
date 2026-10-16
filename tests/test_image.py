"""Tests for Paseo Image platform."""

import pytest
from custom_components.paseo.const import DOMAIN
from custom_components.paseo.coordinator import PaseoDataUpdateCoordinator
from custom_components.paseo.image import PaseoLatestGeneratedImage, async_setup_entry


@pytest.mark.asyncio
async def test_image_setup_and_state(mock_hass, mock_config_entry, mock_client):
    """Test Image entity setup and updating image bytes."""
    coordinator = PaseoDataUpdateCoordinator(mock_hass, mock_config_entry, mock_client)
    await coordinator.async_refresh()

    mock_hass.data[DOMAIN] = {
        mock_config_entry.entry_id: {"coordinator": coordinator, "client": mock_client}
    }

    entities = []

    def mock_add_entities(new_entities):
        entities.extend(new_entities)

    await async_setup_entry(mock_hass, mock_config_entry, mock_add_entities)
    assert len(entities) == 1

    img_entity = entities[0]
    assert isinstance(img_entity, PaseoLatestGeneratedImage)
    assert await img_entity.async_image() is None
    assert img_entity.image_last_updated is None

    test_bytes = b"fake-png-data"
    img_entity.set_image(test_bytes)

    assert await img_entity.async_image() == test_bytes
    assert img_entity.image_last_updated is not None
