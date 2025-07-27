"""
Command Processor for AI Personal Assistant
"""
import re
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from core.nlp_processor import NLPProcessor
from services.task_manager import TaskManager
from services.web_scraper import WebScraper
from utils.logger import setup_logger, log_error

class CommandProcessor:
    """Processes user commands and executes appropriate actions."""
    
    def __init__(self):
        self.logger = setup_logger("command_processor")
        self.nlp_processor = NLPProcessor()
        self.task_manager = TaskManager()
        self.web_scraper = WebScraper()
        
        # Command handlers mapping
        self.command_handlers = {
            'time': self._handle_time_command,
            'weather': self._handle_weather_command,
            'search': self._handle_search_command,
            'task_add': self._handle_task_add_command,
            'task_list': self._handle_task_list_command,
            'calculation': self._handle_calculation_command,
            'system_info': self._handle_system_info_command,
            'greeting': self._handle_greeting_command,
            'goodbye': self._handle_goodbye_command,
            'help': self._handle_help_command,
            'general': self._handle_general_command
        }
    
    def process_command(self, command_text: str) -> Dict[str, Any]:
        """
        Process a user command and return a response.
        
        Args:
            command_text (str): User command text
            
        Returns:
            Dict[str, Any]: Processing result with response and metadata
        """
        try:
            # Analyze the command using NLP
            analysis = self.nlp_processor.analyze_command(command_text)
            
            # Get the appropriate handler
            intent = analysis['intent']
            handler = self.command_handlers.get(intent, self._handle_general_command)
            
            # Execute the command
            response = handler(analysis)
            
            # Add metadata to response
            response.update({
                'intent': intent,
                'confidence': analysis['confidence'],
                'category': analysis['category'],
                'timestamp': datetime.now().isoformat()
            })
            
            self.logger.info(f"Processed command: {intent}")
            return response
            
        except Exception as e:
            log_error(e, "command processing", self.logger)
            return {
                'text': "I'm sorry, I encountered an error processing your command. Please try again.",
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _handle_time_command(self, analysis: Dict) -> Dict[str, Any]:
        """Handle time and date related commands."""
        time_info = self.web_scraper.get_time_and_date()
        
        response_text = f"It's currently {time_info['formatted_datetime']}."
        
        return {
            'text': response_text,
            'data': time_info,
            'success': True
        }
    
    def _handle_weather_command(self, analysis: Dict) -> Dict[str, Any]:
        """Handle weather related commands."""
        # Extract location from entities if available
        entities = analysis.get('entities', {})
        location = "current"
        
        # Look for location in various entity types
        if 'gpe' in entities:  # Geopolitical entity
            location = entities['gpe'][0]
        elif 'loc' in entities:  # Location
            location = entities['loc'][0]
        
        weather_info = self.web_scraper.get_weather(location)
        
        if weather_info:
            if 'error' in weather_info:
                response_text = "I'm sorry, I couldn't retrieve the weather information right now."
            else:
                response_text = (
                    f"The weather in {weather_info.get('location', location)} is "
                    f"{weather_info.get('temperature', 'unknown')}°C with "
                    f"{weather_info.get('description', 'unknown conditions')}."
                )
                
                if 'humidity' in weather_info:
                    response_text += f" Humidity is {weather_info['humidity']}%."
        else:
            response_text = "I couldn't fetch the weather information at the moment."
        
        return {
            'text': response_text,
            'data': weather_info,
            'success': weather_info is not None
        }
    
    def _handle_search_command(self, analysis: Dict) -> Dict[str, Any]:
        """Handle search related commands."""
        # Extract search query from the original text
        search_query = analysis['original_text']
        
        # Remove common search prefixes
        search_prefixes = ['search for', 'find', 'look up', 'google', 'search']
        for prefix in search_prefixes:
            if search_query.lower().startswith(prefix):
                search_query = search_query[len(prefix):].strip()
                break
        
        if not search_query:
            return {
                'text': "What would you like me to search for?",
                'success': False
            }
        
        search_results = self.web_scraper.search_web(search_query, max_results=3)
        
        if search_results:
            response_text = f"Here's what I found about '{search_query}':\n\n"
            for i, result in enumerate(search_results, 1):
                response_text += f"{i}. {result['title']}\n{result['snippet']}\n\n"
        else:
            response_text = f"I couldn't find any information about '{search_query}'. Please try a different search term."
        
        return {
            'text': response_text,
            'data': search_results,
            'success': len(search_results) > 0
        }
    
    def _handle_task_add_command(self, analysis: Dict) -> Dict[str, Any]:
        """Handle task addition commands."""
        # Extract task details from the command
        original_text = analysis['original_text']
        
        # Remove task command prefixes
        task_prefixes = ['add task', 'create task', 'new task', 'remind me to', 'schedule']
        task_title = original_text
        
        for prefix in task_prefixes:
            if task_title.lower().startswith(prefix):
                task_title = task_title[len(prefix):].strip()
                break
        
        if not task_title:
            return {
                'text': "What task would you like me to add?",
                'success': False
            }
        
        # Extract due date if mentioned
        time_entities = analysis.get('entities', {})
        due_date = None
        
        if 'relative_time' in time_entities:
            # Parse relative time like "in 2 hours", "tomorrow"
            relative_time = time_entities['relative_time'][0]
            due_date = self._parse_relative_time(relative_time)
        
        # Add the task
        task_id = self.task_manager.add_task(task_title, due_date=due_date)
        
        response_text = f"I've added the task '{task_title}' to your list."
        if due_date:
            response_text += f" Due date: {due_date.strftime('%Y-%m-%d %H:%M')}"
        
        return {
            'text': response_text,
            'data': {'task_id': task_id, 'title': task_title, 'due_date': due_date},
            'success': True
        }
    
    def _handle_task_list_command(self, analysis: Dict) -> Dict[str, Any]:
        """Handle task listing commands."""
        tasks = self.task_manager.get_tasks(completed=False)
        
        if not tasks:
            response_text = "You have no pending tasks. Great job!"
        else:
            response_text = f"You have {len(tasks)} pending task(s):\n\n"
            for i, task in enumerate(tasks, 1):
                response_text += f"{i}. {task.title}"
                if task.due_date:
                    response_text += f" (Due: {task.due_date.strftime('%Y-%m-%d')})"
                response_text += f" [Priority: {task.priority}]\n"
        
        # Also check for upcoming tasks
        upcoming_tasks = self.task_manager.get_upcoming_tasks(days=3)
        if upcoming_tasks:
            response_text += f"\nUpcoming tasks in the next 3 days:\n"
            for task in upcoming_tasks:
                response_text += f"• {task.title} (Due: {task.due_date.strftime('%Y-%m-%d')})\n"
        
        return {
            'text': response_text,
            'data': {'tasks': [t.__dict__ for t in tasks]},
            'success': True
        }
    
    def _handle_calculation_command(self, analysis: Dict) -> Dict[str, Any]:
        """Handle calculation and math commands."""
        original_text = analysis['original_text']
        
        # Try Wolfram Alpha first
        wolfram_result = self.web_scraper.calculate_with_wolfram(original_text)
        if wolfram_result:
            return {
                'text': f"The answer is: {wolfram_result}",
                'data': {'result': wolfram_result, 'method': 'wolfram'},
                'success': True
            }
        
        # Fallback to basic math evaluation
        try:
            # Extract mathematical expression
            math_expression = re.search(r'[\d\+\-\*/\.\s\(\)]+', original_text)
            if math_expression:
                expr = math_expression.group().strip()
                # Safe evaluation of basic math
                if all(c in '0123456789+-*/.() ' for c in expr):
                    result = eval(expr)
                    return {
                        'text': f"The answer is: {result}",
                        'data': {'result': result, 'expression': expr, 'method': 'basic'},
                        'success': True
                    }
        except:
            pass
        
        return {
            'text': "I couldn't solve that calculation. Please try rephrasing it or use simpler math expressions.",
            'success': False
        }
    
    def _handle_system_info_command(self, analysis: Dict) -> Dict[str, Any]:
        """Handle system information commands."""
        try:
            # Get system information
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            system_info = {
                'cpu_usage': cpu_percent,
                'memory_total': round(memory.total / (1024**3), 2),  # GB
                'memory_used': round(memory.used / (1024**3), 2),   # GB
                'memory_percent': memory.percent,
                'disk_total': round(disk.total / (1024**3), 2),     # GB
                'disk_used': round(disk.used / (1024**3), 2),       # GB
                'disk_percent': round((disk.used / disk.total) * 100, 1)
            }
            
            response_text = (
                f"System Status:\n"
                f"• CPU Usage: {cpu_percent}%\n"
                f"• Memory: {system_info['memory_used']}GB / {system_info['memory_total']}GB ({memory.percent}%)\n"
                f"• Disk: {system_info['disk_used']}GB / {system_info['disk_total']}GB ({system_info['disk_percent']}%)"
            )
            
            return {
                'text': response_text,
                'data': system_info,
                'success': True
            }
            
        except Exception as e:
            log_error(e, "system info retrieval", self.logger)
            return {
                'text': "I couldn't retrieve system information at the moment.",
                'success': False
            }
    
    def _handle_greeting_command(self, analysis: Dict) -> Dict[str, Any]:
        """Handle greeting commands."""
        greetings = [
            "Hello! How can I assist you today?",
            "Hi there! What can I help you with?",
            "Good day! I'm here to help.",
            "Hello! Ready to assist you."
        ]
        
        import random
        response_text = random.choice(greetings)
        
        return {
            'text': response_text,
            'success': True
        }
    
    def _handle_goodbye_command(self, analysis: Dict) -> Dict[str, Any]:
        """Handle goodbye commands."""
        farewells = [
            "Goodbye! Have a great day!",
            "See you later! Take care!",
            "Farewell! Feel free to ask for help anytime.",
            "Goodbye! It was nice assisting you."
        ]
        
        import random
        response_text = random.choice(farewells)
        
        return {
            'text': response_text,
            'success': True,
            'action': 'quit'
        }
    
    def _handle_help_command(self, analysis: Dict) -> Dict[str, Any]:
        """Handle help commands."""
        help_text = """I can help you with the following:

🕒 Time & Date: "What time is it?" or "What's today's date?"
🌤️  Weather: "What's the weather?" or "Weather in New York"
🔍 Search: "Search for Python programming" or "Find information about AI"
📝 Tasks: "Add task: Buy groceries" or "List my tasks"
🧮 Math: "Calculate 15 * 23" or "What's 50% of 200?"
💻 System: "Show system info" or "Check computer performance"
❓ General: Ask me questions and I'll try to help!

Just say "Assistant" followed by your command to get started!"""
        
        return {
            'text': help_text,
            'success': True
        }
    
    def _handle_general_command(self, analysis: Dict) -> Dict[str, Any]:
        """Handle general/unknown commands."""
        original_text = analysis['original_text']
        
        # Try to search for the query
        search_results = self.web_scraper.search_web(original_text, max_results=1)
        
        if search_results:
            result = search_results[0]
            response_text = f"Here's what I found:\n\n{result['title']}\n{result['snippet']}"
        else:
            response_text = (
                "I'm not sure how to help with that. You can ask me about:\n"
                "• Time and date\n"
                "• Weather information\n"
                "• Web searches\n"
                "• Task management\n"
                "• Calculations\n"
                "• System information\n\n"
                "Say 'help' for more details!"
            )
        
        return {
            'text': response_text,
            'data': search_results,
            'success': len(search_results) > 0
        }
    
    def _parse_relative_time(self, relative_time: str) -> Optional[datetime]:
        """Parse relative time expressions to datetime objects."""
        try:
            now = datetime.now()
            relative_time = relative_time.lower()
            
            if 'tomorrow' in relative_time:
                return now + timedelta(days=1)
            elif 'next week' in relative_time:
                return now + timedelta(weeks=1)
            elif 'next month' in relative_time:
                return now + timedelta(days=30)
            elif 'in' in relative_time:
                # Parse "in X minutes/hours/days"
                match = re.search(r'in (\d+) (minute|hour|day)s?', relative_time)
                if match:
                    amount = int(match.group(1))
                    unit = match.group(2)
                    
                    if unit == 'minute':
                        return now + timedelta(minutes=amount)
                    elif unit == 'hour':
                        return now + timedelta(hours=amount)
                    elif unit == 'day':
                        return now + timedelta(days=amount)
            
            return None
            
        except Exception as e:
            log_error(e, "relative time parsing", self.logger)
            return None