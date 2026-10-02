from typing import Literal
from pydantic import BaseModel, Field

Mode = Literal["auto", "idea", "build", "explore"]


class BrainRequest(BaseModel):
    message: str = Field(min_length=1)
    mode: Mode = "auto"
    reference_image_data_url: str | None = None
    save_to_memory: bool = True


class ShotPrompt(BaseModel):
    shot_id: str
    duration_seconds: int = Field(ge=1, le=8)
    purpose: str
    prompt: str
    negative_constraints: list[str] = []
    transition: str = ""


class ProductionPack(BaseModel):
    title: str
    aspect_ratio: Literal["16:9", "9:16"] = "16:9"
    target_duration_seconds: int = Field(ge=1)
    visual_style: str
    continuity_rules: list[str] = []
    shots: list[ShotPrompt] = Field(min_length=1, max_length=60)


class BrainResponse(BaseModel):
    mode: str
    output: str
    production_pack: ProductionPack | None = None
    memory_saved: bool = False
    stages: list[str] = []


class MemoryInput(BaseModel):
    label: str
    content: str = Field(min_length=1)


class VideoRequest(BaseModel):
    prompt: str = Field(min_length=1)
    aspect_ratio: Literal["16:9", "9:16"] = "16:9"


class RenderPackRequest(BaseModel):
    shots: list[ShotPrompt] = Field(min_length=1, max_length=60)
    aspect_ratio: Literal["16:9", "9:16"] = "16:9"
    limit: int = Field(default=1, ge=1, le=60)
