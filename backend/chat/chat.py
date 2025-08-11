from asyncio.log import logger
from pyexpat.errors import messages
import traceback
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel
from dotenv import load_dotenv
import os

from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

class Chat(BaseModel):
    userMessage: str
    user_id: str

class HumanMessageType(BaseModel):
    id: str
    role: str = "user"
    content: str

class AssistantMessageType(BaseModel):
    id: str
    role: str = "assistant"
    content: str
    retrieved_documents: list = []

def generate_message(question):

    messages = [
    (
        "system",
        "You are a helpful assistant that answers user questions.",
    ),
    (f"human", f"{question}"),
    ]

    try:
        ai_msg = llm.invoke(messages)
        response = ai_msg.content
        logger.info(f"LLM response: {response}")
        return response
    except Exception as e:
        traceback.print_exc()   
        logger.error(f"Error generating message: {e}")
        return "Error"