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
CONF_CONVERSATION_MODEL: Final = "conversation_model"
CONF_PROMPT: Final = "prompt"
CONF_TEMPERATURE: Final = "temperature"
CONF_TOP_P: Final = "top_p"
CONF_MAX_TOKENS: Final = "max_tokens"
CONF_LLM_API: Final = "llm_api"
CONF_AI_TASK_MODEL: Final = "ai_task_model"
CONF_AI_TASK_PROMPT: Final = "ai_task_prompt"
CONF_WORKSPACE: Final = "workspace"
CONF_AUTO_ACCEPT: Final = "auto_accept"
CONF_POLL_INTERVAL: Final = "poll_interval"

# Default values
DEFAULT_NAME: Final = "Paseo"
DEFAULT_URL: Final = "http://127.0.0.1:6767"
DEFAULT_CONVERSATION_MODEL: Final = "omniroute/coding-cascade"
DEFAULT_AI_TASK_MODEL: Final = "omniroute/reasoning-latest"
DEFAULT_FAST_MODEL: Final = "omniroute/fast-cascade"
DEFAULT_WORKSPACE: Final = "/config"
DEFAULT_TEMPERATURE: Final = 0.2
DEFAULT_TOP_P: Final = 0.95
DEFAULT_MAX_TOKENS: Final = 4096
DEFAULT_POLL_INTERVAL: Final = 30
DEFAULT_AUTO_ACCEPT: Final = True

DEFAULT_PROMPT: Final = (
    "You are Paseo, an autonomous AI smart home engineer with direct access to this "
    "Home Assistant installation. You have tools to inspect devices, control entities, "
    "trigger scripts and automations, and diagnose smart home states. "
    "Be direct, precise, reliable, and helpful."
)

DEFAULT_AI_TASK_PROMPT: Final = (
    "You are Paseo's autonomous reasoning engine. Analyze smart home data, audit YAML configurations, "
    "generate blueprint automations, and provide structured, production-ready solutions."
)

AVAILABLE_MODELS: Final = [
    "omniroute/coding-cascade",
    "omniroute/reasoning-latest",
    "omniroute/fast-cascade",
    "omniroute/chat-cascade",
    "omniroute/claude-sonnet-latest",
    "omniroute/claude-opus-latest",
    "omniroute/gemini-flash-latest",
    "omniroute/codestral-latest-catalog",
    "omniroute/nemotron-latest",
    "omniroute/qwen-latest",
    "omniroute/free-fast-latest",
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
    Platform.CONVERSATION,
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
