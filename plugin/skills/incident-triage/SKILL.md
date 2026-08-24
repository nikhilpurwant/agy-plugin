---
name: incident-triage
description: >-
  Procedures for triaging urgent bugs, production incidents, and blocker issues in TaskTracker exclusively via FastMCP tools. Use this skill when the user asks to triage bugs, review critical tasks, find unassigned blockers, or perform incident retrospectives.
---

# Incident & Bug Triage Skill

This runbook guides agents through triaging urgent incidents and critical bugs in TaskTracker **exclusively via FastMCP tools**.

> [!IMPORTANT]
> **Do NOT use `curl`, shell commands, or direct HTTP calls to interact with the backend API.**
> Always invoke the registered FastMCP tools directly.

## Step-by-Step Triage Runbook

### Step 1: Scan for Critical & High-Priority Blockers
1. Invoke FastMCP tool `list_tasks(priority="critical")` to retrieve all critical items.
2. Invoke FastMCP tool `list_tasks(priority="high")` to retrieve all high priority items.
3. Identify any tasks that are currently `status="todo"` or have `assignee="unassigned"`.

### Step 2: Formulate Action Plan
1. For each unassigned critical task:
   - Propose an immediate assignee based on expertise.
   - Transition status to `in_progress` by invoking `update_task(task_id=..., status="in_progress", assignee=...)`.
2. If dependencies exist between tasks, document the resolution order.

### Step 3: Verify Resolution
1. When an incident fix is ready, verify the fix.
2. Invoke FastMCP tool `update_task(task_id=..., status="done")`.
3. Invoke FastMCP tool `get_task_metrics()` to confirm blocker count is 0 and compute new completion rate.

## Presentation Template
Present triage results using this format:

```markdown
### 🚨 Incident & Blocker Triage Report
- **Critical Tasks Open**: X
- **High-Priority Tasks Open**: Y
- **Unassigned Urgent Tasks**: Z

#### Priority Action Items:
1. **[CRITICAL] #ID Title** → Assigned to: `@user` | Status: `in_progress`
2. **[HIGH] #ID Title** → Assigned to: `@user` | Status: `todo`
```
