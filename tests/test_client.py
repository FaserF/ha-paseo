"""Tests for the Paseo API client."""

from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp
import pytest
from custom_components.paseo.client import (
    CannotConnect,
    InvalidAuth,
    PaseoClient,
    PaseoRpcError,
)


@pytest.mark.asyncio
async def test_client_get_status_success():
    """Test successful /api/status call."""
    mock_resp = AsyncMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(
        return_value={
            "status": "server_info",
            "serverId": "srv_123",
            "hostname": "oracle-paseo",
            "version": "0.11.4",
            "listen": "0.0.0.0:6767",
        }
    )

    mock_session = MagicMock()
    mock_session.closed = False
    mock_session.get.return_value.__aenter__.return_value = mock_resp

    client = PaseoClient("http://127.0.0.1:6767", api_key="secret", session=mock_session)
    res = await client.async_get_status()

    assert res["status"] == "server_info"
    assert res["serverId"] == "srv_123"
    assert res["hostname"] == "oracle-paseo"
    assert "latency_ms" in res


@pytest.mark.asyncio
async def test_client_get_status_auth_error():
    """Test 401 raises InvalidAuth."""
    mock_resp = AsyncMock()
    mock_resp.status = 401

    mock_session = MagicMock()
    mock_session.closed = False
    mock_session.get.return_value.__aenter__.return_value = mock_resp

    client = PaseoClient("http://127.0.0.1:6767", api_key="wrong", session=mock_session)
    with pytest.raises(InvalidAuth):
        await client.async_get_status()


@pytest.mark.asyncio
async def test_client_get_status_connect_error():
    """Test connection error raises CannotConnect."""
    mock_session = MagicMock()
    mock_session.closed = False
    mock_session.get.side_effect = aiohttp.ClientError("Conn failed")

    client = PaseoClient("http://127.0.0.1:6767", session=mock_session)
    with pytest.raises(CannotConnect):
        await client.async_get_status()


@pytest.mark.asyncio
async def test_client_call_mcp_rpc_success():
    """Test successful MCP JSON-RPC call."""
    mock_resp = AsyncMock()
    mock_resp.status = 200
    mock_resp.text = AsyncMock(
        return_value='data: {"jsonrpc":"2.0","id":1,"result":{"tools":[{"name":"create_agent"}]}}\n\n'
    )

    mock_session = MagicMock()
    mock_session.closed = False
    mock_session.post.return_value.__aenter__.return_value = mock_resp

    client = PaseoClient("http://127.0.0.1:6767", api_key="secret", session=mock_session)
    res = await client.async_call_mcp_rpc("tools/list", {})
    assert "tools" in res
    assert res["tools"][0]["name"] == "create_agent"


@pytest.mark.asyncio
async def test_client_call_mcp_rpc_error():
    """Test MCP JSON-RPC error payload raises PaseoRpcError."""
    mock_resp = AsyncMock()
    mock_resp.status = 200
    mock_resp.text = AsyncMock(
        return_value='{"jsonrpc":"2.0","id":1,"error":{"code":-32601,"message":"Method not found"}}'
    )

    mock_session = MagicMock()
    mock_session.closed = False
    mock_session.post.return_value.__aenter__.return_value = mock_resp

    client = PaseoClient("http://127.0.0.1:6767", api_key="secret", session=mock_session)
    with pytest.raises(PaseoRpcError):
        await client.async_call_mcp_rpc("invalid_method", {})
