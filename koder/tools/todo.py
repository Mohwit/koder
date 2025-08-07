""" 
This module provides tools for managing todo lists with visual enhancements.
"""

from enum import Enum
import uuid

# Visual constants for better UI
STATUS_ICONS = {
    "pending": "⏳",
    "in_progress": "🔄", 
    "completed": "✅"
}

HEADER_ICONS = {
    "create": "📝",
    "list": "📋",
    "update": "🔄",
    "next": "➡️"
}

class TodoStatus(Enum):
    """
    The status of a todo item.
    """
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class TodoItem:
    """
    A todo item.
    """
    def __init__(self, description: str, item_id: str = None, state: TodoStatus = TodoStatus.PENDING):
        self.id = item_id if item_id else str(uuid.uuid4())
        self.description = description
        self.state = state
    
    def to_dict(self):
        """
        Convert the todo item to a dictionary with visual enhancements.
        """
        return {
            "id": self.id,
            "description": self.description,
            "state": self.state.value,
            "visual_status": f"{STATUS_ICONS.get(self.state.value, '❓')} {self.description}",
        }
        
class TodoList:
    """
    A todo list.
    """
    def __init__(self, name: str, items: list[TodoItem] = None):
        self.name = name
        self.items = items if items else []
    
    def get_item(self, item_id: str) -> TodoItem:
        """
        Get a todo item by id.
        """
        for todo_item in self.items:
            if todo_item.id == item_id:
                return todo_item
        return None
    
    def to_dict(self):
        """
        Convert the todo list to a dictionary with visual enhancements.
        """
        completed_count = sum(1 for item in self.items if item.state == TodoStatus.COMPLETED)
        total_count = len(self.items)
        progress_bar = self._generate_progress_bar(completed_count, total_count)
        
        return {
            "name": self.name,
            "items": [item.to_dict() for item in self.items],
            "progress": f"{completed_count}/{total_count} completed",
            "visual_progress": progress_bar,
            "visual_header": f"📋 {self.name}"
        }
    
    def _generate_progress_bar(self, completed: int, total: int, width: int = 20) -> str:
        """Generate a visual progress bar."""
        if total == 0:
            return "▱" * width
        
        filled = int((completed / total) * width)
        bar = "▰" * filled + "▱" * (width - filled)
        percentage = int((completed / total) * 100)
        return f"[{bar}] {percentage}%"
   
# Global variable to store the current todo list
_current_todo_list = None

## tool to create a todo list     
def create_todo_list(task_description: str, items: list[str]) -> dict:
    """
    Create a todo list for a given task with visual feedback.
    """
    global _current_todo_list
    todo_items = [TodoItem(description=item) for item in items]
    _current_todo_list = TodoList(name=task_description, items=todo_items)
    
    result = _current_todo_list.to_dict()
    # Add creation success message
    result["success_message"] = f"✨ Successfully created todo list '{task_description}' with {len(items)} items"
    result["visual_summary"] = f"{HEADER_ICONS['create']} Created: {len(items)} tasks ready to go!"
    
    return result

def get_current_todo_list() -> dict:
    """
    Get the current todo list with visual enhancements.
    """
    if _current_todo_list is None:
        return {
            "error": "❌ No todo list exists. Create one first.",
            "visual_message": f"{HEADER_ICONS['list']} No active todo list found"
        }
    
    result = _current_todo_list.to_dict()
    result["visual_message"] = f"{HEADER_ICONS['list']} Current todo list status"
    return result

def update_todo_item_state(item_id: str, state: TodoStatus) -> dict:
    """
    Update the state of a todo item with visual feedback.
    """
    global _current_todo_list
    if _current_todo_list is None:
        return {
            "error": "❌ No todo list exists. Create one first.",
            "visual_message": f"{HEADER_ICONS['update']} Update failed - no active list"
        }
    
    todo_item = _current_todo_list.get_item(item_id)
    if todo_item is None:
        return {
            "error": f"❌ Todo item with id '{item_id}' not found.",
            "visual_message": f"{HEADER_ICONS['update']} Update failed - item not found"
        }
    
    old_state = todo_item.state.value
    todo_item.state = state
    
    result = _current_todo_list.to_dict()
    result["update_message"] = f"🔄 Updated task: {todo_item.description}"
    result["state_change"] = f"{STATUS_ICONS.get(old_state, '❓')} → {STATUS_ICONS.get(state.value, '❓')} ({old_state} → {state.value})"
    result["visual_message"] = f"{HEADER_ICONS['update']} Task status updated successfully"
    
    return result

