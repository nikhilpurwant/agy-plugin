import argparse
import os
import sys
from typing import Any, Dict, List, Optional

import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP

# Load environment variables
load_dotenv()

APP_API_URL = os.getenv("APP_API_URL", "http://127.0.0.1:5050/api").rstrip("/")
API_KEY = os.getenv("API_KEY", "tasktracker-secret-api-key-2026")
DEFAULT_TRANSPORT = os.getenv("MCP_TRANSPORT", "http")
DEFAULT_HOST = os.getenv("MCP_HOST", "127.0.0.1")
DEFAULT_PORT = int(os.getenv("MCP_PORT", 8080))

# Initialize FastMCP Server
mcp = FastMCP(
    name="TaskTracker MCP Server",
    instructions="MCP Server for managing tasks, issues, and project workflows in TaskTracker via REST API.",
)

# ---------------------------------------------------------------------------
# HTTP Client Helper
# ---------------------------------------------------------------------------
def _get_headers() -> Dict[str, str]:
    """Return standard headers with API Key authentication."""
    return {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _make_request(method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None) -> Any:
    """Execute an HTTP request to the backend Flask API with error handling."""
    url = f"{APP_API_URL}{endpoint}"
    headers = _get_headers()
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data,
            )

            if response.status_code == 401:
                return {"error": "Authentication failed: Invalid or missing API key in MCP server configuration."}

            if response.status_code == 404:
                return {"error": f"Resource not found at {url}"}

            if not response.is_success:
                try:
                    err_json = response.json()
                    return {"error": err_json.get("error", f"HTTP {response.status_code}: {response.text}")}
                except Exception:
                    return {"error": f"HTTP {response.status_code}: {response.text}"}

            return response.json()

    except httpx.ConnectError:
        return {
            "error": f"Failed to connect to TaskTracker App at {APP_API_URL}. Ensure the Flask app is running."
        }
    except Exception as exc:
        return {"error": f"Unexpected error communicating with TaskTracker App: {str(exc)}"}


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------
@mcp.tool(
    name="list_tasks",
    description="List tasks from TaskTracker with optional filtering by status ('todo', 'in_progress', 'done'), priority ('low', 'medium', 'high', 'critical'), or search text."
)
def list_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
) -> Dict[str, Any]:
    """Retrieve tasks with optional filters."""
    params = {}
    if status:
        params["status"] = status
    if priority:
        params["priority"] = priority
    if search:
        params["search"] = search

    return _make_request("GET", "/tasks", params=params)


@mcp.tool(
    name="get_task",
    description="Retrieve a single task by its integer ID."
)
def get_task(task_id: int) -> Dict[str, Any]:
    """Get task details for a given task_id."""
    return _make_request("GET", f"/tasks/{task_id}")


@mcp.tool(
    name="create_task",
    description="Create a new task in TaskTracker with a title, description, priority ('low', 'medium', 'high', 'critical'), and assignee."
)
def create_task(
    title: str,
    description: str = "",
    priority: str = "medium",
    status: str = "todo",
    assignee: str = "unassigned",
) -> Dict[str, Any]:
    """Create a new task."""
    payload = {
        "title": title,
        "description": description,
        "priority": priority,
        "status": status,
        "assignee": assignee,
    }
    return _make_request("POST", "/tasks", json_data=payload)


@mcp.tool(
    name="update_task",
    description="Update an existing task's title, description, status ('todo', 'in_progress', 'done'), priority, or assignee."
)
def update_task(
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assignee: Optional[str] = None,
) -> Dict[str, Any]:
    """Update fields on an existing task."""
    payload: Dict[str, Any] = {}
    if title is not None:
        payload["title"] = title
    if description is not None:
        payload["description"] = description
    if status is not None:
        payload["status"] = status
    if priority is not None:
        payload["priority"] = priority
    if assignee is not None:
        payload["assignee"] = assignee

    if not payload:
        return {"error": "No update fields provided."}

    return _make_request("PUT", f"/tasks/{task_id}", json_data=payload)


@mcp.tool(
    name="delete_task",
    description="Delete a task from TaskTracker by its ID."
)
def delete_task(task_id: int) -> Dict[str, Any]:
    """Delete a task."""
    return _make_request("DELETE", f"/tasks/{task_id}")


@mcp.tool(
    name="get_task_metrics",
    description="Get aggregated TaskTracker metrics including total tasks, breakdown by status, breakdown by priority, and completion percentage."
)
def get_task_metrics() -> Dict[str, Any]:
    """Get project KPI summary statistics."""
    return _make_request("GET", "/tasks/stats")


