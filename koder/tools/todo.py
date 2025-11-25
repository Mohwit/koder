ALLOWED_STATUSES = {"pending", "in_progress", "completed"}


def _normalize_item(item: object) -> dict:
    """Normalize a single todo item into a simple dict with 'name' and 'status'."""
    if isinstance(item, str):
        return {"name": item, "status": "pending"}

    if isinstance(item, dict):
        name = item.get("name")
        if not name:
            # Fallback to 'description' if provided, else string-cast the dict
            name = item.get("description") or str(item)
        status = item.get("status", "pending")
        if status not in ALLOWED_STATUSES:
            status = "pending"
        return {"name": name, "status": status}

    # Unknown type, stringify as a name
    return {"name": str(item), "status": "pending"}


def create_todo_list(task_description: str, list_of_items: list) -> dict:
    """Create a todo list using plain JSON-compatible structures."""
    normalized_items = [_normalize_item(item) for item in list_of_items]
    return {"task_description": task_description, "items": normalized_items}


def update_todo_list(task_description: str, list_of_items: list) -> dict:
    """Update a todo list using plain JSON-compatible structures."""
    normalized_items = [_normalize_item(item) for item in list_of_items]
    return {"task_description": task_description, "items": normalized_items}
