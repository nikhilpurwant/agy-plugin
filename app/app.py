import os
import threading
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from dotenv import load_dotenv
from flask import (
    Flask,
    g,
    jsonify,
    request,
    send_from_directory,
)

# Load environment variables
load_dotenv()

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 5050))
DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"

DEMO_USERNAME = os.getenv("DEMO_USERNAME", "admin")
DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "password123")
API_KEY = os.getenv("API_KEY", "tasktracker-secret-api-key-2026")
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-jwt-key-tasktracker-2026")
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", 24))

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.config["SECRET_KEY"] = JWT_SECRET

# ---------------------------------------------------------------------------
# In-Memory Database
# ---------------------------------------------------------------------------
db_lock = threading.Lock()

tasks_db = [
    {
        "id": 1,
        "title": "Set up CI/CD pipeline",
        "description": "Configure GitHub Actions workflow for automated testing and deployment.",
        "status": "done",
        "priority": "high",
        "assignee": "alex.dev",
        "created_at": "2026-08-18T09:00:00Z",
        "updated_at": "2026-08-18T17:30:00Z",
    },
    {
        "id": 2,
        "title": "Implement FastMCP server endpoints",
        "description": "Expose TaskTracker tools and resources over stdio, sse, and streamable-http.",
        "status": "in_progress",
        "priority": "critical",
        "assignee": "admin",
        "created_at": "2026-08-19T08:30:00Z",
        "updated_at": "2026-08-19T10:15:00Z",
    },
    {
        "id": 3,
        "title": "Build Antigravity CLI Plugin",
        "description": "Package slash commands, skills, lifecycle hooks, rules, and subagents.",
        "status": "in_progress",
        "priority": "critical",
        "assignee": "admin",
        "created_at": "2026-08-19T10:00:00Z",
        "updated_at": "2026-08-19T11:45:00Z",
    },
    {
        "id": 4,
        "title": "Write end-to-end integration tests",
        "description": "Cover API key authentication, JWT token generation, and MCP tool execution.",
        "status": "todo",
        "priority": "medium",
        "assignee": "sam.qa",
        "created_at": "2026-08-19T11:00:00Z",
        "updated_at": "2026-08-19T11:00:00Z",
    },
    {
        "id": 5,
        "title": "Draft release documentation and architecture diagram",
        "description": "Document plugin architecture, FastMCP transports, and UI user guide in README.",
        "status": "todo",
        "priority": "low",
        "assignee": "unassigned",
        "created_at": "2026-08-19T11:30:00Z",
        "updated_at": "2026-08-19T11:30:00Z",
    },
]

next_task_id = 6

