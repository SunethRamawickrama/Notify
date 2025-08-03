import os
import shutil
from werkzeug.utils import secure_filename
from fastapi import UploadFile

class UploadHandler() :
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)

    def upload(self, file: UploadFile) -> str:
        filename = secure_filename(file.filename)
        destination = os.path.join(self.upload_dir, filename)

        with open(destination, "wb") as out_file:
            shutil.copyfileobj(file.file, out_file)

        return destination


        