def clear_todo_list() -> dict:
    """
    Clear the current todo list and reset state.
    """
    global _current_todo_list
    if _current_todo_list is None:
        return {
            "message": "❌ No todo list to clear.",
            "visual_message": "📝 No active todo list found"
        }
    
    old_name = _current_todo_list.name
    _current_todo_list = None
    
    return {
        "message": f"✅ Todo list '{old_name}' has been cleared.",
        "visual_message": "🗑️ Todo list cleared successfully",
        "success": True
    }

def get_next_task() -> str:
    """
    Get the next task to be done with visual indicators.
    """
    if _current_todo_list is None:
        return f"❌ No todo list exists. Create one first. {HEADER_ICONS['next']}"
    
    # Check for pending tasks
    for todo_item in _current_todo_list.items:
        if todo_item.state == TodoStatus.PENDING:
            return f"{HEADER_ICONS['next']} Next task: {STATUS_ICONS['pending']} {todo_item.description} (ID: {todo_item.id})"
    
    # Check completion status
    completed_count = sum(1 for item in _current_todo_list.items if item.state == TodoStatus.COMPLETED)
    in_progress_count = sum(1 for item in _current_todo_list.items if item.state == TodoStatus.IN_PROGRESS)
    total_count = len(_current_todo_list.items)
    
    if completed_count == total_count and total_count > 0:
        return f"🎉 ALL TASKS COMPLETED! Great job finishing '{_current_todo_list.name}' - No more work needed!"
    elif in_progress_count > 0:
        return f"⚠️ No pending tasks, but {in_progress_count} task(s) still in progress. Consider marking them as completed."
    else:
        return f"⚠️ No pending tasks found. Total: {completed_count}/{total_count} completed. {HEADER_ICONS['next']}"


if __name__ == "__main__":
    # Example usage of the todo list tools with visual enhancements
    print("🎯 === Todo List Tools Demo with Visual Enhancements ===\n")
    
    # 1. Create a todo list
    print("1️⃣ Creating a visual todo list...")
    task_items = [
        "Set up project structure",
        "Write initial code", 
        "Add tests",
        "Write documentation",
        "Deploy to production"
    ]
    result = create_todo_list("Build Web Application", task_items)
    print(f"✨ {result.get('success_message', '')}")
    print(f"📊 Progress: {result.get('visual_progress', '')}")
    print(f"📋 Visual items:")
    for item in result["items"]:
        print(f"   {item['visual_status']}")
    print()
    
    # 2. Get current todo list
    print("2️⃣ Getting current todo list with visuals...")
    current_list = get_current_todo_list()
    print(f"{current_list.get('visual_message', '')}")
    print(f"📊 {current_list.get('visual_progress', '')}")
    print()
    
    # 3. Get next task
    print("3️⃣ Getting next task...")
    next_task = get_next_task()
    print(f"{next_task}\n")
    
    # 4. Update todo item state
    print("4️⃣ Updating first item to 'in_progress'...")
    first_item_id = current_list["items"][0]["id"]
    updated_list = update_todo_item_state(first_item_id, TodoStatus.IN_PROGRESS)
    print(f"{updated_list.get('update_message', '')}")
    print(f"🔄 State change: {updated_list.get('state_change', '')}")
    print(f"📊 New progress: {updated_list.get('visual_progress', '')}")
    print()
    
    # 5. Complete the first item
    print("5️⃣ Completing first item...")
    completed_list = update_todo_item_state(first_item_id, TodoStatus.COMPLETED)
    print(f"{completed_list.get('update_message', '')}")
    print(f"🔄 State change: {completed_list.get('state_change', '')}")
    print(f"📊 New progress: {completed_list.get('visual_progress', '')}")
    print()
    
    # 6. Get next task again
    print("6️⃣ Getting next task after completion...")
    next_task = get_next_task()
    print(f"{next_task}\n")
    
    # 7. Complete all tasks to demonstrate visual completion
    print("7️⃣ Completing all remaining tasks...")
    for todo_item in completed_list["items"]:
        if todo_item["state"] != "completed":
            result = update_todo_item_state(todo_item["id"], TodoStatus.COMPLETED)
            print(f"   ✅ {result.get('update_message', '')}")
    
    print()
    final_next_task = get_next_task()
    print(f"🏁 Final status: {final_next_task}")
    
    final_list = get_current_todo_list()
    print(f"📊 Final progress: {final_list.get('visual_progress', '')}")
    print(f"🎉 Demo completed! All visual enhancements working perfectly.")