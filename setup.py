#!/usr/bin/env python3
"""
Setup script for AI Personal Assistant
"""
import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"Installing {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install {description}")
        print(f"Error: {e.stderr}")
        return False

def install_system_dependencies():
    """Install system-level dependencies."""
    system = platform.system().lower()
    
    print("Installing system dependencies...")
    
    if system == "linux":
        # Ubuntu/Debian
        commands = [
            "sudo apt-get update",
            "sudo apt-get install -y python3-dev python3-pip",
            "sudo apt-get install -y portaudio19-dev python3-pyaudio",
            "sudo apt-get install -y espeak espeak-data libespeak1 libespeak-dev",
            "sudo apt-get install -y ffmpeg"
        ]
        
        for cmd in commands:
            if not run_command(cmd, f"System package ({cmd.split()[-1]})"):
                print("Warning: Some system packages may not have installed correctly")
    
    elif system == "darwin":  # macOS
        commands = [
            "brew install portaudio",
            "brew install espeak",
            "brew install ffmpeg"
        ]
        
        # Check if Homebrew is installed
        if subprocess.run("which brew", shell=True, capture_output=True).returncode != 0:
            print("Homebrew not found. Please install Homebrew first:")
            print("Visit: https://brew.sh/")
            return False
        
        for cmd in commands:
            run_command(cmd, f"Homebrew package ({cmd.split()[-1]})")
    
    elif system == "windows":
        print("On Windows, please ensure you have:")
        print("1. Visual C++ Build Tools installed")
        print("2. A microphone and speakers/headphones connected")
        print("3. Windows Speech Platform SDK (optional)")
    
    return True

def install_python_dependencies():
    """Install Python dependencies."""
    print("\nInstalling Python dependencies...")
    
    # Install requirements
    if not run_command("pip install -r requirements.txt", "Python packages"):
        print("Trying with pip3...")
        if not run_command("pip3 install -r requirements.txt", "Python packages"):
            return False
    
    # Download spaCy model
    print("Downloading spaCy English model...")
    spacy_commands = [
        "python -m spacy download en_core_web_sm",
        "python3 -m spacy download en_core_web_sm"
    ]
    
    for cmd in spacy_commands:
        if run_command(cmd, "spaCy English model"):
            break
    else:
        print("Warning: spaCy model download failed. NLP features may be limited.")
    
    return True

def create_environment_file():
    """Create a .env file template for API keys."""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("\nCreating environment file for API keys...")
        
        env_content = """# AI Personal Assistant - Environment Variables
# Copy this file and add your actual API keys

# OpenAI API Key (for advanced NLP - optional)
OPENAI_API_KEY=your_openai_api_key_here

# Wolfram Alpha API Key (for calculations - optional)
WOLFRAM_API_KEY=your_wolfram_alpha_api_key_here

# Weather API Key (OpenWeatherMap - optional)
WEATHER_API_KEY=your_openweather_api_key_here

# Note: The assistant will work without these API keys,
# but some features may be limited.
"""
        
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print("✓ Created .env file template")
        print("  Edit .env file to add your API keys (optional)")
    else:
        print("✓ Environment file already exists")

def test_installation():
    """Test the installation."""
    print("\nTesting installation...")
    
    try:
        # Test imports
        import speech_recognition
        import pyttsx3
        import requests
        import nltk
        
        print("✓ Core packages imported successfully")
        
        # Test microphone
        import pyaudio
        print("✓ Audio system available")
        
        # Test spaCy
        try:
            import spacy
            nlp = spacy.load("en_core_web_sm")
            print("✓ spaCy model loaded successfully")
        except:
            print("⚠ spaCy model not available (NLP features will be limited)")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Test error: {e}")
        return False

def main():
    """Main setup function."""
    print("=== AI Personal Assistant Setup ===\n")
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required")
        sys.exit(1)
    
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.system()} {platform.release()}\n")
    
    # Install system dependencies
    if not install_system_dependencies():
        print("Warning: Some system dependencies may not have installed correctly")
    
    # Install Python dependencies
    if not install_python_dependencies():
        print("Error: Failed to install Python dependencies")
        sys.exit(1)
    
    # Create environment file
    create_environment_file()
    
    # Test installation
    if test_installation():
        print("\n✓ Setup completed successfully!")
        print("\nTo start the assistant:")
        print("  python assistant.py")
        print("\nTo test components:")
        print("  python assistant.py --test")
        print("\nTo run interactive setup:")
        print("  python assistant.py --setup")
        
        # Provide API key information
        print("\n=== Optional API Keys ===")
        print("For enhanced features, you can add API keys to the .env file:")
        print("• OpenAI API Key: For advanced natural language processing")
        print("• Wolfram Alpha API Key: For complex calculations and queries")
        print("• OpenWeatherMap API Key: For accurate weather information")
        print("\nThe assistant will work without these keys, but some features may be limited.")
        
    else:
        print("\n✗ Setup completed with errors")
        print("Some features may not work correctly")
        sys.exit(1)

if __name__ == "__main__":
    main()