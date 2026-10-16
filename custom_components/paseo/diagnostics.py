"""Diagnostics support for Paseo."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import PaseoDataUpdateCoordinator
from .helpers import redact_sensitive


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: PaseoDataUpdateCoordinator = data["coordinator"]

    return {
        "entry": {
            "entry_id": entry.entry_id,
            "version": entry.version,
            "domain": entry.domain,
            "title": entry.title,
            "data": redact_sensitive(dict(entry.data)),
            "options": redact_sensitive(dict(entry.options)),
        },
        "coordinator_data": redact_sensitive(dict(coordinator.data or {})),
    }
