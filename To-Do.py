import json
from datetime import datetime, timedelta
import subprocess, platform
from weather_api import get_weather

def clear():
    # Clear the console screen
    if platform.system() == "Windows":
        if platform.release() in {"10", "11"}:
            subprocess.run("", shell=True)  # Needed to fix a bug regarding Windows 10; not sure about Windows 11
            print("\033c", end="")
        else:
            subprocess.run(["cls"])
    else:  # Linux and Mac
        print("\033c", end="")

def load_lists(file_path):
    # Load to-do lists from a JSON file
    try:
        with open(file_path, 'r') as file:
            lists = json.load(file)
            # Ensure all tasks have the necessary fields
            for list_name, todo_list in lists.items():
                for todo in todo_list:
                    todo.setdefault("due_date", None)
                    todo.setdefault("priority", None)
                    todo.setdefault("completed", False)
                    todo.setdefault("subtasks", [])
            return lists
    except FileNotFoundError:
        return {}

def save_lists(file_path, lists):
    # Save to-do lists to a JSON file
    with open(file_path, 'w') as file:
        json.dump(lists, file, indent=4)

def load_todo_list(lists, list_name):
    # Load a specific to-do list by name
    return lists.get(list_name, [])

def save_todo_list(lists, list_name, todo_list):
    # Save a specific to-do list by name
    lists[list_name] = todo_list

def add_todo(todo_list, item, due_date=None, priority=None, parent_index=None):
    # Add a new to-do item or subtask
    clear()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_todo = {"item": item, "timestamp": timestamp, "completed": False, "due_date": due_date, "priority": priority, "subtasks": []}
    if parent_index is not None:
        todo_list[parent_index - 1]["subtasks"].append(new_todo)
    else:
        todo_list.append(new_todo)

def remove_todo(todo_list, index, parent_index=None):
    # Remove a to-do item or subtask by index
    clear()
    if parent_index is not None:
        if 1 <= index <= len(todo_list[parent_index - 1]["subtasks"]):
            removed_item = todo_list[parent_index - 1]["subtasks"].pop(index - 1)
            print(f"Removed: {removed_item['item']} - {removed_item['timestamp']}")
        else:
            print("Invalid index. Please try again.")
    else:
        if 1 <= index <= len(todo_list):
            removed_item = todo_list.pop(index - 1)
            print(f"Removed: {removed_item['item']} - {removed_item['timestamp']}")
        else:
            print("Invalid index. Please try again.")

def mark_completed(todo_list, index, parent_index=None):
    # Mark a to-do item or subtask as completed by index
    clear()
    if parent_index is not None:
        if 1 <= index <= len(todo_list[parent_index - 1]["subtasks"]):
            todo_list[parent_index - 1]["subtasks"][index - 1]["completed"] = True
            todo_list[parent_index - 1]["subtasks"][index - 1]["due_date"] = None  # Remove due date when marked as complete
            todo_list[parent_index - 1]["subtasks"][index - 1]["priority"] = None  # Remove priority when marked as complete
            print(f"Marked as completed: {todo_list[parent_index - 1]['subtasks'][index - 1]['item']} - {todo_list[parent_index - 1]['subtasks'][index - 1]['timestamp']}")
        else:
            print("Invalid index. Please try again.")
    else:
        if 1 <= index <= len(todo_list):
            todo_list[index - 1]["completed"] = True
            todo_list[index - 1]["due_date"] = None  # Remove due date when marked as complete
            todo_list[index - 1]["priority"] = None  # Remove priority when marked as complete
            print(f"Marked as completed: {todo_list[index - 1]['item']} - {todo_list[index - 1]['timestamp']}")
        else:
            print("Invalid index. Please try again.")

