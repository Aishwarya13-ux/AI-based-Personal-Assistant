"""
AI Personal Assistant - Main Application
"""
import threading
import time
import signal
import sys
from datetime import datetime
from typing import Optional
from core.speech_recognition import SpeechRecognizer
from core.text_to_speech import TextToSpeech
from services.command_processor import CommandProcessor
from services.task_manager import TaskManager
from utils.logger import setup_logger, log_user_interaction, log_error

class AIPersonalAssistant:
    """Main AI Personal Assistant class that coordinates all components."""
    
    def __init__(self):
        self.logger = setup_logger("ai_assistant")
        self.is_running = False
        self.is_listening = False
        
        # Initialize components
        self.logger.info("Initializing AI Personal Assistant...")
        
        try:
            self.speech_recognizer = SpeechRecognizer()
            self.text_to_speech = TextToSpeech()
            self.command_processor = CommandProcessor()
            self.task_manager = TaskManager()
            
            self.logger.info("All components initialized successfully")
            
        except Exception as e:
            log_error(e, "component initialization", self.logger)
            raise
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def start(self):
        """Start the AI Personal Assistant."""
        try:
            self.is_running = True
            self.logger.info("Starting AI Personal Assistant")
            
            # Welcome message
            welcome_message = (
                "Hello! I'm your AI Personal Assistant. "
                "I'm now listening for the wake word 'Assistant'. "
                "You can also type 'quit' to exit or 'help' for assistance."
            )
            print(f"\n{welcome_message}\n")
            self.text_to_speech.speak(welcome_message)
            
            # Start listening for wake word
            self.speech_recognizer.listen_for_wake_word(self._on_wake_word_detected)
            
            # Start reminder checking thread
            reminder_thread = threading.Thread(target=self._check_reminders, daemon=True)
            reminder_thread.start()
            
            # Main input loop (for text input as fallback)
            self._run_input_loop()
            
        except Exception as e:
            log_error(e, "assistant startup", self.logger)
            self.stop()
    
    def _run_input_loop(self):
        """Run the main input loop for text-based interaction."""
        print("You can also type commands directly (type 'quit' to exit):")
        
        while self.is_running:
            try:
                # Get text input
                user_input = input("> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'stop']:
                    self.stop()
                    break
                
                # Process the command
                self._process_user_command(user_input)
                
            except EOFError:
                # Handle Ctrl+D
                self.stop()
                break
            except KeyboardInterrupt:
                # Handle Ctrl+C
                self.stop()
                break
            except Exception as e:
                log_error(e, "input loop", self.logger)
    
    def _on_wake_word_detected(self):
        """Callback function when wake word is detected."""
        if not self.is_running:
            return
        
        self.logger.info("Wake word detected, listening for command...")
        self.text_to_speech.speak("Yes?")
        
        # Listen for the actual command
        command = self.speech_recognizer.listen_for_command()
        
        if command:
            self._process_user_command(command)
        else:
            self.text_to_speech.speak("I didn't catch that. Please try again.")
    
    def _process_user_command(self, command: str):
        """
        Process a user command and provide response.
        
        Args:
            command (str): User command to process
        """
        try:
            # Log the user input
            print(f"\nUser: {command}")
            
            # Process the command
            response = self.command_processor.process_command(command)
            
            # Extract response text
            response_text = response.get('text', 'I couldn\'t process that command.')
            
            # Log the interaction
            log_user_interaction(command, response_text, self.logger)
            
            # Display and speak the response
            print(f"Assistant: {response_text}\n")
            self.text_to_speech.speak(response_text)
            
            # Handle special actions
            if response.get('action') == 'quit':
                self.stop()
            
        except Exception as e:
            log_error(e, "command processing", self.logger)
            error_message = "I encountered an error processing your command. Please try again."
            print(f"Assistant: {error_message}\n")
            self.text_to_speech.speak(error_message)
    
    def _check_reminders(self):
        """Check for due reminders in a background thread."""
        while self.is_running:
            try:
                due_reminders = self.task_manager.get_due_reminders()
                
                for reminder in due_reminders:
                    reminder_text = f"Reminder: {reminder.message}"
                    self.logger.info(f"Triggering reminder: {reminder.message}")
                    
                    print(f"\n🔔 {reminder_text}\n")
                    self.text_to_speech.speak(reminder_text)
                
                # Check every 30 seconds
                time.sleep(30)
                
            except Exception as e:
                log_error(e, "reminder checking", self.logger)
                time.sleep(60)  # Wait longer on error
    
    def stop(self):
        """Stop the AI Personal Assistant."""
        if not self.is_running:
            return
        
        self.logger.info("Stopping AI Personal Assistant")
        self.is_running = False
        
        # Stop speech recognition
        if hasattr(self, 'speech_recognizer'):
            self.speech_recognizer.stop_listening()
        
        # Stop text-to-speech
        if hasattr(self, 'text_to_speech'):
            self.text_to_speech.stop_speaking()
        
        # Goodbye message
        goodbye_message = "Goodbye! Have a great day!"
        print(f"\n{goodbye_message}")
        
        # Try to speak goodbye (may not work if TTS is already stopped)
        try:
            self.text_to_speech.speak(goodbye_message, blocking=True)
        except:
            pass
        
        self.logger.info("AI Personal Assistant stopped")
    
    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown."""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)
    
    def test_components(self) -> bool:
        """
        Test all components to ensure they're working properly.
        
        Returns:
            bool: True if all tests pass
        """
        try:
            print("Testing AI Personal Assistant components...\n")
            
            # Test Text-to-Speech
            print("1. Testing Text-to-Speech...")
            if self.text_to_speech.test_speech():
                print("   ✓ Text-to-Speech working")
            else:
                print("   ✗ Text-to-Speech failed")
                return False
            
            # Test Speech Recognition
            print("2. Testing Speech Recognition...")
            print("   Please say something when prompted...")
            if self.speech_recognizer.test_microphone():
                print("   ✓ Speech Recognition working")
            else:
                print("   ✗ Speech Recognition failed")
                return False
            
            # Test Command Processing
            print("3. Testing Command Processing...")
            test_command = "what time is it"
            response = self.command_processor.process_command(test_command)
            if response.get('success'):
                print("   ✓ Command Processing working")
                print(f"   Response: {response['text']}")
            else:
                print("   ✗ Command Processing failed")
                return False
            
            # Test Task Management
            print("4. Testing Task Management...")
            task_id = self.task_manager.add_task("Test task", description="This is a test")
            if task_id:
                print("   ✓ Task Management working")
                # Clean up test task
                self.task_manager.delete_task(task_id)
            else:
                print("   ✗ Task Management failed")
                return False
            
            print("\n✓ All components working correctly!")
            return True
            
        except Exception as e:
            log_error(e, "component testing", self.logger)
            print(f"\n✗ Component testing failed: {e}")
            return False
    
    def run_interactive_setup(self):
        """Run interactive setup to configure the assistant."""
        print("=== AI Personal Assistant Setup ===\n")
        
        # Test components first
        if not self.test_components():
            print("\nSome components failed testing. Please check your configuration.")
            return False
        
        # Voice configuration
        print("\n=== Voice Configuration ===")
        voices = self.text_to_speech.get_available_voices()
        
        if voices:
            print("Available voices:")
            for voice in voices:
                print(f"  {voice['id']}: {voice['name']}")
            
            try:
                choice = input(f"\nSelect voice (0-{len(voices)-1}, or press Enter for default): ").strip()
                if choice and choice.isdigit():
                    voice_id = int(choice)
                    if 0 <= voice_id < len(voices):
                        self.text_to_speech.set_voice(voice_id)
                        print(f"Voice set to: {voices[voice_id]['name']}")
            except:
                pass
        
        # Speed configuration
        try:
            speed = input("\nSpeech speed (100-300, default 200): ").strip()
            if speed and speed.isdigit():
                speed_val = int(speed)
                if 100 <= speed_val <= 300:
                    self.text_to_speech.set_rate(speed_val)
                    print(f"Speech rate set to: {speed_val}")
        except:
            pass
        
        print("\n=== Setup Complete ===")
        print("Your AI Personal Assistant is ready to use!")
        
        return True

def main():
    """Main entry point for the AI Personal Assistant."""
    try:
        assistant = AIPersonalAssistant()
        
        # Check command line arguments
        if len(sys.argv) > 1:
            if sys.argv[1] == '--test':
                assistant.test_components()
                return
            elif sys.argv[1] == '--setup':
                assistant.run_interactive_setup()
                return
        
        # Run the assistant
        assistant.start()
        
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()