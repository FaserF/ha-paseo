"""Image platform for Paseo integration."""

from __future__ import annotations

from datetime import UTC, datetime
import logging

from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DATA_COORDINATOR, DATA_IMAGE_ENTITY, DOMAIN
from .coordinator import PaseoDataUpdateCoordinator
from .helpers import get_device_info

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Paseo image entities from config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: PaseoDataUpdateCoordinator = data[DATA_COORDINATOR]

    entity = PaseoLatestGeneratedImage(hass, coordinator, entry)
    data[DATA_IMAGE_ENTITY] = entity
    async_add_entities([entity])


class PaseoLatestGeneratedImage(
    CoordinatorEntity[PaseoDataUpdateCoordinator], ImageEntity
):
    """Image entity showing the most recently generated AI image or diagram."""

    _attr_has_entity_name = True
    _attr_name = "Latest Generated Image"
    _attr_icon = "mdi:image-filter-hdr"

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: PaseoDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize latest generated image entity."""
        CoordinatorEntity.__init__(self, coordinator)
        ImageEntity.__init__(self, hass)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_latest_generated_image"
        sw_version = coordinator.data.get("version") if coordinator.data else None
        self._attr_device_info = get_device_info(entry, sw_version)
        self._image_bytes: bytes | None = None
        self._image_last_updated: datetime | None = None

    @property
    def image_last_updated(self) -> datetime | None:
        """Return the date and time the image was last updated."""
        return self._image_last_updated

    async def async_image(self) -> bytes | None:
        """Return bytes of the current image."""
        return self._image_bytes

    def set_image(self, image_bytes: bytes) -> None:
        """Set new image bytes and update timestamp."""
        self._image_bytes = image_bytes
        self._image_last_updated = datetime.now(UTC)
        self.async_write_ha_state()
