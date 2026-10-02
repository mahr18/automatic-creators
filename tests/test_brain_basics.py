from pathlib import Path

from app.brain import ContentBrain
from app.models import BrainRequest
from app.storage import MemoryStore


def test_auto_mode_detects_idea_request(tmp_path: Path):
    store = MemoryStore(tmp_path / "brain.sqlite3")
    brain = ContentBrain(store)
    request = BrainRequest(message="ما عندي فكرة")
    assert brain._mode(request) == "idea"


def test_auto_mode_detects_build_request(tmp_path: Path):
    store = MemoryStore(tmp_path / "brain.sqlite3")
    brain = ContentBrain(store)
    request = BrainRequest(message="أريد فيديو عن الطماطم من البذرة للحصاد")
    assert brain._mode(request) == "build"


def test_memory_roundtrip(tmp_path: Path):
    store = MemoryStore(tmp_path / "brain.sqlite3")
    store.add_memory("niche", "What If + Transformation")
    assert "What If + Transformation" in store.context()