def display_todo_list(todo_list):
    # Display the to-do list with sorting and formatting
    clear()
    # Sort tasks by priority (Highest first)
    priority_order = {"H": 1, "M": 2, "L": 3}
    todo_list.sort(key=lambda x: (priority_order.get(x["priority"], 4), x["completed"]))

    for idx, todo in enumerate(todo_list, start=1):
        item_text = f"{todo['item']} - {todo['timestamp']}"
        if todo["completed"]:
            item_text = f"\033[9m{item_text}\033[0m"  # Strikethrough effect
            print(f"  {idx}. [✓] {item_text}")
        else:
            priority_text = f"[{todo['priority']}] " if todo['priority'] else ""
            due_date_text = f" (Due: {todo['due_date']})" if todo['due_date'] else ""
            percentage_complete = calculate_percentage_completed(todo)
            print(f"  {idx}. {priority_text}{item_text}{due_date_text} ({percentage_complete:.0f}% complete)")

        # Sort subtasks by priority (Highest first)
        todo["subtasks"].sort(key=lambda x: (priority_order.get(x["priority"], 4), x["completed"]))

        # Display subtasks
        for sub_idx, subtask in enumerate(todo["subtasks"], start=1):
            subtask_text = f"{subtask['item']} - {subtask['timestamp']}"
            if subtask["completed"]:
                subtask_text = f"\033[9m{subtask_text}\033[0m"  # Strikethrough effect
                print(f"    {idx}{chr(96 + sub_idx)}. [✓] {subtask_text}")
            else:
                subtask_priority_text = f"[{subtask['priority']}] " if subtask['priority'] else ""
                subtask_due_date_text = f" (Due: {subtask['due_date']})" if subtask['due_date'] else ""
                print(f"    {idx}{chr(96 + sub_idx)}. {subtask_priority_text}{subtask_text}{subtask_due_date_text}")

def remove_list(lists, list_name):
    # Remove a to-do list by name
    if list_name in lists:
        del lists[list_name]
        print(f"List '{list_name}' removed.")
    else:
        print(f"List '{list_name}' not found.")

def check_reminders(lists):
    # Check for reminders based on due dates
    now = datetime.now()
    reminders = []
    for list_name, todo_list in lists.items():
        for todo in todo_list:
            if todo["due_date"] and not todo["completed"]:
                due_date = datetime.strptime(todo["due_date"], "%Y-%m-%d")
                if due_date.date() == now.date():
                    reminders.append(f"Reminder: {todo['item']} in list '{list_name}' is due today!")
                elif due_date.date() == (now + timedelta(days=1)).date():
                    reminders.append(f"Reminder: {todo['item']} in list '{list_name}' is due tomorrow!")
            for subtask in todo["subtasks"]:
                if subtask["due_date"] and not subtask["completed"]:
                    due_date = datetime.strptime(subtask["due_date"], "%Y-%m-%d")
                    if due_date.date() == now.date():
                        reminders.append(f"Reminder: {subtask['item']} in list '{list_name}' is due today!")
                    elif due_date.date() == (now + timedelta(days=1)).date():
                        reminders.append(f"Reminder: {subtask['item']} in list '{list_name}' is due tomorrow!")
    return reminders

def search_tasks(lists, keyword):
    # Search for tasks containing a specific keyword
    results = []
    for list_name, todo_list in lists.items():
        for idx, todo in enumerate(todo_list, start=1):
            if keyword.lower() in todo["item"].lower():
                results.append((list_name, idx, todo))
            for sub_idx, subtask in enumerate(todo["subtasks"], start=1):
                if keyword.lower() in subtask["item"].lower():
                    results.append((list_name, f"{idx}{chr(96 + sub_idx)}", subtask))
    return results

def filter_tasks(lists, status):
    # Filter tasks by completion status
    results = []
    for list_name, todo_list in lists.items():
        for idx, todo in enumerate(todo_list, start=1):
            if todo["completed"] == status:
                results.append((list_name, idx, todo))
            for sub_idx, subtask in enumerate(todo["subtasks"], start=1):
                if subtask["completed"] == status:
                    results.append((list_name, f"{idx}{chr(96 + sub_idx)}", subtask))
    return results

