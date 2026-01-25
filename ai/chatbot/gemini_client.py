# ============================================================================
# FILE: ai/chatbot/gemini_client.py (UPDATED WITH ERROR HANDLING)
# ============================================================================

import os
from typing import List, Dict, Optional, Generator

class GeminiClient:
    """Gemini API Client Wrapper with error handling"""
    
    def __init__(self):
        """Initialize Gemini client with error handling"""
        self.model = None
        self.chat_session = None
        self.is_available = False
        
        try:
            # Check if API key exists
            from config.gemini_config import GeminiConfig
            
            if not GeminiConfig.API_KEY or GeminiConfig.API_KEY == 'your-gemini-api-key-here':
                raise ValueError("Gemini API key not configured")
            
            # Try to import and configure
            import google.generativeai as genai
            
            genai.configure(api_key=GeminiConfig.API_KEY)
            self.model = genai.GenerativeModel(
                model_name=GeminiConfig.MODEL_NAME,
                generation_config=GeminiConfig.get_generation_config(),
                safety_settings=GeminiConfig.SAFETY_SETTINGS
            )
            self.is_available = True
            
        except ImportError:
            print("⚠️ google-generativeai not installed. Install with: pip install google-generativeai")
            self.is_available = False
        except Exception as e:
            print(f"⚠️ Gemini initialization failed: {str(e)}")
            self.is_available = False
    
    def initialize_chat(self, system_prompt: str, history: List[Dict] = None):
        """Initialize a new chat session"""
        if not self.is_available:
            raise ValueError("Gemini API not available. Check your API key configuration.")
        
        formatted_history = self._format_history(history) if history else []
        self.chat_session = self.model.start_chat(history=formatted_history)
        
        # Send system prompt if provided
        if system_prompt:
            self.chat_session.send_message(system_prompt)
    
    def send_message(self, message: str, stream: bool = False):
        """Send a message and get response"""
        if not self.is_available:
            raise ValueError("Gemini API not available")
        
        if not self.chat_session:
            raise ValueError("Chat session not initialized. Call initialize_chat first.")
        
        try:
            if stream:
                return self._send_streaming(message)
            else:
                response = self.chat_session.send_message(message)
                return response.text
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}. Please try rephrasing your question."
    
    def _send_streaming(self, message: str) -> Generator[str, None, None]:
        """Send message with streaming response"""
        response = self.chat_session.send_message(message, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text
    
    def _format_history(self, history: List[Dict]) -> List[Dict]:
        """Format conversation history for Gemini"""
        formatted = []
        for msg in history:
            formatted.append({
                'role': 'user' if msg['role'] == 'user' else 'model',
                'parts': [msg['content']]
            })
        return formatted
    
    def clear_session(self):
        """Clear the current chat session"""
        self.chat_session = None