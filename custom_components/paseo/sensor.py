"""Support for Paseo sensors."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_WORKSPACE, DEFAULT_WORKSPACE, DOMAIN
from .coordinator import PaseoDataUpdateCoordinator
from .helpers import get_device_info


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Paseo sensors based on a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: PaseoDataUpdateCoordinator = data["coordinator"]

    async_add_entities(
        [
            PaseoStatusSensor(coordinator, entry),
            PaseoLatencySensor(coordinator, entry),
            PaseoVersionSensor(coordinator, entry),
            PaseoHostnameSensor(coordinator, entry),
            PaseoActiveAgentsSensor(coordinator, entry),
            PaseoToolsCountSensor(coordinator, entry),
            PaseoWorkspaceSensor(coordinator, entry),
        ]
    )


class PaseoBaseSensor(CoordinatorEntity[PaseoDataUpdateCoordinator], SensorEntity):
    """Base class for Paseo sensors."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: PaseoDataUpdateCoordinator,
        entry: ConfigEntry,
        key: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entry = entry
        self._key = key
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        sw_version = coordinator.data.get("version") if coordinator.data else None
        self._attr_device_info = get_device_info(entry, sw_version)


class PaseoStatusSensor(PaseoBaseSensor):
    """Sensor reporting the operational status of the Paseo daemon."""

    _attr_translation_key = "status"
    _attr_name = "Status"
    _attr_icon = "mdi:server-network"

    def __init__(
        self, coordinator: PaseoDataUpdateCoordinator, entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator, entry, "status")

    @property
    def native_value(self) -> str:
        """Return daemon operational state."""
        if not self.coordinator.data or not self.coordinator.data.get("connected"):
            return "offline"
        return str(self.coordinator.data.get("status", "operational"))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return server connection and capability attributes."""
        if not self.coordinator.data:
            return {}
        return {
            "serverId": self.coordinator.data.get("serverId"),
            "listen": self.coordinator.data.get("listen"),
            "hostname": self.coordinator.data.get("hostname"),
            "tools_count": self.coordinator.data.get("tools_count", 0),
            "agents_count": self.coordinator.data.get("agents_count", 0),
        }


class PaseoLatencySensor(PaseoBaseSensor):
    """Sensor reporting the API ping latency in milliseconds."""

    _attr_translation_key = "latency"
    _attr_name = "Latency"
    _attr_icon = "mdi:speedometer"
    _attr_native_unit_of_measurement = UnitOfTime.MILLISECONDS
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_device_class = SensorDeviceClass.DURATION

    def __init__(
        self, coordinator: PaseoDataUpdateCoordinator, entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator, entry, "latency")

    @property
    def native_value(self) -> float | None:
        """Return gateway latency."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("latency_ms")


class PaseoVersionSensor(PaseoBaseSensor):
    """Sensor reporting the software version of the Paseo daemon."""

    _attr_translation_key = "version"
    _attr_name = "Version"
    _attr_icon = "mdi:tag-text"

    def __init__(
        self, coordinator: PaseoDataUpdateCoordinator, entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator, entry, "version")

    @property
    def native_value(self) -> str | None:
        """Return daemon software version."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("version")


class PaseoHostnameSensor(PaseoBaseSensor):
    """Sensor reporting the host name of the Paseo worker node."""

    _attr_translation_key = "hostname"
    _attr_name = "Hostname"
    _attr_icon = "mdi:domain"

    def __init__(
        self, coordinator: PaseoDataUpdateCoordinator, entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator, entry, "hostname")

    @property
    def native_value(self) -> str | None:
        """Return node hostname."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("hostname")


class PaseoActiveAgentsSensor(PaseoBaseSensor):
    """Sensor reporting the number of currently active autonomous agents."""

    _attr_translation_key = "active_agents"
    _attr_name = "Active Agents"
    _attr_icon = "mdi:robot"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self, coordinator: PaseoDataUpdateCoordinator, entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator, entry, "active_agents")

    @property
    def native_value(self) -> int:
        """Return active agents count."""
        if not self.coordinator.data:
            return 0
        return int(self.coordinator.data.get("agents_count", 0))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return details of active agents."""
        if not self.coordinator.data:
            return {}
        return {"agents": self.coordinator.data.get("agents", [])}


class PaseoToolsCountSensor(PaseoBaseSensor):
    """Sensor reporting the number of registered MCP tools."""

    _attr_translation_key = "tools_count"
    _attr_name = "Available MCP Tools"
    _attr_icon = "mdi:tools"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self, coordinator: PaseoDataUpdateCoordinator, entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator, entry, "tools_count")

    @property
    def native_value(self) -> int:
        """Return total registered MCP tools."""
        if not self.coordinator.data:
            return 0
        return int(self.coordinator.data.get("tools_count", 0))


class PaseoWorkspaceSensor(PaseoBaseSensor):
    """Sensor reporting the active workspace directory."""

    _attr_translation_key = "workspace"
    _attr_name = "Workspace"
    _attr_icon = "mdi:folder-code"

    def __init__(
        self, coordinator: PaseoDataUpdateCoordinator, entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator, entry, "workspace")

    @property
    def native_value(self) -> str:
        """Return configured workspace path."""
        return str(self.entry.options.get(CONF_WORKSPACE, DEFAULT_WORKSPACE))
