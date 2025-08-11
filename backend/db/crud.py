from asyncio.log import logger
from typing import List
from sqlalchemy.orm import Session
from db.models import ChatSession

def create_session(db: Session, sessionId: str, userId: str, initial_messages: list):
    session = ChatSession(sessionId=sessionId, userId=userId, messages=initial_messages)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def get_sessions_by_user(db: Session, userId: str):
    sessions = db.query(ChatSession).filter(ChatSession.userId == userId).all()
    logger.info(f"Found {len(sessions)} sessions for userId={userId}")
    return sessions

def get_session(db: Session, sessionId: str):
    session = db.query(ChatSession).filter(ChatSession.sessionId == sessionId).first()
    logger.info(f"Looking for sessionId={sessionId} found: {session}")
    return session

def append_message(db: Session, sessionId: str, message: List[dict]):
    session = get_session(db, sessionId)
    if not session:
        logger.warning(f"Session not found for sessionId={sessionId}")
        return None
    current_messages = session.messages or []
    current_messages.extend(message)
    session.messages = current_messages

    db.commit()
    db.refresh(session)
    return session
