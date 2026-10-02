# MAHER CONTENT BRAIN

Mobile-first agentic content system for the What If + Transformation + Timelapse + Curiosity niche.

## Primary deployment: $0-first Cloudflare Edition

Use the `cloudflare/` directory as the main deployment:

- Cloudflare Workers — mobile UI + API.
- Cloudflare Workflows — durable multi-step orchestration.
- Cloudflare D1 — persistent jobs, memory, ideas and source registry.
- Gemini API — default AI provider.
- YouTube Data API — optional only.
- OpenAI API — optional, explicitly blocked by the cost guard by default.
- Video API generation — intentionally OFF in the $0 path.

The old FastAPI/Render implementation remains under `app/` as a legacy/local path.

## Current brain pipeline

Owner request
→ Research
→ Creative Director + Strategy
→ Production Pack
→ Visual QA + Repair
→ Persistent Memory

The Production Pack contains:
- concept and viewer question
- 0–3 second visual hook
- script
- long-form plan
- Shorts cut plan
- title variants
- thumbnail concept
- continuity rules
- shot-by-shot AI video prompts

## Free-first rule

The cloud version defaults to Gemini and has an application-level daily call guard.

OpenAI is not used merely because an OpenAI key exists. To enable it intentionally you must set:

`AI_PROVIDER=openai`
`ENABLE_OPENAI_API=true`

That is a paid API path and is outside the $0 requirement.

## Start here

Read the complete mobile-friendly deployment guide:

`docs/DEPLOY_CLOUDFLARE.md`

Repository:
https://github.com/mahr18/automatic-creators

Cloudflare app:
`cloudflare/`

## API

- GET /api/health
- POST /api/jobs
- GET /api/jobs/:id
- GET /api/memory
- POST /api/memory
- GET /api/quota

## Security

Never commit API keys.

Use Cloudflare Secrets for:
- `GEMINI_API_KEY`
- `BRAIN_ACCESS_TOKEN`
- optionally `OPENAI_API_KEY`

The browser only receives the non-secret access token you type into the app. Provider keys stay server-side.

## Project links

GitHub:
https://github.com/mahr18/automatic-creators

Google AI Studio:
https://aistudio.google.com/

Gemini API keys:
https://aistudio.google.com/apikey

Gemini documentation:
https://ai.google.dev/gemini-api/docs

Cloudflare Dashboard:
https://dash.cloudflare.com/

Cloudflare Workers:
https://developers.cloudflare.com/workers/

Cloudflare D1:
https://developers.cloudflare.com/d1/

Cloudflare Workflows:
https://developers.cloudflare.com/workflows/

Cloudflare Workers Builds:
https://developers.cloudflare.com/workers/ci-cd/builds/

OpenAI API keys:
https://platform.openai.com/api-keys
