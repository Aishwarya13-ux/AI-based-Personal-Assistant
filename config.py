"""
Configuration file for the AI Personal Assistant
"""
import os
from pathlib import Path

# Base configuration
BASE_DIR = Path(__file__).parent.absolute()
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Voice settings
VOICE_RATE = 200  # Speech rate
VOICE_VOLUME = 0.9  # Volume level (0.0 to 1.0)
VOICE_ID = 0  # Voice ID (0 for male, 1 for female on most systems)

# Speech recognition settings
MICROPHONE_INDEX = None  # None for default microphone
RECOGNITION_TIMEOUT = 5  # Seconds
RECOGNITION_PHRASE_TIMEOUT = 1  # Seconds

# Wake word
WAKE_WORD = "assistant"  # Change this to your preferred wake word

# API Keys (set these as environment variables for security)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
WOLFRAM_API_KEY = os.getenv("WOLFRAM_API_KEY", "")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")

# Web scraping settings
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
REQUEST_TIMEOUT = 10  # Seconds

# Task management
TASKS_FILE = DATA_DIR / "tasks.json"
REMINDERS_FILE = DATA_DIR / "reminders.json"

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FILE = LOGS_DIR / "assistant.log"

# Command categories
CATEGORIES = {
    "time": ["time", "date", "clock", "calendar"],
    "weather": ["weather", "temperature", "forecast"],
    "search": ["search", "find", "lookup", "google"],
    "tasks": ["task", "todo", "reminder", "schedule"],
    "system": ["system", "computer", "cpu", "memory"],
    "music": ["play", "music", "song", "spotify"],
    "calculation": ["calculate", "math", "compute", "solve"],
    "general": ["what", "who", "where", "when", "why", "how"]
}