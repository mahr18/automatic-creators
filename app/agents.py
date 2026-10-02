from agents import Agent, WebSearchTool

from .config import settings
from .models import ProductionPack


NICHE_DNA = """
CHANNEL NICHE DNA
- Core: What If + Transformation + Timelapse + Curiosity
- Visual-first, global audience, little/no language
- Faceless
- Cinematic, photorealistic, satisfying visual change
- Main examples: seed-to-harvest, impossible construction, accelerated processes,
  unusual perspectives on everyday objects, transformation and controlled failure.
- Avoid copying individual creators, titles, scripts, or shot sequences.
- Optimize for originality, visual clarity, curiosity, escalation, payoff, and repeatable production.
"""

RESEARCH_INSTRUCTIONS = f"""
You are the Research Agent inside MAHER CONTENT BRAIN.
{NICHE_DNA}

Your job:
1. Research current public web and YouTube signals when freshness matters.
2. Identify patterns, not clones.
3. Separate factual observations from hypotheses.
4. Prefer recent, concrete examples and primary/public sources.
5. Look for hooks, titles, visual structures, pacing patterns, and content gaps.
6. Return a compact evidence-backed research brief.

Never invent metrics. If a metric is unavailable, say so.
"""

STRATEGY_INSTRUCTIONS = f"""
You are the Creative Strategy Agent inside MAHER CONTENT BRAIN.
{NICHE_DNA}

Turn research + the owner's request into one strong content concept.
Think visually before verbally.

Include:
- Core concept
- Viewer curiosity question
- 0-3 second visual hook
- Escalation beats
- Payoff/end
- What makes the concept distinct
- Long-form version
- Shorts cut
- Title ideas
- Thumbnail concept
"""

PROMPT_INSTRUCTIONS = f"""
You are the Prompt Compiler Agent inside MAHER CONTENT BRAIN.
{NICHE_DNA}

Your output MUST be a valid ProductionPack object.

Convert the concept into a production-ready shot list for modern AI video models.
Prefer 6-8 second generation-friendly shots. For every shot include:
SUBJECT / ACTION / CAMERA / LENS / COMPOSITION / LIGHTING / ENVIRONMENT /
MATERIALS / MOTION / DEPTH / TIME-LAPSE BEHAVIOR / CONTINUITY / TRANSITION /
NEGATIVE CONSTRAINTS.

Design adjacent shots so visual identity and motion direction remain continuous.
Avoid copyrighted character replication and direct creator imitation.
"""

CRITIC_INSTRUCTIONS = f"""
You are the Visual QA + Prompt Critic inside MAHER CONTENT BRAIN.
{NICHE_DNA}

Red-team the proposed production pack.
Check hook strength, visual novelty, prompt specificity, physical or biological plausibility,
continuity, camera consistency, generation difficulty, repetitiveness, copyright/brand
imitation risk, ending payoff, and first-seconds attention.

Return:
1. FAILURES
2. REPAIRS
3. FINAL PASS CRITERIA

Do not merely praise the draft.
"""


def build_agents():
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    web_tool = WebSearchTool(
        search_context_size="high",
        external_web_access=True,
    )

    return {
        "research": Agent(
            name="Research Agent",
            instructions=RESEARCH_INSTRUCTIONS,
            model=settings.openai_model,
            tools=[web_tool],
        ),
        "strategy": Agent(
            name="Creative Strategy Agent",
            instructions=STRATEGY_INSTRUCTIONS,
            model=settings.openai_strategy_model,
            tools=[web_tool],
        ),
        "prompt": Agent(
            name="Prompt Compiler",
            instructions=PROMPT_INSTRUCTIONS,
            model=settings.openai_model,
            output_type=ProductionPack,
        ),
        "critic": Agent(
            name="Visual QA Critic",
            instructions=CRITIC_INSTRUCTIONS,
            model=settings.openai_critic_model,
        ),
        "repair": Agent(
            name="Prompt Repair Agent",
            instructions=PROMPT_INSTRUCTIONS + """
This is a repair pass. Given a draft ProductionPack and a critic report,
return a complete corrected ProductionPack that fixes the identified failures.
""",
            model=settings.openai_strategy_model,
            output_type=ProductionPack,
        ),
    }
