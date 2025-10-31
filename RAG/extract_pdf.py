import PyPDF2

def extract_pdf(pdf_path: str):
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = len(reader.pages)
            pdf_data = ""

            for page_num in range(num_pages):
                page = reader.pages[page_num]
                text = page.extract_text()
                pdf_data += "".join(text)
            return pdf_data
    except Exception as e:
        print(f"⚠️ Unexpected error: {e}")