def calculate_percentage_completed(todo):
    # Calculate the percentage of completed subtasks
    if not todo["subtasks"]:
        return 0
    completed_subtasks = sum(1 for subtask in todo["subtasks"] if subtask["completed"])
    return (completed_subtasks / len(todo["subtasks"])) * 100

def display_weather(city):
    # Display weather information for a specific city
    weather_data = get_weather(city)
    if weather_data:
        main = weather_data['main']
        weather = weather_data['weather'][0]
        print(f"\nWeather in {city}:")
        print(f"Temperature: {main['temp']}°C")
        print(f"Weather: {weather['description']}")
        print(f"Humidity: {main['humidity']}%")
    else:
        print(f"Could not retrieve weather data for {city}.")

def main():
    # Main function to run the to-do list application
    file_path = 'todo_lists.json'
    lists = load_lists(file_path)
    exit_program = False
    show_weather = False

    while not exit_program:
        clear()
        reminders = check_reminders(lists)
        for reminder in reminders:
            print(reminder)

        print("\nSelect an option:")
        print("  1. Select a to-do list")
        print("  2. Search tasks")
        print("  3. Filter tasks")
        print("  4. Create a new list")
        print("  5. Remove a list")
        print("  6. Weather")
        print("  7. Settings")
        print("  8. Exit")

        choice = input(">>> ")
        if choice.isdigit():
            choice = int(choice)
            if choice == 1:
                while True:
                    clear()
                    print("Select a to-do list:")
                    for idx, list_name in enumerate(lists.keys(), start=1):
                        print(f"  {idx}. {list_name}")
                    print(f"  {len(lists) + 1}. Go back")

                    choice = input(">>> ")
                    if choice.isdigit():
                        choice = int(choice)
                        if 1 <= choice <= len(lists):
                            list_name = list(lists.keys())[choice - 1]
                            todo_list = load_todo_list(lists, list_name)
                            while True:
                                display_todo_list(todo_list)
                                print("\n  1. Add item\n  2. Remove item\n  3. Mark as completed\n  4. Add subtask\n  5. Save\n  6. Go back to list selection\n")
                                choice = input(">>> ")

                                if choice == '1':
                                    item = input(" Item to add: ")
                                    due_date = input(" Due date (YYYY-MM-DD) (optional): ")
                                    if due_date:
                                        try:
                                            datetime.strptime(due_date, "%Y-%m-%d")
                                        except ValueError:
                                            print("Invalid date format. Please use YYYY-MM-DD.")
                                            continue
                                    priority = input(" Priority (H/M/L) (optional): ").upper()
                                    if priority not in ["H", "M", "L", ""]:
                                        print("Invalid priority. Please use H, M, or L.")
                                        continue
                                    add_todo(todo_list, item, due_date, priority)
                                elif choice == '2':
                                    index = input(" Index to remove (e.g., 1a for subtask): ")
                                    parent_index = None
                                    if len(index) > 1:
                                        parent_index = int(index[0])
                                        index = index[1:]
                                    index = ord(index) - 96
                                    remove_todo(todo_list, index, parent_index)
                                elif choice == '3':
                                    index = input(" Index to mark as completed (e.g., 1a for subtask): ")
                                    parent_index = None
                                    if len(index) > 1:
                                        parent_index = int(index[0])
                                        index = index[1:]
                                    index = ord(index) - 96
                                    mark_completed(todo_list, index, parent_index)
                                elif choice == '4':
                                    parent_index = int(input(" Parent index: "))
                                    item = input(" Subtask to add: ")
                                    due_date = input(" Due date (YYYY-MM-DD) (optional): ")
                                    if due_date:
                                        try:
                                            datetime.strptime(due_date, "%Y-%m-%d")
                                        except ValueError:
                                            print("Invalid date format. Please use YYYY-MM-DD.")
                                            continue
                                    priority = input(" Priority (H/M/L) (optional): ").upper()
                                    if priority not in ["H", "M", "L", ""]:
                                        print("Invalid priority. Please use H, M, or L.")
                                        continue
                                    add_todo(todo_list, item, due_date, priority, parent_index)
                                elif choice == '5':
                                    save_todo_list(lists, list_name, todo_list)
                                    save_lists(file_path, lists)
                                    print("List saved.")
                                elif choice == '6':
                                    save_lists(file_path, lists)
                                    break  # Go back to list selection menu
                                else:
                                    print("Invalid choice. Please input again.")
                        elif choice == len(lists) + 1:
                            break  # Go back to main menu
                        else:
                            print("Invalid choice. Please try again.")
                    else:
                        print("Invalid choice. Please try again.")
            elif choice == 2:
                keyword = input("Enter keyword to search: ")
                results = search_tasks(lists, keyword)
                clear()
                if results:
                    print("Search results:")
                    for list_name, index, task in results:
                        item_text = f"{task['item']} - {task['timestamp']}"
                        if task["completed"]:
                            item_text = f"\033[9m{item_text}\033[0m"  # Strikethrough effect
                            print(f"  {index}. [✓] {item_text} (List: {list_name})")
                        else:
                            priority_text = f"[{task['priority']}] " if task['priority'] else ""
                            due_date_text = f" (Due: {task['due_date']})" if task['due_date'] else ""
                            percentage_complete = calculate_percentage_completed(task)
                            if index[-1].isalpha():  # If it's a subtask
                                print(f"  {index}. {priority_text}[SUB] {item_text}{due_date_text} ({percentage_complete:.0f}% complete) (List: {list_name})")
                            else:
                                print(f"  {index}. {priority_text}{item_text}{due_date_text} ({percentage_complete:.0f}% complete) (List: {list_name})")
                else:
                    print("No tasks found.")
                input("Press Enter to continue...")
            elif choice == 3:
                status = input("Filter by status (C for completed, P for pending): ").upper()
                if status == "C":
                    results = filter_tasks(lists, True)
                elif status == "P":
                    results = filter_tasks(lists, False)
                else:
                    print("Invalid response. Please use C or P.")
                    continue

                clear()
                if results:
                    print("Filtered results:")
                    for list_name, index, task in results:
                        item_text = f"{task['item']} - {task['timestamp']}"
                        if task["completed"]:
                            item_text = f"\033[9m{item_text}\033[0m"  # Strikethrough effect
                            print(f"  {index}. [✓] {item_text} (List: {list_name})")
                        else:
                            priority_text = f"[{task['priority']}] " if task['priority'] else ""
                            due_date_text = f" (Due: {task['due_date']})" if task['due_date'] else ""
                            percentage_complete = calculate_percentage_completed(task)
                            if index[-1].isalpha():  # If it's a subtask
                                print(f"  {index}. {priority_text}[SUB] {item_text}{due_date_text} ({percentage_complete:.0f}% complete) (List: {list_name})")
                            else:
                                print(f"  {index}. {priority_text}{item_text}{due_date_text} ({percentage_complete:.0f}% complete) (List: {list_name})")
                else:
                    print("No tasks found.")
                input("Press Enter to continue...")
            elif choice == 4:
                list_name = input("Enter the name of the new list: ")
                todo_list = []
                save_todo_list(lists, list_name, todo_list)
            elif choice == 5:
                list_name = input("Enter the name of the list to remove: ")
                remove_list(lists, list_name)
                save_lists(file_path, lists)
            elif choice == 6:
                while True:
                    clear()
                    print("Weather Forecast")
                    city = input("Enter city for weather forecast: ")
                    display_weather(city)
                    print("\n  1. Check another city\n  2. Go back to main menu")
                    choice = input(">>> ")
                    if choice == '2':
                        break
            elif choice == 7:
                while True:
                    clear()
                    print("Settings:")
                    print("  1. Go back to main menu")
                    choice = input(">>> ")
                    if choice == '1':
                        break
                    elif choice == '2':
                        break
            elif choice == 8:
                exit_program = True
            else:
                print("Invalid choice. Please try again.")
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()