from pathlib import Path

from app.brain import ContentBrain
from app.models import BrainRequest, ProductionPack, ShotPrompt
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


def test_production_pack_validates_veo_shot_durations():
    pack = ProductionPack(
        title="Tomato growth",
        target_duration_seconds=24,
        visual_style="cinematic photorealistic macro",
        shots=[
            ShotPrompt(
                shot_id="S01",
                duration_seconds=8,
                purpose="hook",
                prompt="Macro underground tomato seed in rich soil, dramatic roots forming.",
            ),
            ShotPrompt(
                shot_id="S02",
                duration_seconds=8,
                purpose="sprout",
                prompt="Time-lapse tomato sprout breaking through soil, continuous camera.",
            ),
            ShotPrompt(
                shot_id="S03",
                duration_seconds=8,
                purpose="payoff",
                prompt="Mature tomato fruit filling the frame, realistic harvest moment.",
            ),
        ],
    )
    assert len(pack.shots) == 3
