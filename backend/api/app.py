from fastapi import FastAPI, UploadFile, File, Depends, Header, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session
from db.models import Base
from db.database import SessionLocal, engine
import db.crud as crud

from document_processor.upload_handler import UploadHandler
from chat.chat import Chat, HumanMessageType, AssistantMessageType, generate_message
from api.jwt_verifier import get_jwk, verify_jwt, get_current_user

from uuid import uuid4
import logging
import traceback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://192.168.0.134:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

file_saver = UploadHandler()

@app.post("/api/upload")
def upload(file: UploadFile = File(...)):
    global file_saver
    file_saver.upload(file=file)

    return JSONResponse(content={"message": "File uploaded Successfully!"}, status_code=200)

@app.get("/api/messages/{session_id}")
def get_messages_for_session(session_id: str, db: Session = Depends(get_db)):
    try:
        session = crud.get_session(db=db, sessionId=session_id)

        # GET JWT token and verify the userId with jwt.userId == session.userId else return 403 unauthroized

        if not session:
            return JSONResponse(content={"response": "Session not found"}, status_code=404)

        return JSONResponse(content={"messages": session.messages}, status_code=200)
    except Exception as e:
        logger.error(f"Error fetching messages for the given session: {e}")
        traceback.print_exc()
        return JSONResponse(content={"response": "Failed to fetch messages"}, status_code=500)

@app.post("/api/chat")
def chat(question: Chat, db: Session = Depends(get_db)): 
    
    # create a new chat session in the database and add these messages to it with userId

    try:
        response =  generate_message(question=question.userMessage)
        logger.info(f"Generated response: {response}")
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        traceback.print_exc()
        return JSONResponse(content={"response": "Failed to generate response"}, status_code=500)

    session_id = str(uuid4())

    user_message = {
        "id": 1,
        "role": "user",
        "content": question.userMessage
    }

    ai_message = {
        "id": 2,
        "role": "assistant",
        "content": response,
        "retrieved_documents": []
    }

    messages = [user_message, ai_message]

    try:
        session = crud.create_session(db=db, sessionId=session_id, userId=question.user_id, initial_messages=messages)
        return JSONResponse(content={"response": response, "session_id": session_id}, status_code=200)
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        traceback.print_exc()
        return JSONResponse(content={"response": "Failed to create session"}, status_code=500)

@app.post("/api/chat/{sessionId}")
def chat(question: HumanMessageType, sessionId: str, db: Session = Depends(get_db)):
    response =  generate_message(question=question.content)

    ai_message = AssistantMessageType(
        id=str(int(question.id)+1),  
        role="assistant",
        content=response,
        retrieved_documents=[]
    )

    crud.append_message(db=db, sessionId=sessionId, message=[question.model_dump(), ai_message.model_dump()])
    return JSONResponse(content={"response": response, "session_id": sessionId}, status_code=200)

@app.get("api/sessions")
# Later will extract the user id from the jwt, keep the header for testing
def get_sessions_for_the_user(db: Session = Depends(get_db), userId: str = Header(...)):
    try:
        sessions = crud.get_sessions_by_user(db=db, userId=userId)
        if not sessions:
            return JSONResponse(content={"response": "No sessions found for the user"}, status_code=404)
        return JSONResponse(content={"sessions": sessions}, status_code=200)
    except Exception as e:
        logger.error(f"Error fetching sessions for the user: {e}")
        traceback.print_exc()
        return JSONResponse(content={"response": "Failed to fetch sessions"}, status_code=500)


