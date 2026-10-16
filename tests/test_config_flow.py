"""Tests for Paseo config flow and options flow."""

from unittest.mock import patch

import pytest

from custom_components.paseo.client import CannotConnect, InvalidAuth
from custom_components.paseo.config_flow import PaseoConfigFlow, PaseoOptionsFlow
from custom_components.paseo.const import (
    CONF_AI_TASK_MODEL,
    CONF_API_KEY,
    CONF_NAME,
    CONF_URL,
)


@pytest.mark.asyncio
async def test_flow_user_init(mock_hass):
    """Test initial user step shows form."""
    flow = PaseoConfigFlow()
    flow.hass = mock_hass

    result = await flow.async_step_user(None)
    assert result["type"] == "form"
    assert result["step_id"] == "user"
    assert not result["errors"]


@pytest.mark.asyncio
async def test_flow_user_success(mock_hass, mock_client):
    """Test successful user configuration."""
    flow = PaseoConfigFlow()
    flow.hass = mock_hass

    with patch(
        "custom_components.paseo.config_flow.PaseoClient", return_value=mock_client
    ):
        result = await flow.async_step_user(
            {
                CONF_NAME: "Oracle VM Paseo",
                CONF_URL: "http://100.64.0.1:6767",
                CONF_API_KEY: "secret_pass",
            }
        )
        assert result["type"] == "create_entry"
        assert result["title"] == "Oracle VM Paseo"
        assert result["data"][CONF_URL] == "http://100.64.0.1:6767"
        assert result["data"]["server_id"] == "srv_test123"


@pytest.mark.asyncio
async def test_flow_user_invalid_auth(mock_hass, mock_client):
    """Test user step with invalid authentication."""
    flow = PaseoConfigFlow()
    flow.hass = mock_hass
    mock_client.async_get_status.side_effect = InvalidAuth("bad auth")

    with patch(
        "custom_components.paseo.config_flow.PaseoClient", return_value=mock_client
    ):
        result = await flow.async_step_user(
            {
                CONF_NAME: "Paseo",
                CONF_URL: "http://127.0.0.1:6767",
                CONF_API_KEY: "wrong_pass",
            }
        )
        assert result["type"] == "form"
        assert result["errors"]["base"] == "invalid_auth"


@pytest.mark.asyncio
async def test_flow_user_cannot_connect(mock_hass, mock_client):
    """Test user step with connection failure."""
    flow = PaseoConfigFlow()
    flow.hass = mock_hass
    mock_client.async_get_status.side_effect = CannotConnect("down")

    with patch(
        "custom_components.paseo.config_flow.PaseoClient", return_value=mock_client
    ):
        result = await flow.async_step_user(
            {
                CONF_NAME: "Paseo",
                CONF_URL: "http://127.0.0.1:9999",
            }
        )
        assert result["type"] == "form"
        assert result["errors"]["base"] == "cannot_connect"


@pytest.mark.asyncio
async def test_flow_hassio_discovery(mock_hass, mock_client):
    """Test Supervisor Add-on discovery flow."""
    flow = PaseoConfigFlow()
    flow.hass = mock_hass

    with patch(
        "custom_components.paseo.config_flow.PaseoClient", return_value=mock_client
    ):
        result = await flow.async_step_hassio({"host": "edfe50eb-paseo"})
        assert result["type"] == "create_entry"
        assert "Paseo" in result["title"]


@pytest.mark.asyncio
async def test_options_flow(mock_hass, mock_config_entry):
    """Test options flow initialization and submission."""
    flow = PaseoOptionsFlow(mock_config_entry)
    flow.hass = mock_hass

    init_result = await flow.async_step_init(None)
    assert init_result["type"] == "form"
    assert init_result["step_id"] == "init"

    save_result = await flow.async_step_init(
        {
            CONF_AI_TASK_MODEL: "omniroute/fast-cascade",
            "auto_accept": False,
        }
    )
    assert save_result["type"] == "create_entry"
    assert save_result["data"][CONF_AI_TASK_MODEL] == "omniroute/fast-cascade"
    assert save_result["data"]["auto_accept"] is False
