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

Current defaults use the GPT-6 family:
- Research: gpt-6-luna
- Strategy: gpt-6.1-sol
- Prompt compiler: gpt-6-luna
- Critic: gpt-6.1-sol
- Repair: gpt-6.1-sol

For maximum reasoning, set the Strategy/Critic/Repair roles to gpt-6-astra. OpenAI currently describes GPT-6 Astra as its highest-intelligence model, GPT-6.1 Sol as near-Astra at lower cost, and GPT-6 Luna as the efficient high-volume option.

## Current API

- GET /api/health
- POST /api/brain
- POST /api/video
- POST /api/video/render-pack
- POST /api/memory
- GET /api/memory

## Security and deployment notes

The API is protected by BRAIN_ACCESS_TOKEN so a public URL cannot be used anonymously against your OpenAI/Gemini quota.

Render Free uses an ephemeral filesystem, so local SQLite memory and locally rendered MP4 files can disappear after restarts, redeploys, or idle spin-down. Use external persistent storage before relying on the memory as a permanent brain. Render documents this Free-service limitation.

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
