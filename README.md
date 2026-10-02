# MAHER CONTENT BRAIN

A mobile-first agentic content system for the What If + Transformation + Timelapse + Curiosity YouTube niche.

## Current capabilities

- Natural-language requests from a phone browser.
- Automatic routing between idea discovery and idea building.
- Live web research using the OpenAI Agents SDK web-search tool.
- Creative strategy stage for visual-first concepts.
- Shot-by-shot production prompt compilation.
- Red-team visual QA and automatic repair pass.
- Persistent lightweight project memory in SQLite.
- Responsive browser interface.
- Docker runtime and GitHub Actions CI.

## Flow

Request → Research → Strategy → Prompt Compiler → Visual QA → Repair → Production Pack

The project deliberately starts with orchestration instead of training a new model from scratch. The brain is the combination of a strong model, tools, memory, constraints, and workflow.

## Setup

1. Copy .env.example to .env.
2. Put the OpenAI API key in .env.
3. Install the development package with pip install -e ".[dev]".
4. Run uvicorn app.main:app --reload.
5. Open the server URL from the iPhone browser.

For server deployment, provide OPENAI_API_KEY as a platform secret. Never commit secrets.

## Model policy

Default model is GPT-5.6 Luna for cost control. Strategy and repair default to GPT-5.6 Terra. The model IDs are configurable with environment variables, so the brain can be upgraded without changing application code. Current OpenAI docs list GPT-5.6 Luna, Terra, and Sol as available Responses API models; Sol is the highest-intelligence option among those three. 

## Planned upgrades

- Structured YouTube Data API enrichment.
- Competitor watchlists and trend snapshots.
- Source registry with URLs and timestamps.
- Copy/near-duplicate idea detection.
- Storyboard frame generation.
- Direct Veo 3.1 rendering.
- Automatic shot assembly.
- Thumbnail generation.
- Shorts extraction.
- Channel analytics ingestion.
- Retention-driven strategy memory.
- Background jobs for long renders.
- Authentication and private storage.
