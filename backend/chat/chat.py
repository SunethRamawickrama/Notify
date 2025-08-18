from asyncio.log import logger
from pyexpat.errors import messages
import traceback
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from langchain.prompts import PromptTemplate

from langchain_core.prompts import ChatPromptTemplate
from document_processor.vector_store import vector_store
retriever = vector_store.as_retriever()

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

    docs = retriever.invoke(question)
    logger.info(f"Retrieved {len(docs)} documents for question: {question}")
    context_text = "\n\n".join([doc.page_content for doc in docs])

    logger.info(f"Retrieved documents: {context_text}")

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Use the provided context to answer the user's question. "
                   "If the context is not relevant, just say I don't know."),
        ("human", "Context:\n{context}\n\nQuestion: {question}")
    ])
    prompt = prompt_template.format_messages(context=context_text, question=question)

    retrieved_metadata = [
        {
        "source": doc.metadata.get("source"),
        "page_number": doc.metadata.get("page_number"),
        "snippet": doc.page_content[:200] 
        } for doc in docs]

    try:
        ai_msg = llm.invoke(prompt)
        response = ai_msg.content
        logger.info(f"LLM response: {response}")
        return {
            "generation": response, 
            "retrieved_documents": retrieved_metadata
        }
    except Exception as e:
        traceback.print_exc()   
        logger.error(f"Error generating message: {e}")
        return {"error": str(e)}