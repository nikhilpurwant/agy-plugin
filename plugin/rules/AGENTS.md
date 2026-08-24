# TaskTracker Plugin Rules & Guidelines

When working with the TaskTracker application, MCP server, and plugin components, adhere to the following standards:

## 1. Mandatory FastMCP Tool Usage (No Direct cURL / API Calls)
- **ALL** task queries, creations, updates, deletions, and metrics retrievals **MUST** be performed exclusively via the registered **FastMCP Tools**:
  - `list_tasks(status, priority, search)`
  - `get_task(task_id)`
  - `create_task(title, description, priority, status, assignee)`
  - `update_task(task_id, title, description, status, priority, assignee)`
  - `delete_task(task_id)`
  - `get_task_metrics()`
  - `bulk_update_task_status(task_ids, status)`
  - `check_api_health()`
- **STRICT PROHIBITION**: Do **NOT** use `curl`, `wget`, `fetch`, Python scripts, or shell/bash commands (`run_command`) to query or modify tasks against `http://127.0.0.1:5050/api`. Always invoke the FastMCP tools directly.

## 2. Task Lifecycle & State Transitions
- Tasks follow three explicit lifecycle states:
  - `todo`: Initial creation state for unstarted backlog items.
  - `in_progress`: Active development, debugging, or triage in progress.
  - `done`: Verified completed or resolved work.
- Priorities must be one of: `critical`, `high`, `medium`, `low`.
- Whenever a task priority is set to `critical`, ensure an explicit assignee is designated immediately.

## 3. FastMCP Tool Execution Best Practices
- When creating or updating tasks via MCP tools (`create_task`, `update_task`), ensure clear, descriptive titles and concise summaries.
- Before proposing the deletion of any task, verify whether the task is referenced by other open issues or if its status can simply be transitioned to `done`.
- Use `get_task_metrics()` to check sprint health, completion percentage, and high-priority blocker counts before and after bulk operations.

## 4. UI Design Rules
- Keep UI lightweight and accessible. Use Bootstrap 5 semantic classes without custom overriding CSS.
- Keep dynamic interactions driven by vanilla JavaScript `fetch` calls against the REST API.
