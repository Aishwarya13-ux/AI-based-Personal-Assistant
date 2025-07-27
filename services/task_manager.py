"""
Task Management Service for AI Personal Assistant
"""
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from utils.logger import setup_logger, log_error
from config import TASKS_FILE, REMINDERS_FILE

@dataclass
class Task:
    """Represents a task/todo item."""
    id: str
    title: str
    description: str = ""
    created_at: datetime = None
    due_date: Optional[datetime] = None
    completed: bool = False
    priority: str = "medium"  # low, medium, high
    category: str = "general"
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.due_date, str):
            self.due_date = datetime.fromisoformat(self.due_date)

@dataclass
class Reminder:
    """Represents a reminder."""
    id: str
    message: str
    remind_at: datetime
    created_at: datetime = None
    triggered: bool = False
    recurring: bool = False
    recurring_interval: Optional[str] = None  # daily, weekly, monthly
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.remind_at, str):
            self.remind_at = datetime.fromisoformat(self.remind_at)

class TaskManager:
    """Manages tasks, todos, and reminders."""
    
    def __init__(self):
        self.logger = setup_logger("task_manager")
        self.tasks: List[Task] = []
        self.reminders: List[Reminder] = []
        self._load_data()
    
    def _load_data(self):
        """Load tasks and reminders from files."""
        try:
            # Load tasks
            if TASKS_FILE.exists():
                with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                    tasks_data = json.load(f)
                    self.tasks = [Task(**task_data) for task_data in tasks_data]
                self.logger.info(f"Loaded {len(self.tasks)} tasks")
            
            # Load reminders
            if REMINDERS_FILE.exists():
                with open(REMINDERS_FILE, 'r', encoding='utf-8') as f:
                    reminders_data = json.load(f)
                    self.reminders = [Reminder(**reminder_data) for reminder_data in reminders_data]
                self.logger.info(f"Loaded {len(self.reminders)} reminders")
                
        except Exception as e:
            log_error(e, "loading task data", self.logger)
    
    def _save_data(self):
        """Save tasks and reminders to files."""
        try:
            # Save tasks
            tasks_data = []
            for task in self.tasks:
                task_dict = asdict(task)
                # Convert datetime objects to ISO format strings
                if task_dict['created_at']:
                    task_dict['created_at'] = task.created_at.isoformat()
                if task_dict['due_date']:
                    task_dict['due_date'] = task.due_date.isoformat()
                tasks_data.append(task_dict)
            
            with open(TASKS_FILE, 'w', encoding='utf-8') as f:
                json.dump(tasks_data, f, indent=2, ensure_ascii=False)
            
            # Save reminders
            reminders_data = []
            for reminder in self.reminders:
                reminder_dict = asdict(reminder)
                # Convert datetime objects to ISO format strings
                if reminder_dict['created_at']:
                    reminder_dict['created_at'] = reminder.created_at.isoformat()
                if reminder_dict['remind_at']:
                    reminder_dict['remind_at'] = reminder.remind_at.isoformat()
                reminders_data.append(reminder_dict)
            
            with open(REMINDERS_FILE, 'w', encoding='utf-8') as f:
                json.dump(reminders_data, f, indent=2, ensure_ascii=False)
                
            self.logger.info("Task data saved successfully")
            
        except Exception as e:
            log_error(e, "saving task data", self.logger)
    
    def add_task(self, title: str, description: str = "", due_date: Optional[datetime] = None, 
                 priority: str = "medium", category: str = "general") -> str:
        """
        Add a new task.
        
        Args:
            title (str): Task title
            description (str): Task description
            due_date (Optional[datetime]): Due date
            priority (str): Priority level
            category (str): Task category
            
        Returns:
            str: Task ID
        """
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            category=category
        )
        
        self.tasks.append(task)
        self._save_data()
        
        self.logger.info(f"Added task: {title}")
        return task_id
    
    def get_tasks(self, category: Optional[str] = None, completed: Optional[bool] = None) -> List[Task]:
        """
        Get tasks with optional filtering.
        
        Args:
            category (Optional[str]): Filter by category
            completed (Optional[bool]): Filter by completion status
            
        Returns:
            List[Task]: Filtered tasks
        """
        filtered_tasks = self.tasks
        
        if category:
            filtered_tasks = [t for t in filtered_tasks if t.category == category]
        
        if completed is not None:
            filtered_tasks = [t for t in filtered_tasks if t.completed == completed]
        
        return filtered_tasks
    
    def complete_task(self, task_id: str) -> bool:
        """
        Mark a task as completed.
        
        Args:
            task_id (str): Task ID
            
        Returns:
            bool: True if task was found and completed
        """
        for task in self.tasks:
            if task.id == task_id:
                task.completed = True
                self._save_data()
                self.logger.info(f"Task completed: {task.title}")
                return True
        
        self.logger.warning(f"Task not found: {task_id}")
        return False
    
    def delete_task(self, task_id: str) -> bool:
        """
        Delete a task.
        
        Args:
            task_id (str): Task ID
            
        Returns:
            bool: True if task was found and deleted
        """
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                deleted_task = self.tasks.pop(i)
                self._save_data()
                self.logger.info(f"Task deleted: {deleted_task.title}")
                return True
        
        self.logger.warning(f"Task not found: {task_id}")
        return False
    
    def add_reminder(self, message: str, remind_at: datetime, recurring: bool = False, 
                    recurring_interval: Optional[str] = None) -> str:
        """
        Add a new reminder.
        
        Args:
            message (str): Reminder message
            remind_at (datetime): When to remind
            recurring (bool): If reminder should repeat
            recurring_interval (Optional[str]): Repeat interval
            
        Returns:
            str: Reminder ID
        """
        reminder_id = str(uuid.uuid4())
        reminder = Reminder(
            id=reminder_id,
            message=message,
            remind_at=remind_at,
            recurring=recurring,
            recurring_interval=recurring_interval
        )
        
        self.reminders.append(reminder)
        self._save_data()
        
        self.logger.info(f"Added reminder: {message}")
        return reminder_id
    
    def get_due_reminders(self) -> List[Reminder]:
        """
        Get reminders that are due now.
        
        Returns:
            List[Reminder]: Due reminders
        """
        now = datetime.now()
        due_reminders = []
        
        for reminder in self.reminders:
            if not reminder.triggered and reminder.remind_at <= now:
                due_reminders.append(reminder)
                reminder.triggered = True
                
                # Handle recurring reminders
                if reminder.recurring and reminder.recurring_interval:
                    next_reminder_time = self._calculate_next_reminder_time(
                        reminder.remind_at, reminder.recurring_interval
                    )
                    if next_reminder_time:
                        new_reminder = Reminder(
                            id=str(uuid.uuid4()),
                            message=reminder.message,
                            remind_at=next_reminder_time,
                            recurring=True,
                            recurring_interval=reminder.recurring_interval
                        )
                        self.reminders.append(new_reminder)
        
        if due_reminders:
            self._save_data()
        
        return due_reminders
    
    def _calculate_next_reminder_time(self, current_time: datetime, interval: str) -> Optional[datetime]:
        """
        Calculate the next reminder time for recurring reminders.
        
        Args:
            current_time (datetime): Current reminder time
            interval (str): Recurrence interval
            
        Returns:
            Optional[datetime]: Next reminder time
        """
        try:
            if interval == "daily":
                return current_time + timedelta(days=1)
            elif interval == "weekly":
                return current_time + timedelta(weeks=1)
            elif interval == "monthly":
                return current_time + timedelta(days=30)  # Approximate
            else:
                return None
        except Exception as e:
            log_error(e, "calculating next reminder time", self.logger)
            return None
    
    def get_upcoming_tasks(self, days: int = 7) -> List[Task]:
        """
        Get tasks due in the next specified days.
        
        Args:
            days (int): Number of days to look ahead
            
        Returns:
            List[Task]: Upcoming tasks
        """
        cutoff_date = datetime.now() + timedelta(days=days)
        upcoming_tasks = []
        
        for task in self.tasks:
            if not task.completed and task.due_date and task.due_date <= cutoff_date:
                upcoming_tasks.append(task)
        
        # Sort by due date
        upcoming_tasks.sort(key=lambda t: t.due_date or datetime.max)
        
        return upcoming_tasks
    
    def get_task_statistics(self) -> Dict:
        """
        Get task statistics.
        
        Returns:
            Dict: Task statistics
        """
        total_tasks = len(self.tasks)
        completed_tasks = len([t for t in self.tasks if t.completed])
        pending_tasks = total_tasks - completed_tasks
        overdue_tasks = len([t for t in self.tasks 
                           if not t.completed and t.due_date and t.due_date < datetime.now()])
        
        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'overdue_tasks': overdue_tasks,
            'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        }