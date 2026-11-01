from pathlib import Path
from fastapi import (
    FastAPI,
    File,
    HTTPException,
    UploadFile,
)
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from config import UPLOAD_DIR
from rag import (
    ask_question,
    create_brief,
    ingest_pdf,
)
from schemas import (
    AskRequest,
    BriefRequest,
)
app = FastAPI(
    title="Simple RAG API"
)
STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", include_in_schema=False)
def website():
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/health")
def health():
    return {
        "status": "OK"
    }
@app.post("/ingest")
async def ingest(
    file: UploadFile = File(...)
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Missing filename.",
        )
    filename = Path(
        file.filename
    ).name
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )
    file_path = (
        UPLOAD_DIR / filename
    )
    contents = await file.read()
    file_path.write_bytes(
        contents
    )
    try:
        return ingest_pdf(
            str(file_path),
            filename,
        )
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )
@app.post("/ask")
async def ask(
    request: AskRequest
):
    return await ask_question(
        request.question
    )
@app.post("/brief")
async def brief(
    request: BriefRequest
):
    return await create_brief(
        request.topic
    )
