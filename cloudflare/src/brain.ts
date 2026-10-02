import { WorkflowEntrypoint } from "cloudflare:workers";
import type { WorkflowEvent, WorkflowStep } from "cloudflare:workers";

import { generateJson, productionPackSchema, qualitySchema, researchSchema } from "./gemini";
import { optionalYouTubeSignals } from "./youtube";

type BrainParams = {
  jobId: string;
  message: string;
  mode: "auto" | "idea" | "build" | "explore";
  referenceImageDataUrl?: string | null;
};

const NICHE_DNA = `
MAHER CONTENT BRAIN
Core niche: What If + Transformation + Timelapse + Curiosity.
Audience: global, visual-first, faceless.
Style: cinematic, photorealistic, satisfying transformation, strong visual hooks.
Production principle: make the idea understandable from the images before relying on narration.
Originality: study patterns, never copy a creator's exact title, thumbnail, script or shot sequence.
Every recommendation must distinguish observed evidence from hypotheses.
`;

function now(): string {
  return new Date().toISOString();
}

function safeJson(value: unknown): string {
  return JSON.stringify(value);
}

async function updateJob(env: Env, id: string, fields: Record<string, unknown>) {
  const columns = Object.keys(fields);
  const values = Object.values(fields);
  const set = columns.map(k => `${k} = ?`).join(", ");
  await env.DB.prepare(`UPDATE jobs SET ${set}, updated_at = ? WHERE id = ?`)
    .bind(...values, now(), id)
    .run();
}

async function usageGuard(env: Env, provider: string): Promise<void> {
  const limit = Math.max(1, Number(env.GEMINI_DAILY_CALL_GUARD || "40"));
  const day = new Date().toISOString().slice(0, 10);
  const row = await env.DB.prepare("SELECT calls FROM usage WHERE day = ? AND provider = ?")
    .bind(day, provider)
    .first<{ calls: number }>();
  const calls = Number(row?.calls || 0);
  if (calls >= limit) {
    throw new Error(`App safety limit reached for ${provider} today (${limit} calls).`);
  }
  await env.DB.prepare(
    "INSERT INTO usage(day, provider, calls) VALUES (?, ?, 1) ON CONFLICT(day, provider) DO UPDATE SET calls = calls + 1"
  ).bind(day, provider).run();
}

async function ai(env: Env, prompt: string, schema: Record<string, unknown>, image?: string | null) {
  const provider = (env.AI_PROVIDER || "gemini").toLowerCase();
  await usageGuard(env, provider);
  return generateJson(env, prompt, schema, image);
}

function modeFor(message: string, mode: BrainParams["mode"]): BrainParams["mode"] {
  if (mode !== "auto") return mode;
  const t = message.toLowerCase();
  return /(ما عندي فكرة|ماعندي فكرة|أعطني فكرة|اعطيني فكرة|no idea|surprise me)/i.test(t) ? "idea" : "build";
}

function ideaFingerprint(title: string): string {
  return title
    .toLowerCase()
    .replace(/[^a-z0-9\u0600-\u06ff]+/g, " ")
    .trim()
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 10)
    .join("-");
}

