"""
Database Models for Chat History
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class Analysis(Base):
    __tablename__ = 'analyses'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    boundary_geojson = Column(Text)
    results_json = Column(Text)
    overall_score = Column(Integer)
    
    # Relationships
    chat_messages = relationship("ChatMessage", back_populates="analysis")

class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(String, ForeignKey('analyses.id'))
    role = Column(String)  # 'user' or 'assistant'
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata_json = Column(Text)  # Store additional context as JSON
    
    # Relationships
    analysis = relationship("Analysis", back_populates="chat_messages")