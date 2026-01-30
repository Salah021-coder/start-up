"""
Manage Chat Conversations and History
"""
from typing import List, Dict, Optional
from datetime import datetime
from database.chat_repository import ChatRepository

class ConversationManager:
    def __init__(self, analysis_id: Optional[str] = None):
        self.analysis_id = analysis_id
        self.messages: List[Dict] = []
        self.chat_repo = ChatRepository()
    
    def add_message(self, role: str, content: str, metadata: Dict = None):
        """Add a message to the conversation"""
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        self.messages.append(message)
        
        # Save to database
        if self.analysis_id:
            self.chat_repo.save_message(
                analysis_id=self.analysis_id,
                message=message
            )
    
    def get_context_messages(self, limit: int = 10) -> List[Dict]:
        """Get recent messages for context"""
        return self.messages[-limit:]
    
    def get_full_history(self) -> List[Dict]:
        """Get complete conversation history"""
        return self.messages
    
    def load_history(self, analysis_id: str):
        """Load conversation history from database"""
        self.messages = self.chat_repo.get_conversation(analysis_id)
    
    def clear_history(self):
        """Clear conversation history"""
        self.messages = []
    
    def export_conversation(self, format: str = 'json') -> str:
        """Export conversation in specified format"""
        if format == 'json':
            import json
            return json.dumps(self.messages, indent=2)
        elif format == 'text':
            return '\n\n'.join([
                f"{msg['role'].upper()}: {msg['content']}" 
                for msg in self.messages
            ])
