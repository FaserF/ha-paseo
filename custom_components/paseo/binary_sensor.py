"""Support for Paseo binary sensors."""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import PaseoDataUpdateCoordinator
from .helpers import get_device_info


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Paseo binary sensors based on a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: PaseoDataUpdateCoordinator = data["coordinator"]

    async_add_entities(
        [
            PaseoConnectedBinarySensor(coordinator, entry),
            PaseoProblemBinarySensor(coordinator, entry),
            PaseoBusyBinarySensor(coordinator, entry),
            PaseoEdgeAddonBinarySensor(coordinator, entry),
        ]
    )


class PaseoBaseBinarySensor(
    CoordinatorEntity[PaseoDataUpdateCoordinator], BinarySensorEntity
):
    """Base class for Paseo binary sensors."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: PaseoDataUpdateCoordinator,
        entry: ConfigEntry,
        key: str,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.entry = entry
        self._key = key
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        sw_version = coordinator.data.get("version") if coordinator.data else None
        self._attr_device_info = get_device_info(entry, sw_version)


class PaseoConnectedBinarySensor(PaseoBaseBinarySensor):
    """Binary sensor indicating connection status."""

    _attr_translation_key = "connected"
    _attr_name = "Connected"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(
        self, coordinator: PaseoDataUpdateCoordinator, entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator, entry, "connected")

    @property
    def is_on(self) -> bool:
        """Return true if connected."""
        if not self.coordinator.data:
            return False
        return bool(self.coordinator.data.get("connected", False))


class PaseoProblemBinarySensor(PaseoBaseBinarySensor):
    """Binary sensor indicating connection or daemon failure."""

    _attr_translation_key = "problem"
    _attr_name = "Problem"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(
        self, coordinator: PaseoDataUpdateCoordinator, entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator, entry, "problem")

    @property
    def is_on(self) -> bool:
        """Return true if there is a problem."""
        if not self.coordinator.data:
            return True
        return not bool(self.coordinator.data.get("connected", False))


class PaseoBusyBinarySensor(PaseoBaseBinarySensor):
    """Binary sensor indicating active autonomous agent work."""

    _attr_translation_key = "busy"
    _attr_name = "Busy"
    _attr_device_class = BinarySensorDeviceClass.RUNNING
    _attr_icon = "mdi:progress-wrench"

    def __init__(
        self, coordinator: PaseoDataUpdateCoordinator, entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator, entry, "busy")

    @property
    def is_on(self) -> bool:
        """Return true if agents are actively running."""
        if not self.coordinator.data:
            return False
        return int(self.coordinator.data.get("agents_count", 0)) > 0


class PaseoEdgeAddonBinarySensor(PaseoBaseBinarySensor):
    """Binary sensor indicating whether this node is the local Home Assistant Edge Addon."""

    _attr_translation_key = "edge_addon"
    _attr_name = "Edge Add-on Host"
    _attr_icon = "mdi:home-assistant"

    def __init__(
        self, coordinator: PaseoDataUpdateCoordinator, entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator, entry, "edge_addon")

    @property
    def is_on(self) -> bool:
        """Return true if this instance is running locally as the Home Assistant add-on."""
        if not self.coordinator.data:
            return False
        hostname = str(self.coordinator.data.get("hostname", ""))
        return "edfe50eb-paseo" in hostname or "hassio" in hostname.lower()
