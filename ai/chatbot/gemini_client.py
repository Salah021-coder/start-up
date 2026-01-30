import google.generativeai as genai
from typing import List, Dict, Generator
from config.gemini_config import GeminiConfig

class GeminiClient:
    """Robust Gemini client with Quota Awareness"""

    def __init__(self):
        self.model = None
        self.chat_session = None
        self.is_available = False

        api_key = GeminiConfig.get_api_key()
        if not api_key:
            raise RuntimeError("❌ GEMINI_API_KEY not found")

        try:
            genai.configure(api_key=api_key)
            # Basic model init (system_instruction is added during initialize_chat)
            self.model = genai.GenerativeModel(
                model_name=GeminiConfig.MODEL_NAME,
                generation_config=GeminiConfig.get_generation_config(),
                safety_settings=GeminiConfig.SAFETY_SETTINGS
            )
            self.is_available = True
        except Exception as e:
            raise RuntimeError(f"❌ Gemini initialization failed: {e}")

    def initialize_chat(self, system_prompt: str, history: List[Dict] = None):
        """Starts a session. System prompt is passed as an instruction to save quota."""
        if not self.is_available:
            raise RuntimeError("Gemini not available")

        # We re-define the model with the system_instruction to avoid calling .send_message()
        self.model = genai.GenerativeModel(
            model_name=GeminiConfig.MODEL_NAME,
            generation_config=GeminiConfig.get_generation_config(),
            safety_settings=GeminiConfig.SAFETY_SETTINGS,
            system_instruction=system_prompt # Does NOT count as a request
        )

        formatted_history = self._format_history(history) if history else []
        self.chat_session = self.model.start_chat(history=formatted_history)

    def send_message(self, message: str, stream: bool = False):
        if not self.chat_session:
            raise RuntimeError("Chat session not initialized")

        try:
            if stream:
                return self._send_streaming(message)
            
            response = self.chat_session.send_message(message)
            return response.text
        
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                raise RuntimeError("QUOTA_EXCEEDED")
            raise RuntimeError(f"API Error: {error_msg}")

    def _send_streaming(self, message: str) -> Generator[str, None, None]:
        try:
            response = self.chat_session.send_message(message, stream=True)
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            if "429" in str(e):
                yield "⚠️ Quota exceeded. Please wait a moment."
            else:
                yield f"⚠️ Error: {str(e)}"

    @staticmethod
    def _format_history(history: List[Dict]) -> List[Dict]:
        return [
            {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
            for m in history
        ]
