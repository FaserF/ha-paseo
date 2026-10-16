"""Support for Paseo conversation agent entity."""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any

from homeassistant.components import conversation
from homeassistant.components.conversation import (
    ConversationEntity,
    ConversationEntityFeature,
    ConversationInput,
    ConversationResult,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import template
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .client import PaseoClient
from .const import (
    CONF_CONVERSATION_MODEL,
    CONF_MAX_TOKENS,
    CONF_PROMPT,
    CONF_TEMPERATURE,
    CONF_TOP_P,
    DEFAULT_CONVERSATION_MODEL,
    DEFAULT_MAX_TOKENS,
    DEFAULT_PROMPT,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
    DOMAIN,
)
from .coordinator import PaseoDataUpdateCoordinator
from .helpers import get_device_info

_LOGGER = logging.getLogger(__name__)
MAX_TOOL_ITERATIONS = 10


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up conversation entities from config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    client: PaseoClient = data["client"]
    coordinator: PaseoDataUpdateCoordinator = data["coordinator"]

    async_add_entities([PaseoConversationEntity(entry, client, coordinator)])


class PaseoConversationEntity(
    CoordinatorEntity[PaseoDataUpdateCoordinator], ConversationEntity
):
    """Paseo conversation agent entity."""

    _attr_has_entity_name = True
    _attr_name = "Assist"
    _attr_supported_features = ConversationEntityFeature.CONTROL

    def __init__(
        self,
        entry: ConfigEntry,
        client: PaseoClient,
        coordinator: PaseoDataUpdateCoordinator,
    ) -> None:
        """Initialize the conversation entity."""
        super().__init__(coordinator)
        self.entry = entry
        self.client = client
        self._attr_unique_id = f"{entry.entry_id}_conversation"
        sw_version = coordinator.data.get("version") if coordinator.data else None
        self._attr_device_info = get_device_info(entry, sw_version)
        self.history: dict[str, list[dict[str, Any]]] = {}

    @property
    def supported_languages(self) -> list[str]:
        """Return supported languages."""
        return ["*"]

    async def async_process(self, user_input: ConversationInput) -> ConversationResult:
        """Process a conversational input sentence."""
        options = self.entry.options
        model = options.get(CONF_CONVERSATION_MODEL, DEFAULT_CONVERSATION_MODEL)
        prompt_raw = options.get(CONF_PROMPT, DEFAULT_PROMPT)
        temperature = options.get(CONF_TEMPERATURE, DEFAULT_TEMPERATURE)
        top_p = options.get(CONF_TOP_P, DEFAULT_TOP_P)
        max_tokens = options.get(CONF_MAX_TOKENS, DEFAULT_MAX_TOKENS)

        # Render system prompt template
        try:
            prompt_str = template.Template(prompt_raw, self.hass).async_render(
                parse_result=False
            )
        except Exception as exc:  # noqa: BLE001
            _LOGGER.warning("Error rendering prompt template: %s", exc)
            prompt_str = prompt_raw

        # Prepare Home Assistant LLM API and tools
        tools: list[dict[str, Any]] | None = None
        llm_api = None
        try:
            from homeassistant.helpers import llm

            llm_context = llm.LLMContext(
                platform=DOMAIN,
                context=user_input.context,
                user_prompt=user_input.text,
                language=user_input.language,
                assistant="conversation",
                device_id=user_input.device_id,
            )
            llm_api = await llm.async_get_api(
                self.hass, llm.LLM_API_ASSIST, llm_context
            )
            if llm_api and getattr(llm_api, "tools", None):
                tools = [
                    {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.parameters,
                        },
                    }
                    for tool in llm_api.tools
                ]
        except Exception as exc:  # noqa: BLE001
            _LOGGER.debug("LLM Assist tools could not be loaded: %s", exc)

        conversation_id = user_input.conversation_id or uuid.uuid4().hex
        prior_messages = self.history.get(conversation_id, [])

        messages: list[dict[str, Any]] = [
            {"role": "system", "content": prompt_str},
            *prior_messages,
            {"role": "user", "content": user_input.text},
        ]

        iterations = 0
        final_text = "I encountered an issue processing your request."

        while iterations < MAX_TOOL_ITERATIONS:
            iterations += 1
            try:
                response = await self.client.async_chat_completion(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    top_p=top_p,
                    max_tokens=max_tokens,
                    tools=tools,
                )
            except Exception as exc:  # noqa: BLE001
                _LOGGER.error("Paseo completion error: %s", exc)
                final_text = f"Error communicating with Paseo model: {exc}"
                break

            choice = response.get("choices", [{}])[0]
            msg = choice.get("message", {})
            tool_calls = msg.get("tool_calls")

            if not tool_calls or not llm_api:
                final_text = msg.get("content") or "Action completed."
                messages.append(msg)
                break

            # Process tool calls
            messages.append(msg)
            for tool_call in tool_calls:
                fn = tool_call.get("function", {})
                tool_name = fn.get("name", "")
                tool_args_raw = fn.get("arguments", "{}")
                try:
                    tool_args = json.loads(tool_args_raw) if isinstance(tool_args_raw, str) else tool_args_raw
                except Exception:
                    tool_args = {}

                tool_result: Any = "Error: Tool execution failed"
                try:
                    from homeassistant.helpers import llm
                    tool_input = llm.ToolInput(
                        tool_name=tool_name,
                        tool_args=tool_args,
                    )
                    tool_result = await llm_api.async_call_tool(tool_input)
                except Exception as exc:  # noqa: BLE001
                    _LOGGER.error("Error calling tool %s: %s", tool_name, exc)
                    tool_result = f"Error: {exc}"

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.get("id", str(uuid.uuid4())),
                        "name": tool_name,
                        "content": json.dumps(tool_result),
                    }
                )

        # Store capped history (last 12 turns)
        self.history[conversation_id] = messages[1:][-12:]

        from homeassistant.components.conversation import ConversationResult
        from homeassistant.helpers import intent

        intent_response = intent.IntentResponse(language=user_input.language)
        intent_response.async_set_speech(final_text)

        return ConversationResult(
            response=intent_response, conversation_id=conversation_id
        )
