"""API Client for Paseo AI Code Studio & Web IDE."""

from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any

import aiohttp
from homeassistant.exceptions import HomeAssistantError

_LOGGER = logging.getLogger(__name__)


class PaseoError(HomeAssistantError):
    """Base exception for Paseo errors."""


class CannotConnect(PaseoError):
    """Exception to indicate connection error."""


class InvalidAuth(PaseoError):
    """Exception to indicate invalid authentication."""


class PaseoRpcError(PaseoError):
    """Exception to indicate JSON-RPC error."""


class PaseoClient:
    """Client for interacting with Paseo daemon and MCP agent endpoints."""

    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        session: aiohttp.ClientSession | None = None,
        timeout: int = 25,
    ) -> None:
        """Initialize the Paseo client."""
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key.strip() if api_key else None
        self._session = session
        self._own_session = False
        self._timeout = timeout

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create the aiohttp ClientSession."""
        if self._session is None or getattr(self._session, "closed", False) is True:
            self._session = aiohttp.ClientSession()
            self._own_session = True
        return self._session

    def _get_headers(self) -> dict[str, str]:
        """Construct common HTTP request headers."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "User-Agent": "HomeAssistant-Paseo-Integration/1.0.0",
        }
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers

    async def close(self) -> None:
        """Close the client session if owned."""
        if self._own_session and self._session and not self._session.closed:
            await self._session.close()

    async def async_get_status(self) -> dict[str, Any]:
        """Fetch daemon status and server identity from /api/status."""
        session = await self._get_session()
        url = f"{self._base_url}/api/status"
        headers = self._get_headers()
        start = time.monotonic()

        try:
            async with asyncio.timeout(self._timeout):
                async with session.get(url, headers=headers) as resp:
                    latency = round((time.monotonic() - start) * 1000, 2)
                    if resp.status == 401:
                        raise InvalidAuth("Invalid Paseo password or bearer token")
                    if resp.status != 200:
                        text = await resp.text()
                        raise CannotConnect(f"HTTP {resp.status} checking status: {text}")

                    data = await resp.json()
                    data["latency_ms"] = latency
                    return data
        except TimeoutError as err:
            raise CannotConnect(f"Timeout connecting to Paseo at {url}") from err
        except aiohttp.ClientError as err:
            raise CannotConnect(f"ClientError connecting to Paseo at {url}: {err}") from err

    async def async_get_health(self) -> dict[str, Any]:
        """Fetch basic health status from /api/health."""
        session = await self._get_session()
        url = f"{self._base_url}/api/health"
        headers = self._get_headers()

        try:
            async with asyncio.timeout(self._timeout):
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 401:
                        raise InvalidAuth("Invalid Paseo password or bearer token")
                    if resp.status != 200:
                        text = await resp.text()
                        raise CannotConnect(f"HTTP {resp.status} checking health: {text}")
                    return await resp.json()
        except TimeoutError as err:
            raise CannotConnect(f"Timeout connecting to Paseo at {url}") from err
        except aiohttp.ClientError as err:
            raise CannotConnect(f"ClientError connecting to Paseo at {url}: {err}") from err

    async def async_call_mcp_rpc(
        self, method: str, params: dict[str, Any] | None = None
    ) -> Any:
        """Execute a JSON-RPC method against the /mcp/agents Streamable HTTP endpoint."""
        session = await self._get_session()
        url = f"{self._base_url}/mcp/agents"
        headers = self._get_headers()
        payload = {
            "jsonrpc": "2.0",
            "id": int(time.time() * 1000),
            "method": method,
            "params": params or {},
        }

        try:
            async with asyncio.timeout(self._timeout):
                async with session.post(url, headers=headers, json=payload) as resp:
                    if resp.status == 401:
                        raise InvalidAuth("Unauthorized: Agent MCP endpoint requires valid daemon password")
                    if resp.status not in (200, 202):
                        text = await resp.text()
                        raise CannotConnect(f"HTTP {resp.status} on MCP RPC: {text}")

                    raw_text = await resp.text()
                    msg: dict[str, Any] | None = None

                    # Parse SSE lines if returned as event stream
                    for line in raw_text.splitlines():
                        if line.startswith("data:"):
                            chunk = line[5:].strip()
                            if chunk and chunk != "[DONE]":
                                try:
                                    msg = json.loads(chunk)
                                    break
                                except json.JSONDecodeError:
                                    continue

                    if msg is None:
                        try:
                            msg = json.loads(raw_text)
                        except json.JSONDecodeError as err:
                            raise PaseoRpcError(f"Invalid JSON response from MCP: {raw_text[:200]}") from err

                    if msg.get("error"):
                        raise PaseoRpcError(f"Paseo RPC error: {msg['error']}")

                    return msg.get("result", msg)
        except TimeoutError as err:
            raise CannotConnect(f"Timeout communicating with Paseo MCP endpoint at {url}") from err
        except aiohttp.ClientError as err:
            raise CannotConnect(f"ClientError communicating with Paseo MCP at {url}: {err}") from err

    async def async_list_mcp_tools(self) -> list[dict[str, Any]]:
        """List all available tools exposed by the Paseo MCP catalog."""
        try:
            res = await self.async_call_mcp_rpc("tools/list", {})
            if isinstance(res, dict) and "tools" in res:
                return res["tools"]
            return []
        except Exception as exc:  # noqa: BLE001
            _LOGGER.debug("Could not list MCP tools from Paseo: %s", exc)
            return []

    async def async_call_mcp_tool(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> Any:
        """Call a specific tool on the Paseo MCP endpoint."""
        params = {"name": tool_name, "arguments": arguments}
        return await self.async_call_mcp_rpc("tools/call", params)

    async def async_create_agent(
        self,
        title: str,
        initial_prompt: str,
        workspace: str = "/config",
        role: str = "code",
        provider: str = "omniroute/coding-cascade",
        background: bool = True,
    ) -> dict[str, Any]:
        """Spawn an autonomous AI coding agent on Paseo."""
        payload = {
            "title": title,
            "initialPrompt": initial_prompt,
            "background": background,
            "provider": provider,
            "settings": {"modeId": role},
            "labels": {
                "role": role,
                "orchestrator": "homeassistant",
                "source": "ha-paseo-integration",
            },
            "workspaceId": workspace,
        }
        res = await self.async_call_mcp_tool("create_agent", payload)
        return res if isinstance(res, dict) else {"result": res}

    async def async_list_agents(self) -> list[dict[str, Any]]:
        """List active agents from Paseo."""
        try:
            res = await self.async_call_mcp_tool("list_agents", {})
            if isinstance(res, dict):
                return res.get("agents", [])
            if isinstance(res, list):
                return res
            return []
        except Exception as exc:  # noqa: BLE001
            _LOGGER.debug("Could not list agents from Paseo: %s", exc)
            return []

    async def async_get_agent_status(self, agent_id: str) -> dict[str, Any]:
        """Fetch current status and activities of a specific agent."""
        res = await self.async_call_mcp_tool("get_agent_status", {"agentId": agent_id})
        return res if isinstance(res, dict) else {"result": res}

    async def async_send_agent_prompt(
        self, agent_id: str, prompt: str, background: bool = True
    ) -> dict[str, Any]:
        """Send follow-up instructions to an active Paseo agent."""
        res = await self.async_call_mcp_tool(
            "send_agent_prompt",
            {"agentId": agent_id, "prompt": prompt, "background": background},
        )
        return res if isinstance(res, dict) else {"result": res}

    async def async_stop_agent(self, agent_id: str) -> dict[str, Any]:
        """Stop or interrupt a running Paseo agent."""
        res = await self.async_call_mcp_tool("stop_agent", {"agentId": agent_id})
        return res if isinstance(res, dict) else {"result": res}

    async def async_chat_completion(
        self,
        messages: list[dict[str, Any]],
        model: str,
        temperature: float = 0.2,
        top_p: float = 0.95,
        max_tokens: int = 4096,
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str | dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute chat completion via OmniRoute / Paseo API."""
        session = await self._get_session()
        # Direct v1 chat completions endpoint or OmniRoute proxy
        url = f"{self._base_url}/v1/chat/completions"
        headers = self._get_headers()

        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
        }
        if tools:
            payload["tools"] = tools
        if tool_choice:
            payload["tool_choice"] = tool_choice

        try:
            async with asyncio.timeout(self._timeout * 2):
                async with session.post(url, headers=headers, json=payload) as resp:
                    if resp.status == 401:
                        raise InvalidAuth("Invalid authentication token for chat completion")
                    if resp.status != 200:
                        text = await resp.text()
                        raise CannotConnect(f"HTTP {resp.status} on chat completion: {text}")
                    return await resp.json()
        except TimeoutError as err:
            raise CannotConnect(f"Timeout on chat completion to {url}") from err
        except aiohttp.ClientError as err:
            raise CannotConnect(f"ClientError on chat completion to {url}: {err}") from err
