from __future__ import annotations

from dataclasses import dataclass

from .config import settings


@dataclass
class VideoResult:
    provider: str
    status: str
    uri: str | None = None
    message: str | None = None


async def generate_with_veo(prompt: str, aspect_ratio: str = "16:9") -> VideoResult:
    """Optional Veo 3.1 adapter. Kept isolated so the brain can swap providers later."""
    if not settings.gemini_api_key:
        return VideoResult(
            provider="veo",
            status="not_configured",
            message="GEMINI_API_KEY is not configured.",
        )

    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:
        return VideoResult(
            provider="veo",
            status="dependency_missing",
            message="Install the video extra: pip install -e '.[video]'",
        )

    try:
        client = genai.Client(api_key=settings.gemini_api_key)
        operation = client.models.generate_videos(
            model="veo-3.1-generate-preview",
            prompt=prompt,
            config=types.GenerateVideosConfig(aspect_ratio=aspect_ratio),
        )
        while not operation.done:
            operation = client.operations.get(operation)

        response = getattr(operation, "response", None)
        generated = getattr(response, "generated_videos", None) or []
        if not generated:
            return VideoResult(
                provider="veo",
                status="no_video",
                message="Generation completed without a returned video object.",
            )

        video = getattr(generated[0], "video", None)
        uri = getattr(video, "uri", None)
        return VideoResult(
            provider="veo",
            status="completed" if uri else "completed_no_uri",
            uri=uri,
        )
    except Exception as exc:
        return VideoResult(provider="veo", status="error", message=str(exc))
