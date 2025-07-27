# AI Personal Assistant

A comprehensive voice-activated AI assistant similar to Siri or Alexa, built with Python. Features include speech recognition, natural language processing, task management, web scraping, and text-to-speech capabilities.

## Features

### 🎤 Voice Interaction
- **Wake Word Detection**: Responds to "Assistant" wake word
- **Speech Recognition**: Converts speech to text using Google Speech API
- **Text-to-Speech**: Natural voice responses with configurable voices and speed
- **Continuous Listening**: Always ready to help when you say the wake word

### 🧠 Natural Language Processing
- **Intent Recognition**: Understands various command types and user intentions
- **Entity Extraction**: Identifies important information like dates, locations, and numbers
- **Context Awareness**: Maintains conversation context for better responses
- **Sentiment Analysis**: Basic emotion detection in user input

### 📝 Task Management
- **Todo Lists**: Add, list, and manage personal tasks
- **Reminders**: Set time-based reminders with recurring options
- **Due Dates**: Track task deadlines and get notifications
- **Categories**: Organize tasks by different categories
- **Statistics**: View productivity metrics and completion rates

### 🌐 Web Integration
- **Web Search**: Search the internet using DuckDuckGo and Wikipedia
- **Weather Information**: Get current weather and forecasts
- **News Headlines**: Fetch latest news on specific topics
- **Page Scraping**: Extract content from web pages
- **Wolfram Alpha**: Advanced calculations and factual queries

### 💻 System Information
- **Performance Monitoring**: Check CPU, memory, and disk usage
- **System Status**: Get real-time system information
- **Resource Alerts**: Monitor system performance

### 🕒 Time & Date
- **Current Time**: Get the current time and date
- **Time Zones**: Support for different time zones
- **Scheduling**: Parse and understand relative time expressions

## Installation

### Prerequisites

- Python 3.7 or higher
- Microphone and speakers/headphones
- Internet connection for some features

### Quick Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ai-personal-assistant
   ```

2. **Run the setup script:**
   ```bash
   python setup.py
   ```

   This will:
   - Install system dependencies
   - Install Python packages
   - Download required language models
   - Create configuration files

3. **Test the installation:**
   ```bash
   python assistant.py --test
   ```

4. **Configure the assistant:**
   ```bash
   python assistant.py --setup
   ```

### Manual Installation

If the setup script doesn't work for your system:

1. **Install system dependencies:**
   
   **Ubuntu/Debian:**
   ```bash
   sudo apt-get update
   sudo apt-get install python3-dev python3-pip portaudio19-dev python3-pyaudio espeak espeak-data libespeak1 libespeak-dev ffmpeg
   ```
   
   **macOS:**
   ```bash
   brew install portaudio espeak ffmpeg
   ```
   
   **Windows:**
   - Install Visual C++ Build Tools
   - Ensure microphone and speakers are connected

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download language models:**
   ```bash
   python -m spacy download en_core_web_sm
   ```

## Usage

### Starting the Assistant

```bash
python assistant.py
```

The assistant will:
1. Initialize all components
2. Calibrate the microphone
3. Start listening for the wake word "Assistant"
4. Provide both voice and text input options

### Voice Commands

Say "Assistant" followed by your command:

- **"Assistant, what time is it?"**
- **"Assistant, what's the weather like?"**
- **"Assistant, add task: Buy groceries"**
- **"Assistant, search for Python programming"**
- **"Assistant, calculate 15 times 23"**
- **"Assistant, show system information"**
- **"Assistant, list my tasks"**
- **"Assistant, help"**

### Text Commands

You can also type commands directly:

```
> what time is it
> weather in New York
> add task: Call the dentist tomorrow
> search for artificial intelligence
> list tasks
> help
> quit
```

### Command Categories

#### Time & Date
- "What time is it?"
- "What's today's date?"
- "What day is it?"

#### Weather
- "What's the weather?"
- "Weather in [city]"
- "Is it going to rain?"

#### Task Management
- "Add task: [task description]"
- "List my tasks"
- "Show pending tasks"
- "Remind me to [task] in [time]"

#### Web Search
- "Search for [query]"
- "Find information about [topic]"
- "Look up [subject]"

#### Calculations
- "Calculate [expression]"
- "What's [number] plus [number]?"
- "Solve [math problem]"

#### System Information
- "Show system info"
- "Check computer performance"
- "What's my CPU usage?"

#### General Queries
- Ask any question and the assistant will try to help
- "What is [subject]?"
- "Tell me about [topic]"

## Configuration

### API Keys (Optional)

For enhanced features, add API keys to the `.env` file:

```env
# OpenAI API Key (for advanced NLP)
OPENAI_API_KEY=your_openai_api_key_here

