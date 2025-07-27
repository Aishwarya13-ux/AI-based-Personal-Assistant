#!/usr/bin/env python3
"""
Quick Start Script for AI Personal Assistant

This script demonstrates the core concepts without requiring external dependencies.
It's designed to work with just the Python standard library.
"""
import json
import re
import time
from datetime import datetime, timedelta
from pathlib import Path

class QuickAssistant:
    """A simplified version of the AI assistant using only standard library."""
    
    def __init__(self):
        self.tasks = []
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.tasks_file = self.data_dir / "quick_tasks.json"
        self._load_tasks()
    
    def _load_tasks(self):
        """Load tasks from file."""
        if self.tasks_file.exists():
            try:
                with open(self.tasks_file, 'r') as f:
                    self.tasks = json.load(f)
            except:
                self.tasks = []
    
    def _save_tasks(self):
        """Save tasks to file."""
        try:
            with open(self.tasks_file, 'w') as f:
                json.dump(self.tasks, f, indent=2)
        except Exception as e:
            print(f"Error saving tasks: {e}")
    
    def process_command(self, command):
        """Process a text command and return a response."""
        command = command.lower().strip()
        
        # Time commands
        if any(word in command for word in ['time', 'date', 'day']):
            return self._handle_time()
        
        # Task commands
        elif 'add task' in command or 'add:' in command:
            return self._handle_add_task(command)
        
        elif 'list task' in command or 'show task' in command:
            return self._handle_list_tasks()
        
        # Math commands
        elif any(word in command for word in ['calculate', 'math', '+', '-', '*', '/']):
            return self._handle_math(command)
        
        # System info
        elif 'system' in command or 'computer' in command:
            return self._handle_system_info()
        
        # Help command
        elif 'help' in command:
            return self._handle_help()
        
        # Greeting
        elif any(word in command for word in ['hello', 'hi', 'hey']):
            return "Hello! I'm your AI assistant. Type 'help' to see what I can do."
        
        # Goodbye
        elif any(word in command for word in ['bye', 'goodbye', 'quit', 'exit']):
            return "Goodbye! Have a great day!"
        
        # Default response
        else:
            return f"I'm not sure how to help with '{command}'. Type 'help' for available commands."
    
    def _handle_time(self):
        """Handle time and date requests."""
        now = datetime.now()
        return f"Current time: {now.strftime('%A, %B %d, %Y at %I:%M %p')}"
    
    def _handle_add_task(self, command):
        """Handle adding tasks."""
        # Extract task from command
        if 'add task:' in command:
            task_text = command.split('add task:', 1)[1].strip()
        elif 'add:' in command:
            task_text = command.split('add:', 1)[1].strip()
        else:
            # Try to extract after "add task"
            parts = command.split('add task', 1)
            if len(parts) > 1:
                task_text = parts[1].strip()
            else:
                return "Please specify what task to add. Example: 'add task: Buy groceries'"
        
        if not task_text:
            return "Please specify what task to add."
        
        # Create task
        task = {
            'id': len(self.tasks) + 1,
            'text': task_text,
            'created': datetime.now().isoformat(),
            'completed': False
        }
        
        self.tasks.append(task)
        self._save_tasks()
        
        return f"Added task: '{task_text}'"
    
    def _handle_list_tasks(self):
        """Handle listing tasks."""
        if not self.tasks:
            return "You have no tasks. Add one with: 'add task: your task here'"
        
        pending_tasks = [t for t in self.tasks if not t['completed']]
        
        if not pending_tasks:
            return "All tasks completed! Great job!"
        
        response = f"You have {len(pending_tasks)} pending task(s):\n"
        for i, task in enumerate(pending_tasks, 1):
            response += f"  {i}. {task['text']}\n"
        
        return response.strip()
    
    def _handle_math(self, command):
        """Handle basic math calculations."""
        # Extract mathematical expression
        math_expr = re.search(r'[\d\+\-\*/\.\s\(\)]+', command)
        
        if not math_expr:
            return "Please provide a math expression. Example: 'calculate 15 + 25'"
        
        expr = math_expr.group().strip()
        
        try:
            # Simple safety check
            if all(c in '0123456789+-*/.() ' for c in expr):
                result = eval(expr)
                return f"The answer is: {result}"
            else:
                return "Invalid mathematical expression."
        except Exception:
            return "Error calculating that expression."
    
    def _handle_system_info(self):
        """Handle system information requests."""
        import platform
        import os
        
        info = f"System: {platform.system()} {platform.release()}\n"
        info += f"Python: {platform.python_version()}\n"
        info += f"Working directory: {os.getcwd()}"
        
        return info
    
    def _handle_help(self):
        """Handle help requests."""
        help_text = """Available commands:

⏰ Time: "what time is it", "what date is it"
📝 Tasks: "add task: your task", "list tasks"
🧮 Math: "calculate 15 + 25", "what's 10 * 5"
💻 System: "system info", "computer info"
❓ Help: "help"
👋 Greetings: "hello", "hi"
👋 Goodbye: "bye", "quit"

Example usage:
- add task: Buy groceries
- list tasks
- calculate 15 * 23
- what time is it
"""
        return help_text

def main():
    """Main interactive loop."""
    print("🤖 AI Personal Assistant - Quick Start")
    print("=" * 50)
    print("This is a simplified version using only Python standard library.")
    print("Type 'help' for available commands or 'quit' to exit.\n")
    
    assistant = QuickAssistant()
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Assistant: Goodbye! Have a great day!")
                break
            
            response = assistant.process_command(user_input)
            print(f"Assistant: {response}\n")
            
        except KeyboardInterrupt:
            print("\nAssistant: Goodbye! Have a great day!")
            break
        except EOFError:
            print("\nAssistant: Goodbye! Have a great day!")
            break

def demo():
    """Run a demonstration without user interaction."""
    print("🚀 Quick Demo Mode")
    print("=" * 50)
    
    assistant = QuickAssistant()
    
    demo_commands = [
        ("what time is it", "Getting current time"),
        ("add task: Complete the AI project", "Adding a task"),
        ("add task: Buy groceries", "Adding another task"),
        ("list tasks", "Listing all tasks"),
        ("calculate 15 * 23 + 7", "Performing calculation"),
        ("system info", "Getting system information"),
        ("help", "Showing help information")
    ]
    
    for command, description in demo_commands:
        print(f"\n🎯 {description}")
        print(f"Command: '{command}'")
        response = assistant.process_command(command)
        print(f"Response: {response}")
        time.sleep(1)  # Brief pause for readability
    
    print("\n🎉 Demo complete!")
    print("\nTo run interactively: python3 quick_start.py")
    print("To see full assistant features: python3 assistant.py (after setup)")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo()
    else:
        main()