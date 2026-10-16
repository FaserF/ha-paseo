"""Pytest configuration and fixtures for the Paseo integration tests."""

import sys
import types
from dataclasses import dataclass
from typing import Any
from unittest.mock import AsyncMock, MagicMock

# Ensure Unix-specific modules are mocked on Windows
if sys.platform == "win32":
    if "fcntl" not in sys.modules:
        fcntl_mock = types.ModuleType("fcntl")
        fcntl_mock.LOCK_EX = 2
        fcntl_mock.LOCK_NB = 4
        fcntl_mock.LOCK_SH = 1
        fcntl_mock.LOCK_UN = 8
        fcntl_mock.flock = MagicMock()
        sys.modules["fcntl"] = fcntl_mock

    if "resource" not in sys.modules:
        resource_mock = types.ModuleType("resource")
        resource_mock.RLIMIT_NOFILE = 7
        resource_mock.getrlimit = MagicMock(return_value=(1024, 2048))
        resource_mock.setrlimit = MagicMock()
        sys.modules["resource"] = resource_mock

if "voluptuous" not in sys.modules:
    vol_mock = MagicMock()
    vol_mock.Schema = lambda schema, *args, **kwargs: schema
    vol_mock.Required = lambda key, *args, **kwargs: key
    vol_mock.Optional = lambda key, *args, **kwargs: key
    vol_mock.Coerce = lambda typ: typ
    vol_mock.In = lambda items: items
    vol_mock.Range = lambda *args, **kwargs: lambda val: val
    vol_mock.All = lambda *args: lambda val: val
    sys.modules["voluptuous"] = vol_mock

import pytest


def mock_submodule(name: str) -> None:
    """Recursively mock submodules to ensure they are available in sys.modules."""
    parts = name.split(".")
    for i in range(1, len(parts) + 1):
        full_name = ".".join(parts[:i])
        if full_name not in sys.modules:
            mock = MagicMock()
            sys.modules[full_name] = mock
            if i > 1:
                parent_name = ".".join(parts[: i - 1])
                setattr(sys.modules[parent_name], parts[i - 1], mock)


@dataclass(frozen=True, kw_only=True)
class MockEntityDescription:
    """Base class for mocked entity descriptions."""

    key: str
    name: str | None = None
    icon: str | None = None
    entity_registry_enabled_default: bool = True
    entity_category: Any = None
    translation_key: str | None = None
    has_entity_name: bool = False
    device_class: Any = None
    native_unit_of_measurement: str | None = None
    state_class: Any = None
    options: list[str] | None = None


class MockEntity:
    """Base class for mocked Home Assistant entities."""

    _attr_has_entity_name: bool = False
    _attr_name: str | None = None
    _attr_unique_id: str | None = None
    _attr_device_info: dict[str, Any] | None = None
    _attr_extra_state_attributes: dict[str, Any] | None = None
    _attr_icon: str | None = None
    entity_description: Any = None
    hass: Any = None

    @property
    def name(self) -> str | None:
        if self._attr_name is not None:
            return self._attr_name
        if hasattr(self, "entity_description") and self.entity_description:
            return getattr(self.entity_description, "name", None)
        return None

    @property
    def unique_id(self) -> str | None:
        return self._attr_unique_id

    @property
    def device_info(self) -> dict[str, Any] | None:
        return self._attr_device_info

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        return self._attr_extra_state_attributes

    def async_write_ha_state(self) -> None:
        pass


class MockCoordinatorEntity(MockEntity):
    """Base class for coordinator entities."""

    @classmethod
    def __class_getitem__(cls, _):
        return cls

    def __init__(self, coordinator: Any) -> None:
        self.coordinator = coordinator
        self.hass = getattr(coordinator, "hass", None)

    @property
    def available(self) -> bool:
        if self.coordinator and hasattr(self.coordinator, "last_update_success"):
            return self.coordinator.last_update_success
        return True