# Wolfram Alpha API Key (for calculations)
WOLFRAM_API_KEY=your_wolfram_alpha_api_key_here

# Weather API Key (OpenWeatherMap)
WEATHER_API_KEY=your_openweather_api_key_here
```

### Voice Settings

Modify `config.py` to customize:

```python
# Voice settings
VOICE_RATE = 200  # Speech rate (words per minute)
VOICE_VOLUME = 0.9  # Volume level (0.0 to 1.0)
VOICE_ID = 0  # Voice ID (0 for male, 1 for female)

# Wake word
WAKE_WORD = "assistant"  # Change to your preferred wake word
```

## Project Structure

```
ai-personal-assistant/
├── assistant.py              # Main application entry point
├── config.py                # Configuration settings
├── setup.py                 # Installation script
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── .env                    # Environment variables (API keys)
├── core/                   # Core functionality
│   ├── __init__.py
│   ├── speech_recognition.py   # Speech-to-text processing
│   ├── text_to_speech.py      # Text-to-speech conversion
│   └── nlp_processor.py       # Natural language processing
├── services/               # Business logic services
│   ├── __init__.py
│   ├── command_processor.py   # Command interpretation and execution
│   ├── task_manager.py       # Task and reminder management
│   └── web_scraper.py        # Web scraping and API integration
├── utils/                  # Utility functions
│   ├── __init__.py
│   └── logger.py            # Logging utilities
├── data/                   # Data storage
│   ├── tasks.json           # User tasks
│   └── reminders.json       # User reminders
└── logs/                   # Application logs
    └── assistant.log        # Main log file
```

## Troubleshooting

### Common Issues

1. **Microphone not working:**
   - Check microphone permissions
   - Try running: `python assistant.py --test`
   - Ensure microphone is not muted

2. **Speech recognition errors:**
   - Check internet connection
   - Verify microphone quality
   - Try speaking more clearly

3. **Text-to-speech not working:**
   - Install espeak: `sudo apt-get install espeak`
   - Check audio output settings
   - Verify speaker/headphone connection

4. **Module import errors:**
   - Run setup script: `python setup.py`
   - Install manually: `pip install -r requirements.txt`
   - Check Python version (3.7+ required)

5. **spaCy model missing:**
   - Download manually: `python -m spacy download en_core_web_sm`
   - Check internet connection during setup

### Performance Tips

- **Reduce background noise** for better speech recognition
- **Use a quality microphone** for improved accuracy
- **Close unnecessary applications** to free system resources
- **Update audio drivers** if experiencing audio issues

## Development

### Adding New Commands

1. **Create a new intent** in `core/nlp_processor.py`
2. **Add a handler** in `services/command_processor.py`
3. **Map the intent** to the handler in the command_handlers dictionary

### Extending Functionality

- **Add new services** in the `services/` directory
- **Create new utilities** in the `utils/` directory
- **Modify configuration** in `config.py`

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **SpeechRecognition** library for speech-to-text
- **pyttsx3** for text-to-speech conversion
- **spaCy** for natural language processing
- **Wikipedia API** for information retrieval
- **DuckDuckGo** for web search capabilities
- **Wolfram Alpha** for computational queries

## Support

If you encounter any issues or have questions:

1. Check the troubleshooting section above
2. Run the test command: `python assistant.py --test`
3. Check the logs in `logs/assistant.log`
4. Open an issue on the repository

---

**Enjoy your AI Personal Assistant!** 🤖✨