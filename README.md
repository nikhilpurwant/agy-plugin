# TaskTracker — Demo Application, FastMCP Server & Antigravity CLI Plugin

A complete, production-grade reference implementation demonstrating the end-to-end architecture of a **Web Application**, a **FastMCP Server**, and an **Antigravity CLI (`agy`) Plugin** bundling all plugin capabilities: **Skills**, **Agents**, **Commands**, **Hooks**, **Rules**, and **MCP Server Configurations**.

---

## 📐 Architecture Overview

```mermaid
flowchart TD
    subgraph AntigravityPlatform["Google Antigravity Platform (CLI & IDE)"]
        PluginManifest["plugin.json (tasktracker)"]
        SlashCmds["commands/tasktracker/*.toml<br/>(/tasktracker:list, /tasktracker:triage, etc.)"]
        Skills["skills/* (Runbooks & SOPs)"]
        Subagents["agents/* (Specialized Personas)"]
        Hooks["hooks.json (Lifecycle Hooks)"]
        Rules["rules/AGENTS.md (Guidelines)"]
        MCPConfig["mcp_config.json"]
    end

    subgraph MCPServer["FastMCP Server (mcp/)"]
        TransportHTTP["Streamable HTTP (Default: :8080/mcp)"]
        TransportSSE["SSE (:8080/sse)"]
        TransportStdio["Stdio Transport"]
        MCPTools["MCP Tools (list, create, update, delete, metrics)"]
        MCPResources["MCP Resources (tasktracker://tasks/summary)"]
        MCPPrompts["MCP Prompts (triage_tasks, daily_standup)"]
    end

    subgraph WebApp["TaskTracker Flask App (app/)"]
        AuthSystem["Dual Authentication<br/>(JWT for UI / API Key for MCP)"]
        RESTAPI["REST API (/api/tasks, /api/auth, /api/tasks/stats)"]
        InMemoryDB["In-Memory Thread-Safe Database"]
        BootstrapUI["Pure Vanilla JS + Bootstrap 5 UI<br/>(index.html & login.html - No Custom CSS / Jinja)"]
    end

    MCPConfig -->|"MCP Protocol over HTTP (:8080/mcp)"| TransportHTTP
    MCPTools -->|"Authenticated REST Requests with X-API-Key"| RESTAPI
    BootstrapUI -->|"JWT Bearer Token Requests"| RESTAPI
    RESTAPI --> InMemoryDB
```

---

## 🗂️ Repository Structure

```text
.
├── app/                                    # 1. Flask CRUD Application & Web UI
│   ├── .env.example                        # App environment variable template
│   ├── .env                                # Active credentials & server settings
│   ├── app.py                              # Flask server with REST API & in-memory DB
│   ├── pyproject.toml                      # UV package definitions for app
│   └── static/                             # Pure static assets (No Jinja)
│       ├── index.html                      # Bootstrap 5 Dashboard UI with vanilla JS fetch
│       └── login.html                      # Bootstrap 5 JWT Login UI
│
├── mcp/                                    # 2. FastMCP Server
│   ├── .env.example                        # MCP server configuration template
│   ├── .env                                # Active MCP transport & API key config
│   ├── pyproject.toml                      # UV package definitions for FastMCP
│   └── server.py                           # FastMCP server (http, sse, stdio)
│
├── plugin/                                 # 3. Complete Antigravity CLI Plugin
│   ├── plugin.json                         # Plugin manifest declaration (name: tasktracker)
│   ├── mcp_config.json                     # MCP server configuration (HTTP streamable transport)
│   ├── hooks.json                          # Lifecycle hooks definition
│   ├── agents/                             # Subagent persona definitions
│   │   ├── task-manager-agent.md           # Project coordinator subagent
│   │   └── qa-triage-agent.md              # QA & bug triage subagent
│   ├── commands/                           # Custom user-facing slash commands
│   │   └── tasktracker/
│   │       ├── list.toml                   # /tasktracker:list
│   │       ├── create.toml                 # /tasktracker:create
│   │       ├── triage.toml                 # /tasktracker:triage
│   │       ├── stats.toml                  # /tasktracker:stats
│   │       └── setup.toml                  # /tasktracker:setup
│   ├── rules/                              # Behavioral constraints & standards
│   │   └── AGENTS.md                       # TaskTracker workspace rules
│   ├── skills/                             # Procedural runbooks with YAML frontmatter
│   │   ├── task-operations/
│   │   │   └── SKILL.md                    # CRUD operations skill
│   │   └── incident-triage/
│   │       └── SKILL.md                    # Blocker & incident triage skill
│   └── scripts/                            # Hook handler execution scripts
│       ├── pre_tool_check.py               # PreToolUse safety gate
│       ├── post_tool_audit.py              # PostToolUse audit logger
│       ├── pre_invocation_context.py       # PreInvocation context injector
│       └── stop_checker.py                 # Stop termination validator
│
└── README.md                               # Complete documentation & user guide
```

