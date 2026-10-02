import json

from agents import Runner

from .agents import NICHE_DNA, build_agents
from .config import settings
from .models import BrainRequest, BrainResponse, ProductionPack
from .storage import MemoryStore
from .tools.youtube import search_youtube


class ContentBrain:
    def __init__(self, memory: MemoryStore):
        self.memory = memory

    @staticmethod
    def _input_with_image(text: str, image_data_url: str | None):
        content = [{"type": "input_text", "text": text}]
        if image_data_url:
            content.append({"type": "input_image", "image_url": image_data_url})
        return [{"role": "user", "content": content}]

    @staticmethod
    def _mode(request: BrainRequest) -> str:
        if request.mode != "auto":
            return request.mode
        text = request.message.lower()
        idea_phrases = (
            "ما عندي فكرة",
            "ماعندي فكرة",
            "اعطيني فكرة",
            "أعطني فكرة",
            "no idea",
            "surprise me",
        )
        return "idea" if any(p in text for p in idea_phrases) else "build"

    async def _run(self, agent, prompt, image_data_url=None):
        payload = (
            self._input_with_image(prompt, image_data_url)
            if image_data_url
            else prompt
        )
        result = await Runner.run(agent, payload)
        return result.final_output

    async def execute(self, request: BrainRequest) -> BrainResponse:
        if not settings.openai_api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is missing. Copy .env.example to .env and add your key."
            )

        mode = self._mode(request)
        agents = build_agents()
        memory = self.memory.context()

        youtube_signals = []
        youtube_error = None
        if settings.youtube_api_key:
            try:
                youtube_query = request.message if mode != "idea" else (
                    "AI What If transformation timelapse viral YouTube"
                )
                youtube_signals = await search_youtube(
                    query=youtube_query,
                    max_results=10,
                    order="viewCount",
                )
            except Exception as exc:
                youtube_error = str(exc)

        structured_youtube = "\n".join(
            f"- {x['title']} | {x['channel']} | views={x['views']} | {x['url']}"
            for x in youtube_signals
        ) or "No structured YouTube API data configured; use live web research instead."

        if youtube_error:
            structured_youtube += f"\nYouTube API warning: {youtube_error}"

        base = f"""
PROJECT MEMORY:
{memory}

{NICHE_DNA}

STRUCTURED YOUTUBE SIGNALS:
{structured_youtube}

OWNER REQUEST:
{request.message}
"""

        stages: list[str] = []

        research = await self._run(
            agents["research"],
            f"""Research this request for our content channel.
Mode: {mode}

{base}

Use the structured YouTube signals when present, but verify and extend them with web research.
Return a research brief with useful current signals, examples, and production patterns.
""",
            request.reference_image_data_url,
        )
        stages.append("research")

        strategy = await self._run(
            agents["strategy"],
            f"""Create the best concept from this request.

{base}

RESEARCH BRIEF:
{research}
""",
        )
        stages.append("strategy")

        draft_pack = await self._run(
            agents["prompt"],
            f"""Compile a production-ready ProductionPack.

OWNER REQUEST:
{request.message}

STRATEGY:
{strategy}

RESEARCH:
{research}
""",
        )
        if not isinstance(draft_pack, ProductionPack):
            raise TypeError("Prompt Compiler did not return a ProductionPack.")
        stages.append("prompt_compilation")

        critique = await self._run(
            agents["critic"],
            f"""Audit this ProductionPack.

OWNER REQUEST:
{request.message}

STRATEGY:
{strategy}

PRODUCTION PACK:
{draft_pack.model_dump_json(indent=2)}
""",
        )
        stages.append("quality_check")

        final_pack = await self._run(
            agents["repair"],
            f"""REPAIR THIS ProductionPack.

STRATEGY:
{strategy}

DRAFT:
{draft_pack.model_dump_json(indent=2)}

CRITIC:
{critique}

Return the complete corrected ProductionPack.
""",
        )
        if not isinstance(final_pack, ProductionPack):
            raise TypeError("Prompt Repair Agent did not return a ProductionPack.")
        stages.append("repair")

        pack_json = json.dumps(final_pack.model_dump(), ensure_ascii=False, indent=2)
        output = f"""# MAHER CONTENT BRAIN — {mode.upper()}

## Research
{research}

## Creative Strategy
{strategy}

## Final Production Pack
{pack_json}

## QA Report
{critique}

## Generation Checklist
- Render shots independently when useful.
- Preserve subject identity, environment, camera direction, and time progression.
- Review the first 3 seconds before rendering the entire sequence.
- Never copy a competitor's exact title, thumbnail, script, or shot sequence.
"""

        saved = False
        if request.save_to_memory:
            self.memory.log_run(mode, request.message, output)
            self.memory.add_memory(
                "last_run",
                f"Mode={mode}; request={request.message}; shots={len(final_pack.shots)}",
            )
            saved = True

        return BrainResponse(
            mode=mode,
            output=output,
            production_pack=final_pack,
            memory_saved=saved,
            stages=stages,
        )
