from agents import Runner

from .agents import NICHE_DNA, build_agents
from .config import settings
from .models import BrainRequest, BrainResponse
from .storage import MemoryStore


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

        base = f"""
PROJECT MEMORY:
{memory}

{NICHE_DNA}

OWNER REQUEST:
{request.message}
"""

        stages: list[str] = []

        research = await self._run(
            agents["research"],
            f"""Research this request for our content channel.
Mode: {mode}

{base}

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

        prompt_pack = await self._run(
            agents["prompt"],
            f"""Compile a production-ready prompt pack.

OWNER REQUEST:
{request.message}

STRATEGY:
{strategy}

RESEARCH:
{research}
""",
        )
        stages.append("prompt_compilation")

        critique = await self._run(
            agents["critic"],
            f"""Audit this production pack.

OWNER REQUEST:
{request.message}

STRATEGY:
{strategy}

PROMPT PACK:
{prompt_pack}
""",
        )
        stages.append("quality_check")

        final_pack = await self._run(
            agents["repair"],
            f"""REPAIR THE FOLLOWING PRODUCTION PACK.

STRATEGY:
{strategy}

DRAFT:
{prompt_pack}

CRITIC:
{critique}

Return the complete corrected production pack.
""",
        )
        stages.append("repair")

        output = f"""# MAHER CONTENT BRAIN — {mode.upper()}

## Research
{research}

## Creative Strategy
{strategy}

## Final Production Pack
{final_pack}

## QA Report
{critique}

## Generation Checklist
- Generate shots separately when useful.
- Keep subject identity, environment, camera direction, and time progression consistent.
- Review the first 3 seconds before rendering the full sequence.
- Do not copy a competitor's exact title, thumbnail, script, or shot sequence.
"""

        saved = False
        if request.save_to_memory:
            self.memory.log_run(mode, request.message, output)
            self.memory.add_memory(
                "last_run",
                f"Mode={mode}; request={request.message}; stages={','.join(stages)}",
            )
            saved = True

        return BrainResponse(
            mode=mode,
            output=output,
            memory_saved=saved,
            stages=stages,
        )