---

## ⚡ Quick Start Guide

### Prerequisites
- **Python**: 3.10+
- **UV Package Manager**: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Antigravity CLI (`agy`)**: Installed and in your `$PATH`

---

### Step 1: Launch the Flask Application (`app/`)

1. Navigate to `app/`:
   ```bash
   cd app
   ```
2. Start the application with `uv`:
   ```bash
   uv run app.py
   ```
3. Open your browser:
   - **Dashboard**: `http://127.0.0.1:5050` (Redirects to `/login` if not signed in)
   - **Login**: `http://127.0.0.1:5050/login`
   - **Default Credentials** (from `.env`):
     - Username: `admin`
     - Password: `password123`

---

### Step 2: Launch the FastMCP Server (`mcp/`)

The FastMCP server exposes TaskTracker tools, resources, and prompts over three transports: **Streamable HTTP** (default), **SSE**, and **Stdio**.

#### 1. Streamable HTTP Mode (Default)
```bash
cd mcp
uv run server.py --transport http --port 8080
```
*Server endpoint: `http://127.0.0.1:8080/mcp`*

#### 2. SSE Mode
```bash
cd mcp
uv run server.py --transport sse --port 8080
```
*Server endpoint: `http://127.0.0.1:8080/sse`*

#### 3. Stdio Mode (for local process MCP integrations)
```bash
cd mcp
uv run server.py --transport stdio
```

---

### Step 3: Validate & Use the Antigravity Plugin (`plugin/`)

1. Validate the plugin structure using the Antigravity CLI:
   ```bash
   agy plugin validate ./plugin
   ```
   **Output:**
   ```text
   [ok]    ./plugin
     ✔ skills      : 2 processed
     ✔ agents      : 2 processed
     ✔ commands    : 1 processed (converted to skills)
     ✔ mcpServers  : 1 processed
     ✔ hooks       : 4 processed
   ```

2. Enable or install the plugin:
   - **Workspace Level**: Place or link into `.agents/plugins/tasktracker/`
   - **Global Level**: Copy or link into `~/.gemini/config/plugins/tasktracker/`
   - **Dynamic Link**: Add to `.agents/plugins.json` or `~/.gemini/config/plugins.json`:
     ```json
     {
       "entries": [
         { "path": "/path/to/agy-plugin/plugin" }
       ]
     }
     ```

---

## 🔑 Authentication Architecture

The application implements a dual-mode authentication scheme to secure both browser sessions and machine-to-machine agents:

| Client Type | Auth Mechanism | Header Used | Source of Credentials |
| :--- | :--- | :--- | :--- |
| **Web UI (Browser)** | **JWT (Bearer Token)** | `Authorization: Bearer <jwt_token>` | Generated via `POST /api/auth/login` using `DEMO_USERNAME` & `DEMO_PASSWORD` |
| **FastMCP Server & CLI** | **API Key** | `X-API-Key: <api_key>` | Read from `.env` (`API_KEY`) |

---

## 📡 REST API Reference

| Method | Endpoint | Auth | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/health` | Public | Service health check |
| `POST` | `/api/auth/login` | Public | Authenticate with username/password, returns JWT |
| `GET` | `/api/auth/me` | JWT / Key | Get authenticated user profile |
| `GET` | `/api/tasks` | JWT / Key | List tasks (query params: `status`, `priority`, `search`) |
| `GET` | `/api/tasks/<id>` | JWT / Key | Get task details by ID |
| `POST` | `/api/tasks` | JWT / Key | Create a new task (`title`, `description`, `priority`, `assignee`) |
| `PUT` | `/api/tasks/<id>` | JWT / Key | Update task fields and status |
| `DELETE`| `/api/tasks/<id>` | JWT / Key | Delete a task |
| `GET` | `/api/tasks/stats` | JWT / Key | Aggregated KPI stats and completion percentage |
| `POST` | `/api/tasks/bulk-status` | JWT / Key | Bulk update status for multiple task IDs |

---

## 🛠️ FastMCP Server Capabilities

### Tools
- **`list_tasks(status, priority, search)`**: Filtered task discovery.
- **`get_task(task_id)`**: Fetch task metadata.
- **`create_task(title, description, priority, status, assignee)`**: Create tasks.
- **`update_task(task_id, title, description, status, priority, assignee)`**: Edit task details.
- **`delete_task(task_id)`**: Remove tasks.
- **`get_task_metrics()`**: Retrieve KPI stats and completion metrics.
- **`bulk_update_task_status(task_ids, status)`**: Batch status transitions.
- **`check_api_health()`**: Test Flask backend connectivity.

### Resources
- **`tasktracker://tasks/summary`**: Real-time project overview and markdown summary.
- **`tasktracker://tasks/{task_id}`**: Formatted markdown detail for an individual task.

