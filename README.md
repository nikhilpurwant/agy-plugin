# TaskTracker — Demo Application, FastMCP Server & Antigravity CLI Plugin

A complete, production-grade reference implementation demonstrating the end-to-end architecture of a **Web Application**, a **FastMCP Server**, and an **Antigravity CLI (`agy`) Plugin** bundling all plugin capabilities: **Skills**, **Agents**, **Commands**, **Hooks**, **Rules**, and **MCP Server Configurations**.

---

## 📐 Architecture Overview

```mermaid
flowchart TD
    subgraph AntigravityCLI["Google Antigravity Platform (CLI & IDE)"]
        PluginManifest["plugin.json (tasktracker)"]
        SlashCmds["commands/tasktracker/*.toml\n(/tasktracker:list, /tasktracker:triage, etc.)"]
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
        AuthSystem["Dual Authentication\n(JWT for UI / API Key for MCP)"]
        RESTAPI["REST API (/api/tasks, /api/auth, /api/tasks/stats)"]
        InMemoryDB["In-Memory Thread-Safe Database"]
        BootstrapUI["Pure Vanilla JS + Bootstrap 5 UI\n(index.html & login.html - No Custom CSS / Jinja)"]
    end

    AntigravityCLI -->|MCP Protocol over HTTP (:8080/mcp)| MCPServer
    MCPServer -->|Authenticated REST Requests with X-API-Key| RESTAPI
    BootstrapUI -->|JWT Bearer Token Requests| RESTAPI
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
