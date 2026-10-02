import asyncio
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .brain import ContentBrain
from .config import settings
from .models import BrainRequest, MemoryInput, RenderPackRequest, VideoRequest
from .storage import MemoryStore
from .video import generate_with_veo

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


@app.post("/api/video")
async def generate_video(request: VideoRequest):
    if not settings.gemini_api_key:
        raise HTTPException(status_code=503, detail="GEMINI_API_KEY is not configured.")
    result = await asyncio.to_thread(
        generate_with_veo,
        request.prompt,
        request.aspect_ratio,
    )
    if result.status == "error":
        raise HTTPException(status_code=502, detail=result.message or "Veo generation failed.")
    return result


@app.post("/api/video/render-pack")
async def render_pack(request: RenderPackRequest):
    if not settings.gemini_api_key:
        raise HTTPException(status_code=503, detail="GEMINI_API_KEY is not configured.")

    results = []
    for shot in request.shots[: request.limit]:
        result = await asyncio.to_thread(
            generate_with_veo,
            shot.prompt,
            request.aspect_ratio,
        )
        results.append({
            "shot_id": shot.shot_id,
            "status": result.status,
            "uri": result.uri,
            "message": result.message,
        })
        if result.status == "error":
            break

    return {
        "provider": "veo",
        "requested": min(request.limit, len(request.shots)),
        "results": results,
        "assembled_video": None,
        "note": "Shot rendering is implemented; automatic final assembly is the next production layer.",
    }


@app.post("/api/memory")
def add_memory(item: MemoryInput):
    memory.add_memory(item.label, item.content)
    return {"ok": True}


@app.get("/api/memory")
def get_memory():
    return {"memory": memory.context(limit=50)}
