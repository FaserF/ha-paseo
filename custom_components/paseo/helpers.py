"""Helpers for the Paseo integration."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo

from .const import CONF_NAME, CONF_URL, DEFAULT_NAME, DOMAIN, MANUFACTURER


def get_device_info(entry: ConfigEntry, sw_version: str | None = None) -> DeviceInfo:
    """Return standardized DeviceInfo for a Paseo instance."""
    name = entry.data.get(CONF_NAME, entry.title or DEFAULT_NAME)
    url = entry.data.get(CONF_URL, "")

    info = DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=name,
        manufacturer=MANUFACTURER,
        model="Paseo AI Code Studio",
        configuration_url=url,
        entry_type=DeviceEntryType.SERVICE,
    )
    if sw_version:
        info["sw_version"] = sw_version
    return info


def redact_sensitive(data: dict[str, Any]) -> dict[str, Any]:
    """Redact sensitive keys like tokens, passwords, and API keys."""
    redacted = {}
    sensitive_keys = {
        "api_key",
        "password",
        "token",
        "secret",
        "authorization",
        "cookie",
        "access_token",
        "refresh_token",
    }
    for k, v in data.items():
        if isinstance(v, dict):
            redacted[k] = redact_sensitive(v)
        elif any(s in k.lower() for s in sensitive_keys) and v:
            redacted[k] = "**REDACTED**"
        else:
            redacted[k] = v
    return redacted
