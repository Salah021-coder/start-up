# ============================================================================
# FILE: ai/chatbot/gemini_client.py
# ============================================================================

from typing import List, Dict, Generator
from config.gemini_config import GeminiConfig

class GeminiClient:
    """Robust Gemini client (NO silent failure)"""

    def __init__(self):
        self.model = None
        self.chat_session = None
        self.is_available = False

        api_key = GeminiConfig.get_api_key()

        if not api_key:
            raise RuntimeError("❌ GEMINI_API_KEY not found (secrets or env)")

        try:
            import google.generativeai as genai

            genai.configure(api_key=api_key)

            self.model = genai.GenerativeModel(
                model_name=GeminiConfig.MODEL_NAME,
                generation_config=GeminiConfig.get_generation_config(),
                safety_settings=GeminiConfig.SAFETY_SETTINGS,
            )

            self.is_available = True
            print("✅ Gemini initialized successfully")

        except ImportError:
            raise RuntimeError(
                "❌ google-generativeai not installed. Run: pip install google-generativeai"
            )
        except Exception as e:
            raise RuntimeError(f"❌ Gemini initialization failed: {e}")

    def initialize_chat(self, system_prompt: str, history: List[Dict] = None):
        if not self.is_available:
            raise RuntimeError("Gemini not available")

        formatted_history = self._format_history(history) if history else []
        self.chat_session = self.model.start_chat(history=formatted_history)

        if system_prompt:
            self.chat_session.send_message(system_prompt)

    def send_message(self, message: str, stream: bool = False):
        if not self.chat_session:
            raise RuntimeError("Chat session not initialized")

        if stream:
            return self._send_streaming(message)

        response = self.chat_session.send_message(message)
        return response.text

    def _send_streaming(self, message: str) -> Generator[str, None, None]:
        response = self.chat_session.send_message(message, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text

    @staticmethod
    def _format_history(history: List[Dict]) -> List[Dict]:
        return [
            {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
            for m in history
        ]

    def clear_session(self):
        self.chat_session = None
