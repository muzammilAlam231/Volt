-- ⚡ Volt v2.0 - Full Demo: Todo App (OOP + all features)

class TodoItem {
    func init(title, priority = "normal") {
        set this.title = title
        set this.done = false
        set this.priority = priority
    }

    func complete() {
        set this.done = true
    }

    func toString() {
        set status = "[x]"
        if not this.done {
            set status = "[ ]"
        }
        return f"{status} {this.title} ({this.priority})"
    }
}

class TodoList {
    func init(name) {
        set this.name = name
        set this.items = []
    }

    func add(title, priority = "normal") {
        set item = new TodoItem(title, priority)
        this.items.push(item)
        return item
    }

    func completeByIndex(index) {
        if index < 0 or index >= this.items.length {
            throw f"Invalid index: {index}"
        }
        this.items[index].complete()
    }

    func pending() {
        return this.items.filter((item) => not item.done)
    }

    func completed() {
        return this.items.filter((item) => item.done)
    }

    func display() {
        show f"=== {this.name} ==="
        if this.items.isEmpty() {
            show "  (empty)"
            return null
        }
        for i, item in this.items {
            show f"  {i}. {item}"
        }
        set pendingCount = this.pending().length()
        set doneCount = this.completed().length()
        show "  ---"
        show f"  {doneCount} done, {pendingCount} pending"
    }
}

-- Create and use the todo list
set todos = new TodoList("My Tasks")

todos.add("Learn Volt", "high")
todos.add("Build a project")
todos.add("Write tests", "high")
todos.add("Deploy to production")
todos.add("Take a break", "low")

todos.display()

show ""
show "Completing tasks 0 and 2..."
todos.completeByIndex(0)
todos.completeByIndex(2)

show ""
todos.display()

show ""
show "High priority pending:"
set pending = todos.pending()
for item in pending {
    if item.priority == "high" {
        show f"  ⚡ {item.title}"
    }
}
