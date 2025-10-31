from fastapi import FastAPI
from agent_app import combined_agent
from langgraph.types import Command
from fastapi import FastAPI, Form, File, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse

from RAG.save_data_to_vectordb import upload_pdf
app = FastAPI()


@app.post("/answer")
def handle_user_query(user_input: str = Form(...), session_id: str = Form(...)):
    config = {
        "configurable": {
            "thread_id": session_id,
        }
    }
    cmd = Command(resume=user_input)
    result = combined_agent.invoke(cmd, config=config)
    if result.get("__interrupt__"):
        return {"status": "awaiting_input", "result": result.get("__interrupt__")}
    return {"status": "resumed", "result": result}


@app.post("/upload-file")
def pdf_upload_handler(background_task: BackgroundTasks, file: UploadFile = File(...)):
    try:
        background_task.add_task(upload_pdf, file)
        return JSONResponse(
            status_code=200, content={"message": "File Uploaded Successfully"}
        )
    except Exception as e:
        print("Error occured while uploading file to Vector DB- ", e)
        return JSONResponse(
            status_code=500, content={"message": "Internal Server Error"}
        )
