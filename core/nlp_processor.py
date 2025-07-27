"""
Natural Language Processing Module for AI Personal Assistant
"""
import re
import spacy
import nltk
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from utils.logger import setup_logger, log_error
from config import CATEGORIES

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
except:
    pass

class NLPProcessor:
    """Handles natural language processing for user commands."""
    
    def __init__(self):
        self.logger = setup_logger("nlp_processor")
        self.nlp = None
        self.stopwords = set()
        self._initialize_nlp()
    
    def _initialize_nlp(self):
        """Initialize NLP models and tools."""
        try:
            # Try to load spaCy model
            try:
                self.nlp = spacy.load("en_core_web_sm")
                self.logger.info("spaCy model loaded successfully")
            except OSError:
                self.logger.warning("spaCy model 'en_core_web_sm' not found. Install with: python -m spacy download en_core_web_sm")
                self.nlp = None
            
            # Load NLTK stopwords
            try:
                from nltk.corpus import stopwords
                self.stopwords = set(stopwords.words('english'))
            except:
                self.logger.warning("NLTK stopwords not available")
                self.stopwords = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'])
            
        except Exception as e:
            log_error(e, "NLP initialization", self.logger)
    
    def analyze_command(self, text: str) -> Dict:
        """
        Analyze user command and extract intent, entities, and metadata.
        
        Args:
            text (str): User command text
            
        Returns:
            Dict: Analysis results including intent, entities, confidence
        """
        if not text or not text.strip():
            return {
                'intent': 'unknown',
                'entities': {},
                'confidence': 0.0,
                'category': 'general',
                'original_text': text,
                'processed_text': ''
            }
        
        # Clean and normalize text
        processed_text = self._preprocess_text(text)
        
        # Extract intent and category
        intent, category, confidence = self._extract_intent(processed_text)
        
        # Extract entities
        entities = self._extract_entities(processed_text)
        
        # Extract time information
        time_info = self._extract_time_information(processed_text)
        if time_info:
            entities.update(time_info)
        
        return {
            'intent': intent,
            'entities': entities,
            'confidence': confidence,
            'category': category,
            'original_text': text,
            'processed_text': processed_text
        }
    
    def _preprocess_text(self, text: str) -> str:
        """
        Clean and normalize input text.
        
        Args:
            text (str): Raw input text
            
        Returns:
            str: Preprocessed text
        """
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Handle contractions
        contractions = {
            "won't": "will not",
            "can't": "cannot",
            "n't": " not",
            "'re": " are",
            "'ve": " have",
            "'ll": " will",
            "'d": " would",
            "'m": " am"
        }
        
        for contraction, expansion in contractions.items():
            text = text.replace(contraction, expansion)
        
        return text
    
    def _extract_intent(self, text: str) -> Tuple[str, str, float]:
        """
        Extract intent from preprocessed text.
        
        Args:
            text (str): Preprocessed text
            
        Returns:
            Tuple[str, str, float]: (intent, category, confidence)
        """
        # Intent patterns with confidence scores
        intent_patterns = {
            'time': {
                'patterns': [r'\b(what.*time|current time|time.*now|what.*date|today.*date)\b'],
                'confidence': 0.9
            },
            'weather': {
                'patterns': [r'\b(weather|temperature|forecast|rain|sunny|cloudy)\b'],
                'confidence': 0.8
            },
            'search': {
                'patterns': [r'\b(search|find|look.*up|google|wikipedia)\b'],
                'confidence': 0.8
            },
            'task_add': {
                'patterns': [r'\b(add.*task|create.*task|new.*task|remind.*me|schedule)\b'],
                'confidence': 0.8
            },
            'task_list': {
                'patterns': [r'\b(list.*tasks|show.*tasks|my.*tasks|what.*tasks)\b'],
                'confidence': 0.8
            },
            'calculation': {
                'patterns': [r'\b(calculate|compute|math|solve|\+|\-|\*|\/|\d+.*\d+)\b'],
                'confidence': 0.7
            },
            'system_info': {
                'patterns': [r'\b(system|computer|cpu|memory|disk|performance)\b'],
                'confidence': 0.7
            },
            'greeting': {
                'patterns': [r'\b(hello|hi|hey|good morning|good afternoon|good evening)\b'],
                'confidence': 0.9
            },
            'goodbye': {
                'patterns': [r'\b(goodbye|bye|see you|talk later|exit|quit)\b'],
                'confidence': 0.9
            },
            'help': {
                'patterns': [r'\b(help|what.*can.*do|commands|features)\b'],
                'confidence': 0.8
            }
        }
        
        best_intent = 'general'
        best_category = 'general'
        best_confidence = 0.1
        
        for intent, data in intent_patterns.items():
            for pattern in data['patterns']:
                if re.search(pattern, text):
                    confidence = data['confidence']
                    if confidence > best_confidence:
                        best_intent = intent
                        best_confidence = confidence
                        
                        # Map intent to category
                        for cat, keywords in CATEGORIES.items():
                            if any(keyword in intent or keyword in text for keyword in keywords):
                                best_category = cat
                                break
        
        return best_intent, best_category, best_confidence
    
    def _extract_entities(self, text: str) -> Dict:
        """
        Extract entities from text using spaCy if available.
        
        Args:
            text (str): Preprocessed text
            
        Returns:
            Dict: Extracted entities
        """
        entities = {}
        
        if self.nlp:
            try:
                doc = self.nlp(text)
                
                for ent in doc.ents:
                    entity_type = ent.label_.lower()
                    entity_text = ent.text
                    
                    if entity_type not in entities:
                        entities[entity_type] = []
                    entities[entity_type].append(entity_text)
                    
            except Exception as e:
                log_error(e, "spaCy entity extraction", self.logger)
        
        # Manual entity extraction as fallback
        # Extract numbers
        numbers = re.findall(r'\b\d+(?:\.\d+)?\b', text)
        if numbers:
            entities['numbers'] = numbers
        
        # Extract URLs
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        if urls:
            entities['urls'] = urls
        
        # Extract email addresses
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if emails:
            entities['emails'] = emails
        
        return entities
    
    def _extract_time_information(self, text: str) -> Optional[Dict]:
        """
        Extract time-related information from text.
        
        Args:
            text (str): Preprocessed text
            
        Returns:
            Optional[Dict]: Time information if found
        """
        time_info = {}
        
        # Time patterns
        time_patterns = {
            'relative_time': [
                r'\b(in \d+ minutes?|in \d+ hours?|in \d+ days?|tomorrow|next week|next month)\b',
                r'\b(today|tonight|this morning|this afternoon|this evening)\b'
            ],
            'absolute_time': [
                r'\b\d{1,2}:\d{2}(?:\s*(?:am|pm))?\b',
                r'\b\d{1,2}\s*(?:am|pm)\b'
            ],
            'date_patterns': [
                r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',
                r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}\b'
            ]
        }
        
        for time_type, patterns in time_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    time_info[time_type] = matches
        
        return time_info if time_info else None
    
    def extract_keywords(self, text: str) -> List[str]:
        """
        Extract important keywords from text.
        
        Args:
            text (str): Input text
            
        Returns:
            List[str]: List of keywords
        """
        # Remove stopwords and extract keywords
        words = text.lower().split()
        keywords = [word for word in words if word not in self.stopwords and len(word) > 2]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            if keyword not in seen:
                seen.add(keyword)
                unique_keywords.append(keyword)
        
        return unique_keywords
    
    def get_sentiment(self, text: str) -> str:
        """
        Get basic sentiment of text.
        
        Args:
            text (str): Input text
            
        Returns:
            str: Sentiment (positive, negative, or neutral)
        """
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'love', 'like', 'happy', 'glad']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'dislike', 'angry', 'sad', 'frustrated', 'annoying']
        
        words = text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'