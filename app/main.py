import asyncio
import hmac
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException
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
    version="0.2.0",
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


def require_token(authorization: str | None = Header(default=None)) -> None:
    expected = settings.brain_access_token
    if not expected:
        raise HTTPException(
            status_code=503,
            detail="BRAIN_ACCESS_TOKEN is not configured on the server.",
        )
    scheme, _, token = (authorization or "").partition(" ")
    if scheme.lower() != "bearer" or not hmac.compare_digest(token, expected):
        raise HTTPException(status_code=401, detail="Unauthorized.")


@app.get("/api/health")
def health():
    return {
        "ok": True,
        "openai_configured": bool(settings.openai_api_key),
        "youtube_configured": bool(settings.youtube_api_key),
        "veo_configured": bool(settings.gemini_api_key),
        "auth_configured": bool(settings.brain_access_token),
    }


@app.get("/")
def index():
    return FileResponse(UI_DIR / "index.html")


@app.post("/api/brain", dependencies=[Depends(require_token)])
async def run_brain(request: BrainRequest):
    try:
        return await brain.execute(request)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Brain run failed: {exc}") from exc


@app.post("/api/video", dependencies=[Depends(require_token)])
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


@app.post("/api/video/render-pack", dependencies=[Depends(require_token)])
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
        results.append(
            {
                "shot_id": shot.shot_id,
                "status": result.status,
                "uri": result.uri,
                "file_name": result.file_name,
                "message": result.message,
            }
        )
        if result.status == "error":
            break

    return {
        "provider": "veo",
        "requested": min(request.limit, len(request.shots)),
        "results": results,
        "assembled_video": None,
        "note": "Shot rendering is implemented. Automatic final assembly and durable cloud storage are the next production layers.",
    }


@app.get("/api/media/{filename}", dependencies=[Depends(require_token)])
def media(filename: str):
    safe_name = Path(filename).name
    path = settings.output_directory / safe_name
    if not path.exists() or path.suffix.lower() != ".mp4":
        raise HTTPException(status_code=404, detail="Media file not found.")
    return FileResponse(path, media_type="video/mp4", filename=safe_name)


@app.post("/api/memory", dependencies=[Depends(require_token)])
def add_memory(item: MemoryInput):
    memory.add_memory(item.label, item.content)
    return {"ok": True}


@app.get("/api/memory", dependencies=[Depends(require_token)])
def get_memory():
    return {"memory": memory.context(limit=50)}
