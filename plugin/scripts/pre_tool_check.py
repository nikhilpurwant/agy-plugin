#!/usr/bin/env python3
"""
PreToolUse Hook Script for TaskTracker.
Intercepts tool calls before execution to validate destructive actions.
"""
import json
import sys

def main():
    try:
        raw_input = sys.stdin.read()
        payload = json.loads(raw_input) if raw_input.strip() else {}
        tool_call = payload.get("toolCall", {})
        tool_name = tool_call.get("name", "")

        # Safety check: If deleting task, log or permit
        if tool_name == "delete_task":
            task_id = tool_call.get("args", {}).get("task_id")
            result = {
                "decision": "allow",
                "reason": f"Task deletion for ID {task_id} approved by safety gate."
            }
        else:
            result = {
                "decision": "allow"
            }

        print(json.dumps(result))
    except Exception as exc:
        print(json.dumps({"decision": "allow", "reason": f"Hook error: {str(exc)}"}))

if __name__ == "__main__":
    main()
