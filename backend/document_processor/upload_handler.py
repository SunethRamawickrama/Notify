import os
import shutil
import traceback
from werkzeug.utils import secure_filename
from fastapi import UploadFile

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from .vector_store import vector_store

class UploadHandler() :
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)

    def upload(self, file: UploadFile) -> dict:

        try:
            docs = []
            filename = secure_filename(file.filename)
            destination = os.path.join(self.upload_dir, filename)

            with open(destination, "wb") as out_file:
                shutil.copyfileobj(file.file, out_file)

            loader = PyPDFLoader(destination)
            pages = loader.load()

            for i, page in enumerate(pages):
                page.metadata["source"] = destination
                page.metadata["page_number"] = i + 1
                docs.append(page)

            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

            doc_splits = splitter.split_documents(docs)
            vector_store.add_documents(doc_splits)
            vector_store.persist()

            print({
                "file": destination,
                "pages": len(pages),
                "chunks": len(doc_splits)
            })

            return {
                "file": destination,
                "pages": len(pages),
                "chunks": len(doc_splits)
            }
        
        except Exception as e:
            print("Error occurred while uploading file:", e)
            traceback.print_exc()
            return {"error": str(e)}