@mcp.tool(
    name="bulk_update_task_status",
    description="Update status ('todo', 'in_progress', 'done') for multiple tasks simultaneously."
)
def bulk_update_task_status(task_ids: List[int], status: str) -> Dict[str, Any]:
    """Update status for multiple tasks."""
    payload = {
        "task_ids": task_ids,
        "status": status,
    }
    return _make_request("POST", "/tasks/bulk-status", json_data=payload)


@mcp.tool(
    name="check_api_health",
    description="Check the connectivity and status of the underlying TaskTracker REST API."
)
def check_api_health() -> Dict[str, Any]:
    """Verify backend Flask API health."""
    return _make_request("GET", "/health")


# ---------------------------------------------------------------------------
# MCP Resources
# ---------------------------------------------------------------------------
@mcp.resource("tasktracker://tasks/summary")
def task_summary_resource() -> str:
    """Resource returning a formatted overview of current tasks and stats."""
    metrics = _make_request("GET", "/tasks/stats")
    tasks_res = _make_request("GET", "/tasks")
    tasks = tasks_res.get("tasks", []) if isinstance(tasks_res, dict) else []

    lines = ["# TaskTracker Live System Overview", ""]
    if "total_tasks" in metrics:
        lines.append(f"**Total Tasks**: {metrics.get('total_tasks')}")
        lines.append(f"**Completion Rate**: {metrics.get('completion_rate_percentage')}%")
        lines.append(f"**By Status**: {metrics.get('by_status')}")
        lines.append(f"**By Priority**: {metrics.get('by_priority')}")
        lines.append("")

    lines.append("## Active Tasks")
    for t in tasks:
        lines.append(f"- **#{t['id']} [{t['priority'].upper()}]** {t['title']} ({t['status']}) - Assignee: {t['assignee']}")

    return "\n".join(lines)


@mcp.resource("tasktracker://tasks/{task_id}")
def task_detail_resource(task_id: int) -> str:
    """Resource returning detailed JSON for a specific task."""
    res = _make_request("GET", f"/tasks/{task_id}")
    if "error" in res:
        return f"Error: {res['error']}"
    t = res.get("task", {})
    return (
        f"# Task #{t.get('id')}: {t.get('title')}\n"
        f"- **Status**: {t.get('status')}\n"
        f"- **Priority**: {t.get('priority')}\n"
        f"- **Assignee**: {t.get('assignee')}\n"
        f"- **Created At**: {t.get('created_at')}\n"
        f"- **Updated At**: {t.get('updated_at')}\n\n"
        f"### Description\n{t.get('description', 'No description.')}\n"
    )


# ---------------------------------------------------------------------------
# MCP Prompts
# ---------------------------------------------------------------------------
@mcp.prompt(name="triage_tasks", description="Analyze open and critical tasks to prioritize sprint blockers.")
def triage_tasks_prompt() -> str:
    """Generate a prompt to triage tasks."""
    return (
        "Please query the TaskTracker MCP server for all tasks with status 'todo' and 'in_progress'. "
        "Highlight any 'critical' or 'high' priority items, check if they have assignees, "
        "and suggest a prioritized resolution order."
    )


@mcp.prompt(name="daily_standup_report", description="Generate a daily standup summary from TaskTracker tasks.")
def daily_standup_prompt() -> str:
    """Generate a daily standup prompt."""
    return (
        "Retrieve current metrics via get_task_metrics and list tasks. "
        "Format a clean daily standup report categorized by: "
        "1. Completed yesterday / Done, 2. Currently In Progress, 3. Blockers or Critical Items, 4. Action Items."
    )


# ---------------------------------------------------------------------------
# Server CLI Entrypoint
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="TaskTracker FastMCP Server")
    parser.add_argument(
        "--transport",
        choices=["http", "streamable-http", "sse", "stdio"],
        default=DEFAULT_TRANSPORT,
        help=f"MCP transport mechanism (default: {DEFAULT_TRANSPORT})"
    )
    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help=f"Host interface to bind HTTP/SSE server (default: {DEFAULT_HOST})"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Port number for HTTP/SSE server (default: {DEFAULT_PORT})"
    )

    args = parser.parse_args()

    transport = args.transport
    if transport in ("http", "streamable-http"):
        print(f"Starting TaskTracker FastMCP server in streamable HTTP mode on http://{args.host}:{args.port}/mcp", file=sys.stderr)
        mcp.run(transport="http", host=args.host, port=args.port)
    elif transport == "sse":
        print(f"Starting TaskTracker FastMCP server in SSE mode on http://{args.host}:{args.port}/sse", file=sys.stderr)
        mcp.run(transport="sse", host=args.host, port=args.port)
    elif transport == "stdio":
        print("Starting TaskTracker FastMCP server in stdio mode", file=sys.stderr)
        mcp.run(transport="stdio")
    else:
        print(f"Unknown transport: {transport}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
