---
name: task-operations
description: >-
  Rules and procedural runbooks for managing tasks in TaskTracker exclusively via FastMCP tools. Use this skill whenever the user asks to create, list, filter, update, assign, or delete tasks, or review project KPIs.
---

# Task Operations Skill

This skill provides standard operating procedures for interacting with TaskTracker **exclusively through the FastMCP server tools**.

> [!IMPORTANT]
> **Do NOT use `curl`, shell commands, or direct HTTP calls to interact with the backend API.**
> Always invoke the registered FastMCP tools directly.

## Workflow Procedures

### 1. Listing & Filtering Tasks
- To list all tasks: Invoke the FastMCP tool `list_tasks()`.
- To filter by status (`todo`, `in_progress`, `done`): Call `list_tasks(status="in_progress")`.
- To filter by priority (`low`, `medium`, `high`, `critical`): Call `list_tasks(priority="critical")`.
- To search by keyword: Call `list_tasks(search="pipeline")`.

### 2. Creating New Tasks
- Invoke the FastMCP tool `create_task(title=..., description=..., priority=..., status="todo", assignee=...)`.
- Ensure `title` is clear and concise.
- Set appropriate priority:
  - `critical`: Production outage, blocking release, critical bug.
  - `high`: Major feature blocker or significant bug.
  - `medium`: Standard sprint user story or task.
  - `low`: Minor improvement, cosmetic fix, or technical debt cleanup.

### 3. Updating Tasks
- Invoke the FastMCP tool `update_task(task_id=..., ...)` with only the modified fields.
- When starting work: Call `update_task(task_id=..., status="in_progress", assignee=...)`.
- When completing work: Call `update_task(task_id=..., status="done")`.

### 4. Reviewing Metrics & KPIs
- Invoke the FastMCP tool `get_task_metrics()` to get overall project health, total tasks, count by status, and completion rate.
- Invoke `check_api_health()` if verifying connectivity.

## Error Handling
- If the FastMCP tool returns a connection error: Verify that the FastMCP server is running (`cd mcp && uv run server.py --transport http --port 8080`) and connected to the Flask app (`http://127.0.0.1:5050`).
- If the tool returns an authentication error: Verify `API_KEY` in `.env`.