### Prompts
- **`triage_tasks`**: Prompt for evaluating open blockers and missing assignees.
- **`daily_standup_report`**: Prompt for generating daily team standup summaries.

---

## 🧩 Antigravity Plugin Component Matrix

| Component | File / Directory | Purpose in Antigravity |
| :--- | :--- | :--- |
| **Manifest** | `plugin.json` | Identifies name (`tasktracker`), version, and metadata |
| **MCP Config** | `mcp_config.json` | Exposes FastMCP tools and resources (HTTP streamable transport) |
| **Lifecycle Hooks** | `hooks.json` + `scripts/` | Deterministic pre/post execution gates (`PreToolUse`, `PostToolUse`, `PreInvocation`, `Stop`) |
| **Subagents** | `agents/*.md` | Specialized persona definitions (`task-manager-agent`, `qa-triage-agent`) |
| **Skills** | `skills/*/SKILL.md` | Procedural workflows & runbooks (`task-operations`, `incident-triage`) |
| **Slash Commands**| `commands/tasktracker/*.toml` | Custom user commands (`/tasktracker:list`, `/tasktracker:create`, `/tasktracker:triage`, `/tasktracker:stats`, `/tasktracker:setup`) |
| **Rules** | `rules/AGENTS.md` | Workspace-level coding and workflow constraints |

---

## 🧪 Testing & Verification

### Run End-to-End Verification Script
To test all 3 tiers in one automated command:
```bash
# 1. Start App in background
cd app && uv run app.py &

# 2. Test FastMCP execution
cd ../mcp && uv run python3 -c "
from server import list_tasks, get_task_metrics
print('Live Metrics:', get_task_metrics())
print('Tasks:', list_tasks())
"

# 3. Validate Antigravity Plugin
cd .. && agy plugin validate ./plugin
```

---

## ❓ Frequently Asked Questions (Q&A)

<details>
<summary><strong>Q: Generally when a command is provided to harness like you (AGY) how do you cycle through all these plugin components? Give an example involving each of the components and the path in which they are evaluated - Give me a table</strong></summary>

### Answer

When a command or prompt is provided to an Antigravity (`agy` / Jetski) harness, the system cycles through plugin components in a deterministic lifecycle spanning **Discovery**, **Invocation**, **Execution**, and **Termination**.

---

#### Example Scenario: Running `/tasktracker:triage critical blockers`

Here is an end-to-end example showing how each plugin component is evaluated when a user runs the slash command `/tasktracker:triage critical blockers`:

```text
User Input: /tasktracker:triage critical blockers
   │
   ▼
1. Plugin Manifest (plugin.json) & MCP Config (mcp_config.json) ──▶ Discovered & registered at startup
   │
   ▼
2. Slash Command (commands/tasktracker/triage.toml) ─────────────▶ Interpolates {{args}} into prompt
   │
   ▼
3. Pre-Invocation Hook (scripts/pre_invocation_context.py) ──────▶ Injects runtime context & status
   │
   ▼
4. Rules (rules/AGENTS.md) ──────────────────────────────────────▶ Enforces constraints (e.g. FastMCP only)
   │
   ▼
5. Skills (skills/incident-triage/SKILL.md) ────────────────────▶ Progressively loaded on demand
   │
   ▼
6. Subagents (agents/qa-triage-agent.md) ────────────────────────▶ Invoked to isolate specialist triage work
   │
   ▼
7. Pre-Tool Hook (scripts/pre_tool_check.py) ────────────────────▶ Intercepts tool calls (safety gate)
   │
   ▼
8. FastMCP Server (mcp/server.py via mcp_config.json) ───────────▶ Executes tools/queries over HTTP
   │
   ▼
9. Post-Tool Hook (scripts/post_tool_audit.py) ──────────────────▶ Logs tool telemetry and audit trail
   │
   ▼
10. Stop Hook (scripts/stop_checker.py) ─────────────────────────▶ Verifies completion criteria before output
```

