from typing import Literal
from pydantic import BaseModel, Field

Mode = Literal["auto", "idea", "build", "explore"]


class BrainRequest(BaseModel):
    message: str = Field(min_length=1)
    mode: Mode = "auto"
    reference_image_data_url: str | None = None
    save_to_memory: bool = True


class BrainResponse(BaseModel):
    mode: str
    output: str
    memory_saved: bool = False
    stages: list[str] = []


class MemoryInput(BaseModel):
    label: str
    content: str = Field(min_length=1)


class VideoRequest(BaseModel):
    prompt: str = Field(min_length=1)
    aspect_ratio: Literal["16:9", "9:16"] = "16:9"
