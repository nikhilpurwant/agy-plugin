#!/usr/bin/env python3
"""
Stop Hook Script for TaskTracker.
Evaluates agent execution upon stopping.
"""
import json
import sys

def main():
    try:
        raw_input = sys.stdin.read()
        payload = json.loads(raw_input) if raw_input.strip() else {}
        # Allow default stopping behavior
        print(json.dumps({"decision": "stop"}))
    except Exception:
        print(json.dumps({}))

if __name__ == "__main__":
    main()