export class BrainWorkflow extends WorkflowEntrypoint<Env, BrainParams> {
  async run(event: WorkflowEvent<BrainParams>, step: WorkflowStep) {
    const { jobId, message, referenceImageDataUrl } = event.payload;
    const mode = modeFor(message, event.payload.mode);

    try {
      await updateJob(this.env, jobId, { status: "running", mode });

      const research = await step.do("research", { retries: { limit: 2, delay: "3 seconds", backoff: "linear" } }, async () => {
        let youtube = { items: [] as any[], sources: [] as any[] };
        let youtubeWarning = "";
        try {
          youtube = await optionalYouTubeSignals(this.env, message);
        } catch (error) {
          youtubeWarning = String(error instanceof Error ? error.message : error);
        }

        const recent = await this.env.DB.prepare(
          "SELECT title, fingerprint FROM ideas ORDER BY created_at DESC LIMIT 25"
        ).all<{ title: string; fingerprint: string }>();

        const publicSignals = youtube.items.length
          ? safeJson(youtube.items)
          : "No YouTube API configured. Do not fabricate live YouTube metrics.";

        return {
          research: await ai(
            this.env,
            `${NICHE_DNA}

OWNER REQUEST:
${message}

MODE:
${mode}

RECENT INTERNAL TITLES (avoid near-duplicates):
${safeJson(recent.results || [])}

STRUCTURED PUBLIC YOUTUBE SIGNALS:
${publicSignals}

YOUTUBE WARNING:
${youtubeWarning || "none"}

Build an evidence-aware research brief. When no live YouTube data exists, explicitly say so and use stable creative/production reasoning rather than pretending it is current. Return gaps and risks that a creative strategist should solve.

Return JSON matching the required schema.`,
            researchSchema,
            referenceImageDataUrl
          ),
          sources: youtube.sources
        };
      });

      const packDraft = await step.do("strategy-and-production", { retries: { limit: 2, delay: "3 seconds", backoff: "linear" } }, async () => {
        return await ai(
          this.env,
          `${NICHE_DNA}

OWNER REQUEST:
${message}

MODE:
${mode}

RESEARCH:
${safeJson(research.research)}

You are simultaneously:
1) Creative Director
2) Scriptwriter
3) Visual Storyboard Director
4) Prompt Engineer

Create one original concept that can actually be produced with current AI video tools.

Requirements:
- Hook must be visually legible in 0-3 seconds.
- Escalate the transformation rather than repeat the same shot.
- Include a concrete payoff/end.
- Produce an organic long-form plan and a 1-3 minute Shorts cut plan.
- Give title variants and a thumbnail concept.
- Prompts must cover subject, action, camera, lens, composition, lighting, environment, materials, motion, depth, continuity, time progression and transition.
- Adjacent shots must maintain identity, geography, direction and time progression.
- Use 4/6/8 second shots only.
- Do not claim exact performance outcomes.

Return complete JSON matching the ProductionPack schema.`,
          productionPackSchema,
          referenceImageDataUrl
        );
      });

      const final = await step.do("critic-repair", { retries: { limit: 2, delay: "3 seconds", backoff: "linear" } }, async () => {
        return await ai(
          this.env,
          `${NICHE_DNA}

OWNER REQUEST:
${message}

DRAFT PRODUCTION PACK:
${safeJson(packDraft)}

Act as a hostile visual QA editor. Do not praise the draft.
Check hook strength, visual novelty, clarity, physical plausibility, prompt specificity, continuity, camera consistency, AI-generation difficulty, repetition, originality risk, payoff and first-seconds attention.

Then REPAIR the pack yourself. The final_pack must be fully self-contained and production-ready, not a patch.

Return:
- integer QA scores from 0-100
- concrete failures
- concrete repairs
- complete corrected final_pack

Return JSON matching the required schema.`,
          qualitySchema,
          referenceImageDataUrl
        );
      });

      const finalPack = (final.final_pack || packDraft) as Record<string, unknown>;
      const titles = Array.isArray(finalPack.title_options) ? finalPack.title_options : [];
      const title = String(titles[0] || finalPack.concept || "MAHER CONTENT BRAIN");
      const fingerprint = ideaFingerprint(title);

      await step.do("persist", async () => {
        await updateJob(this.env, jobId, {
          status: "completed",
          result_json: safeJson({
            mode,
            research: research.research,
            sources: research.sources,
            production_pack: finalPack,
            qa: final.qa,
            failures: final.failures,
            repairs: final.repairs
          })
        });

        await this.env.DB.prepare(
          "INSERT INTO ideas(title, fingerprint, created_at) VALUES (?, ?, ?)"
        ).bind(title, fingerprint, now()).run();

        for (const source of research.sources || []) {
          await this.env.DB.prepare(
            "INSERT INTO sources(job_id, source_type, title, url, metadata_json, created_at) VALUES (?, ?, ?, ?, ?, ?)"
          ).bind(
            jobId,
            "youtube",
            String(source.title || ""),
            String(source.url || ""),
            safeJson(source),
            now()
          ).run();
        }

        await this.env.DB.prepare(
          "INSERT INTO memories(label, content, created_at) VALUES (?, ?, ?)"
        ).bind(
          "latest_run",
          `mode=${mode}; title=${title}; concept=${String(finalPack.concept || "")}`,
          now()
        ).run();
      });

      return { ok: true, jobId, mode, result: finalPack };
    } catch (error) {
      const errorText = error instanceof Error ? error.message : String(error);
      await updateJob(this.env, jobId, { status: "failed", error: errorText });
      throw error;
    }
  }
}
