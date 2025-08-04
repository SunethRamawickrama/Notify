from fastapi import FastAPI, UploadFile, File, Depends, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from document_processor.upload_handler import UploadHandler
from chat.chat import Chat, generate_message
from jwt_verifier import get_jwk, verify_jwt, get_current_user

from uuid import uuid4

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

file_saver = UploadHandler()

@app.post("/api/upload")
def upload(file: UploadFile = File(...)):
    global file_saver
    file_saver.upload(file=file)

    return JSONResponse(content={"message": "File uploaded Successfully!"}, status_code=200)

@app.post("/api/chat")
def chat(question: Chat, user=Depends(get_current_user)):
    response =  generate_message(question=question.userMessage)
    session_id = str(uuid4())
    # create a new chat session in the database and add these messages to it with userId
    return JSONResponse(content={"response": response, "session_id": session_id}, status_code=200)

@app.post("/api/chat/{sessionId}")
def chat(question: Chat, user=Depends(get_current_user)):
    response =  generate_message(question=question.userMessage)
    chat_id = str(uuid4())
    return JSONResponse(content={"response": response, "chat_id": chat_id}, status_code=200)