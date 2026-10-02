# MAHER CONTENT BRAIN

A mobile-first agentic content system for the What If + Transformation + Timelapse + Curiosity YouTube niche.

## Current capabilities

- Natural-language requests from a phone browser.
- Automatic routing between idea discovery and idea building.
- Live web research using the OpenAI Agents SDK web-search tool.
- Structured YouTube Data API enrichment when YOUTUBE_API_KEY is configured.
- Creative strategy stage for visual-first concepts.
- Machine-readable shot-by-shot ProductionPack output.
- Red-team visual QA and automatic repair pass.
- Persistent lightweight project memory in SQLite.
- Optional Veo 3.1 shot rendering endpoint.
- Responsive browser interface.
- Docker runtime and GitHub Actions CI.

## Flow

Request → Research → Strategy → Prompt Compiler → Visual QA → Repair → Render Pack

The project deliberately starts with orchestration instead of training a new model from scratch. The brain is the combination of a strong model, tools, memory, constraints, and workflow.

## Setup

1. Copy .env.example to .env.
2. Put the OpenAI API key in .env.
3. Optionally add YOUTUBE_API_KEY for structured YouTube metrics.
4. Optionally add GEMINI_API_KEY and install the video extra for Veo rendering.
5. Install the development package with pip install -e ".[dev]".
6. Run uvicorn app.main:app --reload.
7. Open the server URL from the iPhone browser.

For server deployment, provide secrets as platform environment variables. Never commit API keys.

## Model policy

Default is GPT-5.6 Luna for cost control. Strategy and repair default to GPT-5.6 Terra. Model IDs are configurable without code changes. OpenAI's current model catalog lists GPT-5.6 Luna, Terra, and Sol for the Responses API; Sol is the highest-intelligence option among those three.

## Current API

- GET /api/health
- POST /api/brain
- POST /api/video
- POST /api/video/render-pack
- POST /api/memory
- GET /api/memory

## Next upgrades

- Competitor watchlists and trend snapshots.
- Source registry with URLs and timestamps.
- Copy/near-duplicate idea detection.
- Storyboard frame generation.
- First/last-frame continuity.
- Automatic multi-shot video assembly.
- Thumbnail generation.
- Shorts extraction.
- Channel analytics ingestion.
- Retention-driven strategy memory.
- Background job queue for long renders.
- Authentication and private storage.
