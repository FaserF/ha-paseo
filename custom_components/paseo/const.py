"""Constants for the Paseo integration."""

from __future__ import annotations

from typing import Final

from homeassistant.const import Platform

DOMAIN: Final = "paseo"
MANUFACTURER: Final = "Paseo AI"
INTEGRATION_NAME: Final = "Paseo"

# Configuration Options
CONF_URL: Final = "url"
CONF_API_KEY: Final = "api_key"
CONF_NAME: Final = "name"
CONF_LLM_API: Final = "llm_api"
CONF_AI_TASK_MODEL: Final = "ai_task_model"
CONF_AI_TASK_PROMPT: Final = "ai_task_prompt"
CONF_WORKSPACE: Final = "workspace"
CONF_AUTO_ACCEPT: Final = "auto_accept"
CONF_POLL_INTERVAL: Final = "poll_interval"

# Default values
DEFAULT_NAME: Final = "Paseo"
DEFAULT_URL: Final = "http://127.0.0.1:6767"
DEFAULT_AI_TASK_MODEL: Final = "default"
DEFAULT_FAST_MODEL: Final = "default"
DEFAULT_WORKSPACE: Final = "/config"
DEFAULT_POLL_INTERVAL: Final = 30
DEFAULT_AUTO_ACCEPT: Final = True

DEFAULT_AI_TASK_PROMPT: Final = (
    "You are Paseo's autonomous reasoning engine. Analyze smart home data, audit YAML configurations, "
    "generate blueprint automations, and provide structured, production-ready solutions."
)

AVAILABLE_MODELS: Final[list[str]] = [
    "default",
]

AVAILABLE_MODES: Final = [
    "build",
    "plan",
    "code",
    "ask",
]

# Supported platforms
PLATFORMS: Final = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.SWITCH,
    Platform.SELECT,
    getattr(Platform, "AI_TASK", "ai_task"),
]

# Service definitions
SERVICE_CREATE_AGENT: Final = "create_agent"
SERVICE_SEND_PROMPT: Final = "send_prompt"
SERVICE_STOP_AGENT: Final = "stop_agent"
SERVICE_EXECUTE_TASK: Final = "execute_task"
SERVICE_VALIDATE_CONFIG: Final = "validate_config"
SERVICE_REFRESH_STATUS: Final = "refresh_status"

# Data dict keys
DATA_COORDINATOR: Final = "coordinator"
DATA_CLIENT: Final = "client"

# Ingress / HA Add-on slug
PASEO_ADDON_SLUG: Final = "edfe50eb_paseo"
