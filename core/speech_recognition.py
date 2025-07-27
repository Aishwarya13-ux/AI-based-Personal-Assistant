"""
Speech Recognition Module for AI Personal Assistant
"""
import speech_recognition as sr
import threading
import time
from typing import Optional, Callable
from utils.logger import setup_logger, log_error
from config import (
    MICROPHONE_INDEX, 
    RECOGNITION_TIMEOUT, 
    RECOGNITION_PHRASE_TIMEOUT,
    WAKE_WORD
)

class SpeechRecognizer:
    """Handles speech recognition and wake word detection."""
    
    def __init__(self):
        self.logger = setup_logger("speech_recognition")
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone(device_index=MICROPHONE_INDEX)
        self.is_listening = False
        self.wake_word_detected = False
        
        # Adjust for ambient noise
        self._calibrate_microphone()
    
    def _calibrate_microphone(self):
        """Calibrate microphone for ambient noise."""
        try:
            self.logger.info("Calibrating microphone for ambient noise...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            self.logger.info("Microphone calibration complete")
        except Exception as e:
            log_error(e, "microphone calibration", self.logger)
    
    def listen_for_wake_word(self, callback: Callable):
        """
        Continuously listen for the wake word.
        
        Args:
            callback (Callable): Function to call when wake word is detected
        """
        self.is_listening = True
        self.logger.info(f"Listening for wake word: '{WAKE_WORD}'")
        
        def listen_loop():
            while self.is_listening:
                try:
                    with self.microphone as source:
                        # Listen for audio with timeout
                        audio = self.recognizer.listen(
                            source, 
                            timeout=1, 
                            phrase_time_limit=3
                        )
                    
                    # Recognize speech
                    text = self.recognizer.recognize_google(audio).lower()
                    
                    if WAKE_WORD.lower() in text:
                        self.logger.info(f"Wake word detected: {text}")
                        self.wake_word_detected = True
                        callback()
                        
                except sr.WaitTimeoutError:
                    # Normal timeout, continue listening
                    pass
                except sr.UnknownValueError:
                    # Could not understand audio, continue listening
                    pass
                except sr.RequestError as e:
                    log_error(e, "speech recognition request", self.logger)
                    time.sleep(1)  # Wait before retrying
                except Exception as e:
                    log_error(e, "wake word detection", self.logger)
                    time.sleep(1)
        
        # Start listening in a separate thread
        thread = threading.Thread(target=listen_loop, daemon=True)
        thread.start()
    
    def listen_for_command(self) -> Optional[str]:
        """
        Listen for a command after wake word detection.
        
        Returns:
            Optional[str]: Recognized command text or None if failed
        """
        try:
            self.logger.info("Listening for command...")
            
            with self.microphone as source:
                # Listen for the command
                audio = self.recognizer.listen(
                    source,
                    timeout=RECOGNITION_TIMEOUT,
                    phrase_time_limit=RECOGNITION_PHRASE_TIMEOUT * 5  # Longer for commands
                )
            
            # Recognize the command
            command = self.recognizer.recognize_google(audio)
            self.logger.info(f"Command recognized: {command}")
            return command
            
        except sr.WaitTimeoutError:
            self.logger.warning("No command heard within timeout")
            return None
        except sr.UnknownValueError:
            self.logger.warning("Could not understand the command")
            return None
        except sr.RequestError as e:
            log_error(e, "command recognition", self.logger)
            return None
        except Exception as e:
            log_error(e, "command listening", self.logger)
            return None
    
    def stop_listening(self):
        """Stop the wake word listening loop."""
        self.is_listening = False
        self.logger.info("Stopped listening for wake word")
    
    def test_microphone(self) -> bool:
        """
        Test if microphone is working properly.
        
        Returns:
            bool: True if microphone is working, False otherwise
        """
        try:
            with self.microphone as source:
                self.logger.info("Testing microphone... Say something!")
                audio = self.recognizer.listen(source, timeout=5)
                text = self.recognizer.recognize_google(audio)
                self.logger.info(f"Microphone test successful. Heard: {text}")
                return True
        except Exception as e:
            log_error(e, "microphone test", self.logger)
            return False