class MockDataUpdateCoordinator:
    """Mock DataUpdateCoordinator."""

    @classmethod
    def __class_getitem__(cls, _):
        return cls

    def __init__(
        self,
        hass: Any,
        logger: Any,
        *,
        name: str,
        update_interval: Any = None,
        update_method: Any = None,
    ) -> None:
        self.hass = hass
        self.logger = logger
        self.name = name
        self.update_interval = update_interval
        self.update_method = update_method
        self.data: Any = None
        self.last_update_success = True
        self._listeners: list[Any] = []

    def async_add_listener(self, update_callback: Any, context: Any = None) -> Any:
        self._listeners.append(update_callback)
        return lambda: self._listeners.remove(update_callback)

    async def async_refresh(self) -> None:
        if hasattr(self, "_async_update_data"):
            self.data = await self._async_update_data()

    async def async_config_entry_first_refresh(self) -> None:
        await self.async_refresh()


class MockConfigFlow:
    """Mock ConfigFlow."""

    def __init_subclass__(cls, domain: str | None = None, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        cls._domain = domain

    def __init__(self) -> None:
        self.hass: Any = None
        self._unique_id: str | None = None

    async def async_set_unique_id(self, unique_id: str) -> None:
        self._unique_id = unique_id

    def _abort_if_unique_id_configured(self) -> None:
        pass

    def async_show_form(
        self,
        *,
        step_id: str,
        data_schema: Any = None,
        errors: dict[str, str] | None = None,
        description_placeholders: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        return {
            "type": "form",
            "step_id": step_id,
            "data_schema": data_schema,
            "errors": errors or {},
            "description_placeholders": description_placeholders or {},
        }

    def async_create_entry(
        self,
        *,
        title: str,
        data: dict[str, Any],
        options: dict[str, Any] | None = None,
        description: str | None = None,
        description_placeholders: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        return {
            "type": "create_entry",
            "title": title,
            "data": data,
            "options": options or {},
            "description": description,
            "description_placeholders": description_placeholders,
        }

    def async_abort(self, *, reason: str) -> dict[str, Any]:
        return {"type": "abort", "reason": reason}


class MockOptionsFlow:
    """Mock OptionsFlow."""

    def __init__(self, config_entry: Any = None) -> None:
        self.config_entry = config_entry
        self.hass: Any = None

    def async_show_form(
        self,
        *,
        step_id: str,
        data_schema: Any = None,
        errors: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        return {
            "type": "form",
            "step_id": step_id,
            "data_schema": data_schema,
            "errors": errors or {},
        }

    def async_create_entry(
        self, *, title: str = "", data: dict[str, Any]
    ) -> dict[str, Any]:
        return {"type": "create_entry", "title": title, "data": data}


# Setup homeassistant mock structure
mock_submodule("homeassistant.const")
mock_submodule("homeassistant.core")
mock_submodule("homeassistant.exceptions")
mock_submodule("homeassistant.data_entry_flow")
mock_submodule("homeassistant.config_entries")
mock_submodule("homeassistant.helpers.update_coordinator")
mock_submodule("homeassistant.helpers.entity")
mock_submodule("homeassistant.helpers.entity_platform")
mock_submodule("homeassistant.helpers.aiohttp_client")
mock_submodule("homeassistant.helpers.config_validation")
mock_submodule("homeassistant.helpers.template")
mock_submodule("homeassistant.helpers.selector")
mock_submodule("homeassistant.helpers.llm")
mock_submodule("homeassistant.components.sensor")
mock_submodule("homeassistant.components.binary_sensor")
mock_submodule("homeassistant.components.button")
mock_submodule("homeassistant.components.select")
mock_submodule("homeassistant.components.switch")
mock_submodule("homeassistant.components.diagnostics")
mock_submodule("homeassistant.components.conversation")
mock_submodule("homeassistant.helpers.device_registry")
mock_submodule("homeassistant.helpers.entity_registry")
mock_submodule("homeassistant.components.stt")
mock_submodule("homeassistant.components.tts")
mock_submodule("homeassistant.components.image")

# Assign standard attributes
ha_const = sys.modules["homeassistant.const"]
ha_const.Platform = types.SimpleNamespace(
    CONVERSATION="conversation",
    SENSOR="sensor",
    BINARY_SENSOR="binary_sensor",
    BUTTON="button",
    SELECT="select",
    SWITCH="switch",
    STT="stt",
    TTS="tts",
    IMAGE="image",
    AI_TASK="ai_task",
)
ha_const.CONF_NAME = "name"
ha_const.UnitOfTime = types.SimpleNamespace(MILLISECONDS="ms")
ha_const.EntityCategory = types.SimpleNamespace(
    DIAGNOSTIC="diagnostic",
    CONFIG="config",
)

ha_core = sys.modules["homeassistant.core"]
ha_core.HomeAssistant = MagicMock
ha_core.ServiceCall = MagicMock
ha_core.SupportsResponse = types.SimpleNamespace(
    NONE="none",
    OPTIONAL="optional",
    ONLY="only",
)
ha_core.callback = lambda fn: fn

ha_exc = sys.modules["homeassistant.exceptions"]


class MockHomeAssistantError(Exception):
    pass


ha_exc.HomeAssistantError = MockHomeAssistantError


class MockUpdateFailed(MockHomeAssistantError):
    pass


coord_module = sys.modules["homeassistant.helpers.update_coordinator"]
coord_module.DataUpdateCoordinator = MockDataUpdateCoordinator
coord_module.CoordinatorEntity = MockCoordinatorEntity
coord_module.UpdateFailed = MockUpdateFailed

entity_module = sys.modules["homeassistant.helpers.entity"]
entity_module.Entity = MockEntity

sensor_module = sys.modules["homeassistant.components.sensor"]


class MockSensorEntity(MockEntity):
    _attr_native_value: Any = None
    _attr_native_unit_of_measurement: str | None = None
    _attr_state_class: Any = None
    _attr_device_class: Any = None

    @property
    def native_value(self) -> Any:
        return self._attr_native_value


sensor_module.SensorEntity = MockSensorEntity
sensor_module.SensorEntityDescription = MockEntityDescription
sensor_module.SensorStateClass = types.SimpleNamespace(
    MEASUREMENT="measurement",
    TOTAL="total",
    TOTAL_INCREASING="total_increasing",
)
sensor_module.SensorDeviceClass = types.SimpleNamespace(
    DURATION="duration",
    DATA_SIZE="data_size",
)

# Binary Sensor module
bs_module = sys.modules["homeassistant.components.binary_sensor"]


class MockBinarySensorEntity(MockEntity):
    _attr_is_on: bool = False

    @property
    def is_on(self) -> bool:
        return self._attr_is_on


bs_module.BinarySensorEntity = MockBinarySensorEntity
bs_module.BinarySensorEntityDescription = MockEntityDescription
bs_module.BinarySensorDeviceClass = types.SimpleNamespace(
    CONNECTIVITY="connectivity",
    PROBLEM="problem",
    RUNNING="running",
)

# Button module
btn_module = sys.modules["homeassistant.components.button"]


class MockButtonEntity(MockEntity):
    async def async_press(self) -> None:
        pass


btn_module.ButtonEntity = MockButtonEntity
btn_module.ButtonEntityDescription = MockEntityDescription
btn_module.ButtonDeviceClass = types.SimpleNamespace(
    RESTART="restart",
    UPDATE="update",
)

# Select module
select_module = sys.modules["homeassistant.components.select"]


class MockSelectEntity(MockEntity):
    _attr_current_option: str | None = None
    _attr_options: list[str] = []

    @property
    def current_option(self) -> str | None:
        return self._attr_current_option

    @property
    def options(self) -> list[str]:
        return self._attr_options

    async def async_select_option(self, option: str) -> None:
        self._attr_current_option = option


select_module.SelectEntity = MockSelectEntity
select_module.SelectEntityDescription = MockEntityDescription

# Switch module
switch_module = sys.modules["homeassistant.components.switch"]


class MockSwitchEntity(MockEntity):
    _attr_is_on: bool = False

    @property
    def is_on(self) -> bool:
        return self._attr_is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        self._attr_is_on = True

    async def async_turn_off(self, **kwargs: Any) -> None:
        self._attr_is_on = False


switch_module.SwitchEntity = MockSwitchEntity
switch_module.SwitchEntityDescription = MockEntityDescription

# Diagnostics module
diag_module = sys.modules["homeassistant.components.diagnostics"]


def mock_async_redact_data(data: dict[str, Any], to_redact: Any) -> dict[str, Any]:
    redacted = dict(data)
    for k in data:
        if k in to_redact:
            redacted[k] = "**REDACTED**"
    return redacted


diag_module.async_redact_data = mock_async_redact_data

# Device Registry
dr_module = sys.modules["homeassistant.helpers.device_registry"]


class MockDeviceInfo(dict):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        for k, v in kwargs.items():
            setattr(self, k, v)


dr_module.DeviceInfo = MockDeviceInfo
dr_module.DeviceEntryType = types.SimpleNamespace(SERVICE="service")

# Conversation module
conv_module = sys.modules["homeassistant.components.conversation"]


class MockConversationEntity(MockEntity):
    _attr_supported_features = 1


conv_module.ConversationEntity = MockConversationEntity
conv_module.ConversationEntityFeature = types.SimpleNamespace(CONTROL=1)


@dataclass
class MockConversationInput:
    text: str
    context: Any = None
    conversation_id: str | None = None
    device_id: str | None = None
    language: str = "en"
    agent_id: str | None = None


conv_module.ConversationInput = MockConversationInput


@dataclass
class MockConversationResult:
    response: Any
    conversation_id: str | None = None


conv_module.ConversationResult = MockConversationResult


class MockIntentResponse:
    def __init__(self, language: str = "en") -> None:
        self.language = language
        self.speech: dict[str, Any] = {"plain": {"speech": ""}}

    def async_set_speech(self, speech: str) -> None:
        self.speech = {"plain": {"speech": speech}}


conv_module.intent = types.SimpleNamespace(IntentResponse=MockIntentResponse)
mock_submodule("homeassistant.helpers.intent")
sys.modules["homeassistant.helpers.intent"].IntentResponse = MockIntentResponse

# STT Module
stt_mod = sys.modules["homeassistant.components.stt"]


class MockSpeechToTextEntity(MockEntity):
    pass


@dataclass
class MockSpeechResult:
    text: str
    result: Any


stt_mod.SpeechToTextEntity = MockSpeechToTextEntity
stt_mod.SpeechMetadata = MagicMock
stt_mod.SpeechResult = MockSpeechResult
stt_mod.SpeechResultState = types.SimpleNamespace(SUCCESS="success", ERROR="error")
stt_mod.AudioFormats = types.SimpleNamespace(WAV="wav", OGG="ogg")
stt_mod.AudioCodecs = types.SimpleNamespace(PCM="pcm", OPUS="opus")
stt_mod.AudioBitRates = types.SimpleNamespace(BITRATE_16=16, BITRATE_32=32)
stt_mod.AudioSampleRates = types.SimpleNamespace(
    SAMPLERATE_8000=8000,
    SAMPLERATE_16000=16000,
    SAMPLERATE_44100=44100,
    SAMPLERATE_48000=48000,
)
stt_mod.AudioChannels = types.SimpleNamespace(CHANNEL_MONO=1, CHANNEL_STEREO=2)

# TTS Module
tts_mod = sys.modules["homeassistant.components.tts"]


class MockTextToSpeechEntity(MockEntity):
    pass


tts_mod.TextToSpeechEntity = MockTextToSpeechEntity
tts_mod.TtsAudioType = Any

# Image Module
img_mod = sys.modules["homeassistant.components.image"]


class MockImageEntity(MockEntity):
    def __init__(self, hass: Any = None) -> None:
        super().__init__()
        self.hass = hass


img_mod.ImageEntity = MockImageEntity

cfg_module = sys.modules["homeassistant.config_entries"]
cfg_module.ConfigFlow = MockConfigFlow
cfg_module.OptionsFlow = MockOptionsFlow
cfg_module.ConfigEntry = MagicMock

tpl_module = sys.modules["homeassistant.helpers.template"]


class MockTemplate:
    def __init__(self, template_str: str, hass: Any = None) -> None:
        self.template_str = template_str
        self.hass = hass

    def async_render(self, parse_result: bool = False) -> str:
        return self.template_str


tpl_module.Template = MockTemplate


@pytest.fixture
def mock_client():
    """Mock PaseoClient."""
    client = MagicMock()
    client.async_get_status = AsyncMock(
        return_value={
            "status": "server_info",
            "serverId": "srv_test123",
            "hostname": "test-paseo",
            "version": "0.11.4",
            "listen": "0.0.0.0:6767",
            "latency_ms": 5.4,
        }
    )
    client.async_get_health = AsyncMock(
        return_value={"status": "ok", "timestamp": "2026-10-16T05:00:00Z"}
    )
    client.async_list_mcp_tools = AsyncMock(
        return_value=[
            {"name": "browser_list_tabs", "description": "List browser tabs"},
            {"name": "create_agent", "description": "Spawn agent"},
        ]
    )
    client.async_list_agents = AsyncMock(
        return_value=[{"id": "agent_1", "title": "Test Agent", "status": "running"}]
    )
    client.async_create_agent = AsyncMock(
        return_value={"agentId": "agent_123", "status": "created"}
    )
    client.async_send_agent_prompt = AsyncMock(return_value={"status": "sent"})
    client.async_stop_agent = AsyncMock(return_value={"status": "stopped"})
    client.async_chat_completion = AsyncMock(
        return_value={
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "Paseo response text",
                    }
                }
            ]
        }
    )
    client.async_text_to_speech = AsyncMock(return_value=b"fake-mp3-bytes")
    client.async_speech_to_text = AsyncMock(return_value="Transcribed speech text")
    client.async_generate_image = AsyncMock(
        return_value=["https://example.com/image.png"]
    )
    client.close = AsyncMock()
    return client


@pytest.fixture
def mock_config_entry():
    """Mock ConfigEntry."""
    entry = MagicMock()
    entry.entry_id = "test_entry_id_123"
    entry.title = "Paseo Test"
    entry.domain = "paseo"
    entry.version = 1
    entry.data = {
        "url": "http://127.0.0.1:6767",
        "api_key": "test_key",
        "name": "Paseo Test",
        "server_id": "srv_test123",
        "hostname": "test-paseo",
    }
    entry.options = {
        "conversation_model": "omniroute/coding-cascade",
        "prompt": "Test prompt",
        "ai_task_model": "omniroute/reasoning-latest",
        "ai_task_prompt": "Test AI prompt",
        "workspace": "/config",
        "auto_accept": True,
        "temperature": 0.2,
        "top_p": 0.95,
        "max_tokens": 4096,
        "poll_interval": 30,
    }
    entry.async_on_unload = MagicMock()
    return entry


@pytest.fixture
def mock_hass(mock_client, mock_config_entry):
    """Mock Home Assistant core instance."""
    hass = MagicMock()
    hass.data = {
        "paseo": {
            mock_config_entry.entry_id: {
                "client": mock_client,
            }
        }
    }
    hass.services = MagicMock()
    hass.services.async_register = MagicMock()
    hass.services.async_call = AsyncMock()
    hass.config_entries = MagicMock()
    hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    hass.config_entries.async_reload = AsyncMock(return_value=True)

    def mock_update_entry(
        entry: Any, *, options: Any = None, data: Any = None, **kwargs: Any
    ) -> bool:
        if options is not None:
            entry.options = dict(options)
        if data is not None:
            entry.data = dict(data)
        return True

    hass.config_entries.async_update_entry = MagicMock(side_effect=mock_update_entry)
    return hass
