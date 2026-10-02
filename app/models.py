from typing import Literal

from pydantic import BaseModel, Field

Mode = Literal["auto", "idea", "build", "explore"]


class BrainRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12000)
    mode: Mode = "auto"
    reference_image_data_url: str | None = Field(default=None, max_length=9000000)
    save_to_memory: bool = True


class ShotPrompt(BaseModel):
    shot_id: str = Field(min_length=1, max_length=40)
    duration_seconds: Literal[4, 6, 8] = 8
    purpose: str
    prompt: str = Field(min_length=20)
    negative_constraints: list[str] = Field(default_factory=list)
    transition: str = ""


class ProductionPack(BaseModel):
    title: str
    aspect_ratio: Literal["16:9", "9:16"] = "16:9"
    target_duration_seconds: int = Field(ge=4, le=900)
    visual_style: str
    continuity_rules: list[str] = Field(default_factory=list)
    shots: list[ShotPrompt] = Field(min_length=1, max_length=60)


class BrainResponse(BaseModel):
    mode: str
    output: str
    production_pack: ProductionPack | None = None
    memory_saved: bool = False
    stages: list[str] = Field(default_factory=list)


class MemoryInput(BaseModel):
    label: str = Field(min_length=1, max_length=80)
    content: str = Field(min_length=1, max_length=20000)


class VideoRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=12000)
    aspect_ratio: Literal["16:9", "9:16"] = "16:9"


class RenderPackRequest(BaseModel):
    shots: list[ShotPrompt] = Field(min_length=1, max_length=60)
    aspect_ratio: Literal["16:9", "9:16"] = "16:9"
    limit: int = Field(default=1, ge=1, le=8)
