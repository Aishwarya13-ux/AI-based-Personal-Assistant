"""
Text-to-Speech Module for AI Personal Assistant
"""
import pyttsx3
import threading
from typing import Optional
from utils.logger import setup_logger, log_error
from config import VOICE_RATE, VOICE_VOLUME, VOICE_ID

class TextToSpeech:
    """Handles text-to-speech conversion and audio output."""
    
    def __init__(self):
        self.logger = setup_logger("text_to_speech")
        self.engine = None
        self.is_speaking = False
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize the TTS engine with configured settings."""
        try:
            self.engine = pyttsx3.init()
            
            # Configure voice settings
            self.engine.setProperty('rate', VOICE_RATE)
            self.engine.setProperty('volume', VOICE_VOLUME)
            
            # Set voice (try to use configured voice ID)
            voices = self.engine.getProperty('voices')
            if voices and len(voices) > VOICE_ID:
                self.engine.setProperty('voice', voices[VOICE_ID].id)
                self.logger.info(f"Voice set to: {voices[VOICE_ID].name}")
            else:
                self.logger.warning("Could not set specified voice, using default")
            
            self.logger.info("TTS engine initialized successfully")
            
        except Exception as e:
            log_error(e, "TTS engine initialization", self.logger)
            self.engine = None
    
    def speak(self, text: str, blocking: bool = False):
        """
        Convert text to speech and play it.
        
        Args:
            text (str): Text to convert to speech
            blocking (bool): If True, wait for speech to complete
        """
        if not self.engine:
            self.logger.error("TTS engine not available")
            return
        
        if not text or not text.strip():
            self.logger.warning("Empty text provided for speech")
            return
        
        def speak_text():
            try:
                self.is_speaking = True
                self.logger.info(f"Speaking: {text}")
                self.engine.say(text)
                self.engine.runAndWait()
                self.is_speaking = False
            except Exception as e:
                log_error(e, "text-to-speech", self.logger)
                self.is_speaking = False
        
        if blocking:
            speak_text()
        else:
            # Run in separate thread for non-blocking speech
            thread = threading.Thread(target=speak_text, daemon=True)
            thread.start()
    
    def stop_speaking(self):
        """Stop current speech output."""
        if self.engine and self.is_speaking:
            try:
                self.engine.stop()
                self.is_speaking = False
                self.logger.info("Speech stopped")
            except Exception as e:
                log_error(e, "stopping speech", self.logger)
    
    def set_voice(self, voice_id: int) -> bool:
        """
        Change the voice used for speech.
        
        Args:
            voice_id (int): Voice ID to use
            
        Returns:
            bool: True if voice was set successfully, False otherwise
        """
        if not self.engine:
            return False
        
        try:
            voices = self.engine.getProperty('voices')
            if voices and len(voices) > voice_id:
                self.engine.setProperty('voice', voices[voice_id].id)
                self.logger.info(f"Voice changed to: {voices[voice_id].name}")
                return True
            else:
                self.logger.warning(f"Voice ID {voice_id} not available")
                return False
        except Exception as e:
            log_error(e, "setting voice", self.logger)
            return False
    
    def set_rate(self, rate: int):
        """
        Set the speech rate.
        
        Args:
            rate (int): Speech rate (words per minute)
        """
        if not self.engine:
            return
        
        try:
            self.engine.setProperty('rate', rate)
            self.logger.info(f"Speech rate set to: {rate}")
        except Exception as e:
            log_error(e, "setting speech rate", self.logger)
    
    def set_volume(self, volume: float):
        """
        Set the speech volume.
        
        Args:
            volume (float): Volume level (0.0 to 1.0)
        """
        if not self.engine:
            return
        
        try:
            volume = max(0.0, min(1.0, volume))  # Clamp between 0.0 and 1.0
            self.engine.setProperty('volume', volume)
            self.logger.info(f"Speech volume set to: {volume}")
        except Exception as e:
            log_error(e, "setting speech volume", self.logger)
    
    def get_available_voices(self) -> list:
        """
        Get list of available voices.
        
        Returns:
            list: List of available voice names and IDs
        """
        if not self.engine:
            return []
        
        try:
            voices = self.engine.getProperty('voices')
            voice_list = []
            for i, voice in enumerate(voices):
                voice_list.append({
                    'id': i,
                    'name': voice.name,
                    'languages': getattr(voice, 'languages', [])
                })
            return voice_list
        except Exception as e:
            log_error(e, "getting available voices", self.logger)
            return []
    
    def test_speech(self) -> bool:
        """
        Test the TTS system.
        
        Returns:
            bool: True if test successful, False otherwise
        """
        test_text = "Hello! This is a test of the text to speech system."
        try:
            self.speak(test_text, blocking=True)
            self.logger.info("TTS test successful")
            return True
        except Exception as e:
            log_error(e, "TTS test", self.logger)
            return False