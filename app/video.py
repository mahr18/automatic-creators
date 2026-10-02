from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from .config import settings


@dataclass
class VideoResult:
    provider: str
    status: str
    uri: str | None = None
    file_name: str | None = None
    message: str | None = None


def generate_with_veo(prompt: str, aspect_ratio: str = "16:9") -> VideoResult:
    """Generate one Veo 3.1 shot and persist it temporarily on the server."""
    if not settings.gemini_api_key:
        return VideoResult(
            provider="veo",
            status="not_configured",
            message="GEMINI_API_KEY is not configured.",
        )

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        return VideoResult(
            provider="veo",
            status="dependency_missing",
            message="Install the video extra with pip install -e '.[video]'.",
        )

    try:
        client = genai.Client(api_key=settings.gemini_api_key)
        operation = client.models.generate_videos(
            model="veo-3.1-generate-preview",
            source=types.GenerateVideosSource(prompt=prompt),
            config=types.GenerateVideosConfig(
                aspect_ratio=aspect_ratio,
                duration_seconds=8,
                number_of_videos=1,
            ),
        )

        while not operation.done:
            time.sleep(10)
            operation = client.operations.get(operation)

        generated = getattr(operation.response, "generated_videos", None) or []
        if not generated:
            return VideoResult(
                provider="veo",
                status="no_video",
                message="Generation completed without a returned video object.",
            )

        generated_video = generated[0]
        video = generated_video.video
        client.files.download(file=video)

        filename = f"{uuid4().hex}.mp4"
        path = Path(settings.output_directory) / filename
        video.save(path)

        return VideoResult(
            provider="veo",
            status="completed",
            uri=getattr(video, "uri", None),
            file_name=filename,
        )
    except Exception as exc:
        return VideoResult(provider="veo", status="error", message=str(exc))
