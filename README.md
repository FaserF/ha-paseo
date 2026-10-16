<p align="center">
  <img src="https://raw.githubusercontent.com/FaserF/ha-paseo/main/brand/logo.png" alt="Paseo Logo" width="360">
</p>

# Paseo for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/default)
[![CI](https://github.com/FaserF/ha-paseo/actions/workflows/ci-orchestrator.yml/badge.svg)](https://github.com/FaserF/ha-paseo/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Semantic Versioning: SemVer](https://img.shields.io/badge/versioning-SemVer-informational.svg)](https://semver.org)

Home Assistant custom integration for **Paseo AI Code Studio & Autonomous Agent Daemon**. Seamlessly bridges Home Assistant to your local Edge add-on or remote cloud Paseo instances (Oracle Cloud VM, Dell Precision worker nodes, or Headscale/Tailscale mesh), providing autonomous code modification in `/config`, real-time MCP agent control, native Home Assistant Assist voice pipelines, AI task engines, configuration diagnostics, and full telemetry.

---

## 🌟 Key Features & Platforms

### 1. 🗣️ Native Assist Voice & Conversation Agent (`conversation.paseo_*`)
- **Built-in Smart Home Tool Calling**: Directly control lights, switches, climates, query states, run scripts, and trigger automations via Home Assistant's native LLM Assist API.
- **Autonomous Multi-Turn Reasoning**: Capable of executing up to 10 sequential tool iterations in a single conversation turn to fulfill complex multi-device instructions.
- **Template System Prompts**: Full Jinja2 rendering support for system instructions, plus dynamic temperature, top_p, and token parameters.

### 2. 🧠 Autonomous AI Task Engine (`ai_task.paseo_*`)
- **Native 2026 AI Task Compliance**: Compliant with Home Assistant's autonomous AI Task specifications.
- **Automated Smarthome Engineering**: Autonomously draft blueprints, validate YAML syntax, fix broken configurations, and audit smart home automations directly inside `/config`.

### 3. 📊 Daemon & Server Telemetry Sensors (`sensor.paseo_*`)
- `sensor.paseo_status`: Operational status of the daemon (`operational`, `degraded`, `offline`).
- `sensor.paseo_latency`: Roundtrip ping response latency in milliseconds.
- `sensor.paseo_version`: Paseo daemon software version (e.g. `0.11.4`).
- `sensor.paseo_hostname`: Hostname of the executing worker node (`oracle-paseo`, `edfe50eb-paseo`).
- `sensor.paseo_active_agents`: Real-time count of active autonomous coding agents.
- `sensor.paseo_available_mcp_tools`: Count of active Model Context Protocol (MCP) tools registered on the server.
- `sensor.paseo_workspace`: Active filesystem directory (e.g. `/config`, `/addons`).

### 4. 🛡️ System Binary Sensors (`binary_sensor.paseo_*`)
- `binary_sensor.paseo_connected`: True when the Paseo daemon is reachable and responding.
- `binary_sensor.paseo_problem`: Flags connectivity, authentication, or daemon degraded health.
- `binary_sensor.paseo_busy`: Turns on whenever autonomous agents are actively running.
- `binary_sensor.paseo_edge_addon_host`: Distinguishes local Home Assistant Edge Add-on instances from remote Cloud nodes.

### 5. 🎛️ Dynamic Model Selectors (`select.paseo_*`)
- **`select.paseo_conversation_model`**: Dynamically switch the Assist model on the fly (e.g., `omniroute/coding-cascade`, `omniroute/fast-cascade`).
- **`select.paseo_ai_task_model`**: Dynamically switch the reasoning model for background AI tasks.

### 6. ⚡ Autonomous Switches & Action Buttons (`switch` & `button`)
- **`switch.paseo_autonomous_execution`**: Toggle autonomous tool permissions and auto-accept modes.
- **`button.paseo_refresh_telemetry`**: Force an instant data poll and update diagnostic attributes.
- **`button.paseo_validate_home_configuration`**: Trigger Home Assistant configuration validation before reloading or restarting.

### 7. 🛠️ Custom Services (`services.yaml`)
- **`paseo.create_agent`**: Spawns an autonomous Paseo agent with custom prompts, roles (`code`, `plan`, `build`, `ask`), and workspace targets.
- **`paseo.send_prompt`**: Steer or provide follow-up directives to an existing agent.
- **`paseo.stop_agent`**: Cancel or interrupt an active agent.
- **`paseo.execute_task`**: Run a one-shot smart home automation task.
- **`paseo.validate_config`**: Validate Home Assistant configuration.
- **`paseo.refresh_status`**: Programmatically trigger a coordinator refresh.

---

## 🚀 Installation

### Option 1: HACS (Recommended)

1. Open **HACS** in Home Assistant.
2. Navigate to **Integrations**, click the three dots in the upper right corner, and select **Custom repositories**.
3. Add `https://github.com/FaserF/ha-paseo` with category **Integration**.
4. Search for **Paseo**, click **Download**, and restart Home Assistant.

### Option 2: Manual Installation

1. Download the latest release zip from the [Releases page](https://github.com/FaserF/ha-paseo/releases).
2. Unpack and copy the `custom_components/paseo/` directory into your Home Assistant `<config_dir>/custom_components/paseo/`.
3. Restart Home Assistant.

---

## ⚙️ Configuration & Multi-Node Support

Paseo supports configuring multiple instances simultaneously (e.g., your **Oracle Cloud VM Paseo** and your **Home Assistant Edge Add-on Paseo**).

1. In Home Assistant, navigate to **Settings > Devices & Services > Add Integration**.
2. Search for **Paseo**.
3. Fill in the connection settings:
   - **Instance Name**: e.g., `Oracle VM Paseo` or `Home Assistant Paseo Edge`
   - **Daemon URL**: e.g., `http://100.64.0.1:6767` (Oracle VM) or `http://127.0.0.1:6767` / `http://100.64.0.2:6767` (Edge Add-on)
   - **Daemon Password / API Key**: Optional bearer password configured on the daemon.

---

## 🧪 Testing & Quality Assurance

This integration adheres to strict semantic versioning (`major.minor.patch`), robust linting with `ruff`, strict type checking with `mypy`, and automated test suites with `pytest`.

Run the test suite locally:
```bash
pytest tests/ -v
```

---

## 📄 License & Credits

Distributed under the **MIT License**. Created and maintained by [FaserF](https://github.com/FaserF).
Logo and branding assets property of [Paseo](https://github.com/getpaseo).
