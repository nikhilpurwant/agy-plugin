#!/usr/bin/env python3
"""
PreInvocation Hook Script for TaskTracker.
Injects helpful guidelines or reminders prior to model invocation.
"""
import json
import sys

def main():
    try:
        raw_input = sys.stdin.read()
        payload = json.loads(raw_input) if raw_input.strip() else {}
        
        result = {
            "injectSteps": [
                {
                    "ephemeralMessage": "TaskTracker Plugin active. Use TaskTracker FastMCP tools or commands for task queries and updates."
                }
            ]
        }
        print(json.dumps(result))
    except Exception:
        print(json.dumps({}))

if __name__ == "__main__":
    main()
