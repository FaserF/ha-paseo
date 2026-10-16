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

# Speech and Vision Options
CONF_STT_MODEL: Final = "stt_model"
CONF_STT_LANGUAGE: Final = "stt_language"
CONF_TTS_MODEL: Final = "tts_model"
CONF_TTS_VOICE: Final = "tts_voice"
CONF_TTS_SPEED: Final = "tts_speed"
CONF_TTS_FORMAT: Final = "tts_format"
CONF_IMAGE_MODEL: Final = "image_model"
CONF_IMAGE_SIZE: Final = "image_size"

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

DEFAULT_STT_MODEL: Final = "parakeet-tdt-0.6b-v2-int8"
DEFAULT_STT_LANGUAGE: Final = "en"
DEFAULT_TTS_MODEL: Final = "kokoro-en-v0_19"
DEFAULT_TTS_VOICE: Final = "af_heart"
DEFAULT_TTS_SPEED: Final = 1.0
DEFAULT_TTS_FORMAT: Final = "mp3"
DEFAULT_IMAGE_MODEL: Final = "omniroute/flux-schnell"
DEFAULT_IMAGE_SIZE: Final = "1024x1024"

SUPPORTED_TTS_FORMATS: Final = ["mp3", "wav", "opus"]
AVAILABLE_TTS_VOICES: Final = [
    "af_heart",
    "af_bella",
    "am_adam",
    "am_michael",
    "bf_emma",
    "bm_george",
]
AVAILABLE_STT_MODELS: Final = [
    "parakeet-tdt-0.6b-v2-int8",
    "whisper-large-v3",
    "whisper-medium",
    "whisper-small",
]
AVAILABLE_TTS_MODELS: Final = [
    "kokoro-en-v0_19",
    "tts-1",
    "tts-1-hd",
    "sherpa-onnx-tts",
]

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
    Platform.STT,
    Platform.TTS,
    Platform.IMAGE,
    getattr(Platform, "AI_TASK", "ai_task"),
]

# Service definitions
SERVICE_CREATE_AGENT: Final = "create_agent"
SERVICE_SEND_PROMPT: Final = "send_prompt"
SERVICE_STOP_AGENT: Final = "stop_agent"
SERVICE_EXECUTE_TASK: Final = "execute_task"
SERVICE_VALIDATE_CONFIG: Final = "validate_config"
SERVICE_REFRESH_STATUS: Final = "refresh_status"
SERVICE_GENERATE_IMAGE: Final = "generate_image"
SERVICE_TRANSCRIBE_AUDIO: Final = "transcribe_audio"
SERVICE_SYNTHESIZE_SPEECH: Final = "synthesize_speech"

# Data dict keys
DATA_COORDINATOR: Final = "coordinator"
DATA_CLIENT: Final = "client"
DATA_IMAGE_ENTITY: Final = "latest_image_entity"

# Ingress / HA Add-on slug
PASEO_ADDON_SLUG: Final = "edfe50eb_paseo"
