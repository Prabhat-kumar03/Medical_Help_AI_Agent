from RAG.process_pdf import process_pdf
from RAG.text_splitter import text_splitter
from RAG.vector_store import get_vector_store
from fastapi import UploadFile

#uploading file 
async def upload_pdf(file: UploadFile):
    try:
        pdf_data = await process_pdf(file)
        chunks_array = text_splitter(pdf_data)
        vector_store = get_vector_store()
        vector_store.add_documents(documents=chunks_array)
        vector_store.save_local("faiss_index")
        print("Pdf file uploaded successfully")
        return {"sucess": True}
    except Exception as e:
        print("Error occured while saving data :", e)
        return {"sucess": False}


if __name__ == "__main__":
    upload_pdf("pdf.pdf")