---

#### Evaluation Path Table

| Step | Component | Plugin File / Path | Lifecycle Stage | Evaluation & Action |
|:---:|:---|:---|:---|:---|
| **1** | **Plugin Manifest** | [plugin/plugin.json](plugin/plugin.json) | **Session Init / Discovery** | Harness discovers the plugin bundle, registers its namespace (`tasktracker`), and initializes its component directories. |
| **2** | **MCP Config** | [plugin/mcp_config.json](plugin/mcp_config.json) | **Discovery / Tool Registration** | Harness connects to `http://127.0.0.1:8080/mcp`, discovers registered tools (`list_tasks`, `update_task`), prompts, and resources. |
| **3** | **Rules** | [plugin/rules/AGENTS.md](plugin/rules/AGENTS.md) | **Context Assembly** | Loaded hierarchically into the system prompt. Enforces hard constraints (e.g., *strict prohibition on direct cURL/API calls; FastMCP only*). |
| **4** | **Slash Command** | [plugin/commands/tasktracker/triage.toml](plugin/commands/tasktracker/triage.toml) | **Command Ingestion** | Harness routes `/tasktracker:triage`, expands template with arguments (`critical blockers`), and produces the user prompt. |
| **5** | **Lifecycle Hook (PreInvocation)** | [plugin/hooks.json](plugin/hooks.json) & [plugin/scripts/pre_invocation_context.py](plugin/scripts/pre_invocation_context.py) | **Pre-Invocation** | Runs before LLM generation. Injects dynamic runtime state (e.g., server health, active plugin indicators) into context. |
| **6** | **Skills** | [plugin/skills/incident-triage/SKILL.md](plugin/skills/incident-triage/SKILL.md) | **Model Reasoning (Progressive Disclosure)** | Only the skill name and description are in the initial prompt. When the agent recognizes triage is needed, it calls `view_file` to load the full runbook into context. |
| **7** | **Subagents** | [plugin/agents/qa-triage-agent.md](plugin/agents/qa-triage-agent.md) | **Execution / Delegation** | If complex or long-running triage is required, the primary agent invokes `qa-triage-agent` via `invoke_subagent`, running in an isolated sub-conversation. |
| **8** | **Lifecycle Hook (PreToolUse)** | [plugin/hooks.json](plugin/hooks.json) & [plugin/scripts/pre_tool_check.py](plugin/scripts/pre_tool_check.py) | **Pre-Tool Execution** | Matches tool calls against pattern `delete_task\|run_command`. Validates safety policy; can `allow`, `deny`, or prompt for user approval. |
| **9** | **MCP Tools & Resources** | FastMCP server via [plugin/mcp_config.json](plugin/mcp_config.json) | **Tool Invocation** | Tool call `list_tasks(status="todo")` is dispatched to the FastMCP server over HTTP streamable transport and returns task records. |
| **10** | **Lifecycle Hook (PostToolUse)** | [plugin/hooks.json](plugin/hooks.json) & [plugin/scripts/post_tool_audit.py](plugin/scripts/post_tool_audit.py) | **Post-Tool Execution** | Runs on `*` (all tools). Logs tool name, input arguments, execution duration, and outcome to an audit file. |
| **11** | **Lifecycle Hook (Stop)** | [plugin/hooks.json](plugin/hooks.json) & [plugin/scripts/stop_checker.py](plugin/scripts/stop_checker.py) | **Termination** | Triggered when the agent decides to stop calling tools. Verifies completion criteria (e.g. no unresolved errors) before final response delivery. |
| **12** | **Response Delivery** | Chat UI / CLI output | **Turn Completion** | Structured triage report (blockers, priority items, assignment suggestions) is presented to the user. |

---

#### Core Execution Principles

1. **Progressive Disclosure**: Full runbooks ([`SKILL.md`](plugin/skills/incident-triage/SKILL.md)) are not dumped into the initial context; only lightweight metadata is loaded until activated on demand.
2. **Rule Primacy**: Workspace rules ([`AGENTS.md`](plugin/rules/AGENTS.md)) take precedence over agent defaults and prompt instructions, preventing unsafe actions (e.g. prohibiting raw cURL commands).
3. **Safety Gates via Hooks**: `PreToolUse` hooks intercept risky operations before they execute, while `Stop` hooks ensure verification runbooks were followed before the agent exits.

</details>

