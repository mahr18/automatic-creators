# MAHER CONTENT BRAIN — Cloudflare Edition

This is the primary $0-first deployment for the project.

## Stack
- Cloudflare Workers — API + mobile UI
- Cloudflare Workflows — durable orchestration
- Cloudflare D1 — persistent memory/jobs
- Gemini API — default AI provider
- Optional YouTube Data API — only if configured
- Optional OpenAI API — explicitly disabled by the safety guard by default

## Free-first safety
The code defaults to Gemini and refuses OpenAI unless `ENABLE_OPENAI_API=true`.
Video API generation is not wired into the default free path because model API video generation can be metered separately from a consumer Google AI subscription. Use the generated shot prompts in your Google Flow/Veo UI when that is included with your subscription.

See `../docs/DEPLOY_CLOUDFLARE.md` for the exact setup.
