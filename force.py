import os
import datetime

TODO_FILE = "todo_list.txt"

# Function to initialize the file if not exists
def initialize_file():
    if not os.path.exists(TODO_FILE):
        with open(TODO_FILE, 'w') as f:
            f.write("")

# Function to read all tasks from file
def read_tasks():
    with open(TODO_FILE, 'r') as f:
        lines = f.readlines()
    tasks = [line.strip().split('|') for line in lines if line.strip()]
    return tasks

# Function to write all tasks to file
def write_tasks(tasks):
    with open(TODO_FILE, 'w') as f:
        for task in tasks:
            f.write('|'.join(task) + '\n')

# Function to add a task
def add_task():
    title = input("Enter task title: ")
    description = input("Enter description: ")
    due_date = input("Enter due date (YYYY-MM-DD): ")
    created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tasks = read_tasks()
    tasks.append([title, description, due_date, created_at, "Pending"])
    write_tasks(tasks)
    print("✅ Task added successfully!")

# Function to view tasks
def view_tasks():
    tasks = read_tasks()
    if not tasks:
        print("🚫 No tasks found.")
        return
    print("\n📋 To-Do List:")
    print("=" * 50)
    for i, task in enumerate(tasks):
        print(f"{i+1}. Title      : {task[0]}")
        print(f"   Description: {task[1]}")
        print(f"   Due Date   : {task[2]}")
        print(f"   Created At : {task[3]}")
        print(f"   Status     : {task[4]}")
        print("-" * 50)

# Function to mark task as complete
def mark_task_complete():
    tasks = read_tasks()
    view_tasks()
    try:
        index = int(input("Enter task number to mark complete: ")) - 1
        if 0 <= index < len(tasks):
            tasks[index][4] = "Completed"
            write_tasks(tasks)
            print("✅ Task marked as completed!")
        else:
            print("❌ Invalid task number.")
    except ValueError:
        print("❌ Please enter a valid number.")

# Function to delete a task
def delete_task():
    tasks = read_tasks()
    view_tasks()
    try:
        index = int(input("Enter task number to delete: ")) - 1
        if 0 <= index < len(tasks):
            del tasks[index]
            write_tasks(tasks)
            print("🗑️ Task deleted successfully!")
        else:
            print("❌ Invalid task number.")
    except ValueError:
        print("❌ Please enter a valid number.")

# Function to search tasks by keyword
def search_task():
    keyword = input("Enter keyword to search: ").lower()
    tasks = read_tasks()
    found = False
    print("\n🔍 Search Results:")
    print("=" * 50)
    for i, task in enumerate(tasks):
        if keyword in task[0].lower() or keyword in task[1].lower():
            print(f"{i+1}. Title      : {task[0]}")
            print(f"   Description: {task[1]}")
            print(f"   Due Date   : {task[2]}")
            print(f"   Created At : {task[3]}")
            print(f"   Status     : {task[4]}")
            print("-" * 50)
            found = True
    if not found:
        print("🚫 No matching tasks found.")

# Function to show menu
def show_menu():
    print("\n===== 🧠 TO-DO LIST MANAGER =====")
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Mark Task as Completed")
    print("4. Delete Task")
    print("5. Search Task")
    print("6. Exit")

# Main Program
def main():
    initialize_file()
    while True:
        show_menu()
        choice = input("Choose an option (1-6): ")
        if choice == '1':
            add_task()
        elif choice == '2':
            view_tasks()
        elif choice == '3':
            mark_task_complete()
        elif choice == '4':
            delete_task()
        elif choice == '5':
            search_task()
        elif choice == '6':
            print("👋 Exiting... Have a nice day!")
            break
        else:
            print("❌ Invalid choice. Please choose from 1 to 6.")

# Run the app
if __name__ == "__main__":
    main()
