#!/usr/bin/env python3
"""
AI Personal Assistant Demo Script

This script demonstrates the capabilities of the AI Personal Assistant
without requiring voice input or microphone setup.
"""
import time
import sys
from datetime import datetime, timedelta
from services.command_processor import CommandProcessor
from services.task_manager import TaskManager
from services.web_scraper import WebScraper
from core.nlp_processor import NLPProcessor
from utils.logger import setup_logger

def print_separator():
    """Print a visual separator."""
    print("\n" + "="*60 + "\n")

def demo_command(command_processor, command, description):
    """Demonstrate a single command."""
    print(f"🎯 {description}")
    print(f"Command: '{command}'")
    print("Response:")
    
    try:
        response = command_processor.process_command(command)
        print(f"  {response.get('text', 'No response')}")
        
        if response.get('data'):
            print(f"  [Additional data available]")
    except Exception as e:
        print(f"  Error: {e}")
    
    print_separator()
    time.sleep(1)  # Brief pause for readability

def main():
    """Main demo function."""
    print("🤖 AI Personal Assistant Demo")
    print("Showcasing capabilities without requiring voice input")
    print_separator()
    
    # Initialize components
    try:
        command_processor = CommandProcessor()
        task_manager = TaskManager()
        nlp_processor = NLPProcessor()
        web_scraper = WebScraper()
        
        print("✅ All components initialized successfully!")
        print_separator()
    except Exception as e:
        print(f"❌ Error initializing components: {e}")
        sys.exit(1)
    
    # Demo 1: Time and Date
    demo_command(command_processor, "what time is it", 
                "Time and Date Information")
    
    # Demo 2: Natural Language Processing
    print("🧠 Natural Language Processing Demo")
    sample_texts = [
        "Add task: Buy groceries tomorrow",
        "What's the weather like in Paris?",
        "Calculate 15 times 23 plus 100",
        "Search for information about artificial intelligence"
    ]
    
    for text in sample_texts:
        analysis = nlp_processor.analyze_command(text)
        print(f"Text: '{text}'")
        print(f"  Intent: {analysis['intent']} (confidence: {analysis['confidence']:.2f})")
        print(f"  Category: {analysis['category']}")
        if analysis['entities']:
            print(f"  Entities: {analysis['entities']}")
        print()
    
    print_separator()
    
    # Demo 3: Task Management
    print("📝 Task Management Demo")
    
    # Add some demo tasks
    task_ids = []
    demo_tasks = [
        "Complete the AI assistant project",
        "Buy groceries",
        "Call the dentist",
        "Prepare presentation for Monday"
    ]
    
    print("Adding demo tasks...")
    for task in demo_tasks:
        task_id = task_manager.add_task(task, priority="medium")
        task_ids.append(task_id)
        print(f"  ✓ Added: {task}")
    
    print()
    
    # Show task statistics
    stats = task_manager.get_task_statistics()
    print("Task Statistics:")
    print(f"  Total tasks: {stats['total_tasks']}")
    print(f"  Pending tasks: {stats['pending_tasks']}")
    print(f"  Completed tasks: {stats['completed_tasks']}")
    
    # Mark one task as complete
    if task_ids:
        task_manager.complete_task(task_ids[0])
        print(f"  ✓ Marked first task as complete")
    
    print_separator()
    
    # Demo 4: Command Processing
    demo_command(command_processor, "list my tasks", 
                "Task Listing")
    
    demo_command(command_processor, "calculate 25 * 4 + 10", 
                "Mathematical Calculation")
    
    demo_command(command_processor, "show system info", 
                "System Information")
    
    # Demo 5: Web Search (if internet available)
    try:
        demo_command(command_processor, "search for Python programming", 
                    "Web Search Capability")
    except:
        print("🔍 Web Search Demo (requires internet connection)")
        print("Command: 'search for Python programming'")
        print("Response: [Internet connection required for web search]")
        print_separator()
    
    # Demo 6: Help System
    demo_command(command_processor, "help", 
                "Help and Available Commands")
    
    # Demo 7: Greeting and Conversation
    demo_command(command_processor, "hello", 
                "Conversational Greetings")
    
    # Demo 8: Complex Queries
    demo_command(command_processor, "What is artificial intelligence", 
                "General Knowledge Queries")
    
    # Clean up demo tasks
    print("🧹 Cleaning up demo data...")
    for task_id in task_ids:
        task_manager.delete_task(task_id)
    print("  ✓ Demo tasks removed")
    
    print_separator()
    
    # Demo Summary
    print("🎉 Demo Complete!")
    print("\nThe AI Personal Assistant demonstrated:")
    print("  ✓ Natural Language Processing")
    print("  ✓ Task Management")
    print("  ✓ Time and Date Information")
    print("  ✓ Mathematical Calculations")
    print("  ✓ System Information")
    print("  ✓ Web Search Capabilities")
    print("  ✓ Conversational Interface")
    print("  ✓ Help System")
    
    print("\nTo run the full assistant with voice capabilities:")
    print("  python assistant.py")
    
    print("\nTo test all components:")
    print("  python assistant.py --test")
    
    print("\nTo configure the assistant:")
    print("  python assistant.py --setup")

def quick_demo():
    """Run a quick demonstration of key features."""
    print("🚀 Quick Demo - Key Features")
    print_separator()
    
    try:
        command_processor = CommandProcessor()
        
        quick_commands = [
            ("what time is it", "⏰ Time Information"),
            ("calculate 42 * 13", "🧮 Mathematics"),
            ("help", "❓ Help System")
        ]
        
        for command, description in quick_commands:
            print(f"{description}")
            response = command_processor.process_command(command)
            print(f"  {response.get('text', 'No response')[:100]}...")
            print()
        
        print("✅ Quick demo complete!")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        quick_demo()
    else:
        main()