# ---------------------------------------------------------------------------
# Authentication Helpers & Decorators
# ---------------------------------------------------------------------------
def generate_jwt_token(username: str) -> str:
    """Generate a JWT token for the authenticated user."""
    payload = {
        "sub": username,
        "role": "admin" if username == DEMO_USERNAME else "user",
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def require_auth(f):
    """Decorator to authenticate requests via either JWT token or API Key."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. Check for API Key in X-API-Key header
        api_key_header = request.headers.get("X-API-Key")
        if api_key_header:
            if api_key_header == API_KEY:
                g.user = {"username": "api_client", "role": "admin", "auth_type": "api_key"}
                return f(*args, **kwargs)
            return jsonify({"error": "Invalid API key"}), 401

        # 2. Check for Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Authorization credentials missing. Provide Authorization: Bearer <token> or X-API-Key header."}), 401

        parts = auth_header.split()
        if len(parts) != 2:
            return jsonify({"error": "Invalid Authorization header format. Expected 'Bearer <token>'"}), 401

        scheme, token = parts[0], parts[1]

        # Allow API Key passed via Bearer token
        if token == API_KEY:
            g.user = {"username": "api_client", "role": "admin", "auth_type": "api_key"}
            return f(*args, **kwargs)

        if scheme.lower() != "bearer":
            return jsonify({"error": "Unsupported authorization scheme. Use 'Bearer'"}), 401

        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            g.user = {
                "username": payload.get("sub"),
                "role": payload.get("role", "user"),
                "auth_type": "jwt",
            }
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid authentication token"}), 401

        return f(*args, **kwargs)

    return decorated_function


# ---------------------------------------------------------------------------
# UI Static Routes (No Jinja, Static HTML + JS)
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    """Serve the main single-page application dashboard."""
    return send_from_directory("static", "index.html")


@app.route("/login")
def login_page():
    """Serve the login page."""
    return send_from_directory("static", "login.html")


# ---------------------------------------------------------------------------
# Authentication API
# ---------------------------------------------------------------------------
@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    """Authenticate user with username/password and return JWT token."""
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if username == DEMO_USERNAME and password == DEMO_PASSWORD:
        token = generate_jwt_token(username)
        return jsonify({
            "message": "Authentication successful",
            "token": token,
            "user": {
                "username": username,
                "role": "admin",
            },
        }), 200

    return jsonify({"error": "Invalid username or password"}), 401


@app.route("/api/auth/me", methods=["GET"])
@require_auth
def auth_me():
    """Return the profile of the currently authenticated user/client."""
    return jsonify({
        "user": g.user,
        "authenticated": True,
    }), 200


# ---------------------------------------------------------------------------
# Tasks CRUD API Endpoints
# ---------------------------------------------------------------------------
@app.route("/api/tasks", methods=["GET"])
@require_auth
def list_tasks():
    """List all tasks with optional filtering by status, priority, and search keyword."""
    status_filter = request.args.get("status")
    priority_filter = request.args.get("priority")
    search_filter = request.args.get("search", "").lower()

    with db_lock:
        results = list(tasks_db)

    if status_filter:
        results = [t for t in results if t["status"].lower() == status_filter.lower()]

    if priority_filter:
        results = [t for t in results if t["priority"].lower() == priority_filter.lower()]

    if search_filter:
        results = [
            t for t in results
            if search_filter in t["title"].lower()
            or search_filter in t["description"].lower()
            or search_filter in t["assignee"].lower()
        ]

    return jsonify({
        "tasks": results,
        "count": len(results),
        "total": len(tasks_db),
    }), 200


@app.route("/api/tasks/<int:task_id>", methods=["GET"])
@require_auth
def get_task(task_id: int):
    """Retrieve a single task by ID."""
    with db_lock:
        task = next((t for t in tasks_db if t["id"] == task_id), None)

    if not task:
        return jsonify({"error": f"Task with ID {task_id} not found"}), 404

    return jsonify({"task": task}), 200


@app.route("/api/tasks", methods=["POST"])
@require_auth
def create_task():
    """Create a new task."""
    global next_task_id
    data = request.get_json() or {}

    title = data.get("title", "").strip()
    if not title:
        return jsonify({"error": "Task title is required"}), 400

    description = data.get("description", "").strip()
    status = data.get("status", "todo").lower()
    priority = data.get("priority", "medium").lower()
    assignee = data.get("assignee", "unassigned").strip() or "unassigned"

    valid_statuses = {"todo", "in_progress", "done"}
    valid_priorities = {"low", "medium", "high", "critical"}

    if status not in valid_statuses:
        return jsonify({"error": f"Invalid status '{status}'. Allowed: {list(valid_statuses)}"}), 400

    if priority not in valid_priorities:
        return jsonify({"error": f"Invalid priority '{priority}'. Allowed: {list(valid_priorities)}"}), 400

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    with db_lock:
        new_task = {
            "id": next_task_id,
            "title": title,
            "description": description,
            "status": status,
            "priority": priority,
            "assignee": assignee,
            "created_at": now_iso,
            "updated_at": now_iso,
        }
        next_task_id += 1
        tasks_db.append(new_task)

    return jsonify({"message": "Task created successfully", "task": new_task}), 201


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
@require_auth
def update_task(task_id: int):
    """Update an existing task."""
    data = request.get_json() or {}

    valid_statuses = {"todo", "in_progress", "done"}
    valid_priorities = {"low", "medium", "high", "critical"}

    with db_lock:
        task = next((t for t in tasks_db if t["id"] == task_id), None)
        if not task:
            return jsonify({"error": f"Task with ID {task_id} not found"}), 404

        if "title" in data:
            title = data["title"].strip()
            if not title:
                return jsonify({"error": "Title cannot be empty"}), 400
            task["title"] = title

        if "description" in data:
            task["description"] = data["description"].strip()

        if "status" in data:
            status = data["status"].lower()
            if status not in valid_statuses:
                return jsonify({"error": f"Invalid status '{status}'. Allowed: {list(valid_statuses)}"}), 400
            task["status"] = status

        if "priority" in data:
            priority = data["priority"].lower()
            if priority not in valid_priorities:
                return jsonify({"error": f"Invalid priority '{priority}'. Allowed: {list(valid_priorities)}"}), 400
            task["priority"] = priority

        if "assignee" in data:
            task["assignee"] = data["assignee"].strip() or "unassigned"

        task["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        updated_task = dict(task)

    return jsonify({"message": "Task updated successfully", "task": updated_task}), 200


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
@require_auth
def delete_task(task_id: int):
    """Delete a task by ID."""
    global tasks_db
    with db_lock:
        task = next((t for t in tasks_db if t["id"] == task_id), None)
        if not task:
            return jsonify({"error": f"Task with ID {task_id} not found"}), 404

        tasks_db = [t for t in tasks_db if t["id"] != task_id]

    return jsonify({"message": "Task deleted successfully", "deleted_id": task_id}), 200


@app.route("/api/tasks/stats", methods=["GET"])
@require_auth
def task_stats():
    """Return aggregated KPIs and statistics."""
    with db_lock:
        total = len(tasks_db)
        by_status = {
            "todo": sum(1 for t in tasks_db if t["status"] == "todo"),
            "in_progress": sum(1 for t in tasks_db if t["status"] == "in_progress"),
            "done": sum(1 for t in tasks_db if t["status"] == "done"),
        }
        by_priority = {
            "critical": sum(1 for t in tasks_db if t["priority"] == "critical"),
            "high": sum(1 for t in tasks_db if t["priority"] == "high"),
            "medium": sum(1 for t in tasks_db if t["priority"] == "medium"),
            "low": sum(1 for t in tasks_db if t["priority"] == "low"),
        }

    completion_rate = round((by_status["done"] / total * 100), 1) if total > 0 else 0.0

    return jsonify({
        "total_tasks": total,
        "by_status": by_status,
        "by_priority": by_priority,
        "completion_rate_percentage": completion_rate,
    }), 200


@app.route("/api/tasks/bulk-status", methods=["POST"])
@require_auth
def bulk_status_update():
    """Bulk update the status of multiple tasks."""
    data = request.get_json() or {}
    task_ids = data.get("task_ids", [])
    new_status = data.get("status", "").lower()

    valid_statuses = {"todo", "in_progress", "done"}
    if new_status not in valid_statuses:
        return jsonify({"error": f"Invalid status '{new_status}'. Allowed: {list(valid_statuses)}"}), 400

    if not isinstance(task_ids, list) or not task_ids:
        return jsonify({"error": "task_ids must be a non-empty array of integer IDs"}), 400

    updated_count = 0
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    with db_lock:
        for t in tasks_db:
            if t["id"] in task_ids:
                t["status"] = new_status
                t["updated_at"] = now_iso
                updated_count += 1

    return jsonify({
        "message": f"Updated {updated_count} task(s) to status '{new_status}'",
        "updated_count": updated_count,
    }), 200


# ---------------------------------------------------------------------------
# Health Check Endpoint (Public)
# ---------------------------------------------------------------------------
@app.route("/api/health", methods=["GET"])
def health():
    """Public health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "TaskTracker App",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }), 200


# ---------------------------------------------------------------------------
# Main Entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"Starting TaskTracker Flask App on http://{HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=DEBUG)
