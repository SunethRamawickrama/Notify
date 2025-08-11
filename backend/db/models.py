from sqlalchemy import Column, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.mutable import MutableList

Base = declarative_base()

class ChatSession(Base):
   
    __tablename__ = "sessions"
    sessionId = Column("sessionId", String, primary_key=True)
    userId = Column("userId", String, nullable=False)
    messages = Column("messages", MutableList.as_mutable(JSON), nullable=False)
