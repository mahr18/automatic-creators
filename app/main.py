from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .brain import ContentBrain
from .config import settings
from .models import BrainRequest, MemoryInput
from .storage import MemoryStore

BASE_DIR = Path(__file__).resolve().parent.parent
UI_DIR = BASE_DIR / "ui"

app = FastAPI(
    title="MAHER CONTENT BRAIN",
    version="0.1.0",
    description="Mobile-first agentic content research, ideation and prompt engine.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

memory = MemoryStore(settings.database_file)
brain = ContentBrain(memory)


@app.get("/api/health")
def health():
    return {
        "ok": True,
        "openai_configured": bool(settings.openai_api_key),
        "youtube_configured": bool(settings.youtube_api_key),
        "veo_configured": bool(settings.gemini_api_key),
    }


@app.get("/")
def index():
    return FileResponse(UI_DIR / "index.html")


@app.post("/api/brain")
async def run_brain(request: BrainRequest):
    try:
        return await brain.execute(request)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Brain run failed: {exc}") from exc


@app.post("/api/memory")
def add_memory(item: MemoryInput):
    memory.add_memory(item.label, item.content)
    return {"ok": True}


@app.get("/api/memory")
def get_memory():
    return {"memory": memory.context(limit=50)}
