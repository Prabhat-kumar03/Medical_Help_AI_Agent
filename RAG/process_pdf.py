from fastapi import UploadFile
from io import BytesIO
import PyPDF2

async def process_pdf(file: UploadFile) -> str:
    try:
        data: str = ""
        file_content = await file.read()
        pdf_content = PyPDF2.PdfReader(BytesIO(file_content))
        for page in pdf_content.pages:
            data += page.extract_text()
        print("PDF to String")
        return data
    except Exception as e:
        print("Error---------->", e)
