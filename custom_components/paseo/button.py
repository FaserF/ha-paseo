"""Support for Paseo action buttons."""

from __future__ import annotations

import logging
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .client import PaseoClient
from .const import DOMAIN
from .coordinator import PaseoDataUpdateCoordinator
from .helpers import get_device_info

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Paseo buttons based on a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: PaseoDataUpdateCoordinator = data["coordinator"]
    client: PaseoClient = data["client"]

    async_add_entities(
        [
            PaseoRefreshButton(coordinator, entry),
            PaseoValidateConfigButton(coordinator, client, entry),
        ]
    )


class PaseoRefreshButton(
    CoordinatorEntity[PaseoDataUpdateCoordinator], ButtonEntity
):
    """Button to force refresh telemetry from Paseo."""

    _attr_has_entity_name = True
    _attr_translation_key = "refresh"
    _attr_name = "Refresh Telemetry"
    _attr_icon = "mdi:refresh"

    def __init__(
        self, coordinator: PaseoDataUpdateCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_refresh"
        sw_version = coordinator.data.get("version") if coordinator.data else None
        self._attr_device_info = get_device_info(entry, sw_version)

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.async_request_refresh()


class PaseoValidateConfigButton(
    CoordinatorEntity[PaseoDataUpdateCoordinator], ButtonEntity
):
    """Button to execute a configuration validation check via Paseo."""

    _attr_has_entity_name = True
    _attr_translation_key = "validate_config"
    _attr_name = "Validate Home Configuration"
    _attr_icon = "mdi:check-decagram"

    def __init__(
        self,
        coordinator: PaseoDataUpdateCoordinator,
        client: PaseoClient,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self.entry = entry
        self.client = client
        self._attr_unique_id = f"{entry.entry_id}_validate_config"
        sw_version = coordinator.data.get("version") if coordinator.data else None
        self._attr_device_info = get_device_info(entry, sw_version)

    async def async_press(self) -> None:
        """Handle the button press to validate configuration."""
        _LOGGER.info("Initiating Home Assistant configuration validation via Paseo")
        try:
            # First trigger Home Assistant's native check config service
            await self.hass.services.async_call("homeassistant", "check_config")
            _LOGGER.info("Home Assistant configuration check triggered successfully")
        except Exception as exc:  # noqa: BLE001
            _LOGGER.warning("Could not trigger native check_config: %s", exc)

        await self.coordinator.async_request_refresh()
