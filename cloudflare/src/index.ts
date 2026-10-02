import { BrainWorkflow } from "./brain";

function cors(headers: Headers) {
  headers.set("access-control-allow-origin", "*");
  headers.set("access-control-allow-methods", "GET,POST,OPTIONS");
  headers.set("access-control-allow-headers", "Authorization,Content-Type");
}

function json(data: unknown, init: ResponseInit = {}) {
  const headers = new Headers(init.headers);
  headers.set("content-type", "application/json; charset=utf-8");
  cors(headers);
  return new Response(JSON.stringify(data), { ...init, headers });
}

function auth(request: Request, env: Env): Response | null {
  const expected = env.BRAIN_ACCESS_TOKEN;
  if (!expected) return json({ error: "BRAIN_ACCESS_TOKEN is not configured." }, { status: 503 });
  const value = request.headers.get("authorization") || "";
  const [scheme, token] = value.split(" ", 2);
  if (scheme?.toLowerCase() !== "bearer" || !token || token !== expected) {
    return json({ error: "Unauthorized." }, { status: 401 });
  }
  return null;
}

function normalizeMode(value: unknown): "auto" | "idea" | "build" | "explore" {
  return value === "idea" || value === "build" || value === "explore" ? value : "auto";
}

function numberOrNull(value: unknown): number | null {
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
}

export { BrainWorkflow };

export default {
  async fetch(request, env, ctx): Promise<Response> {
    if (request.method === "OPTIONS") return json(null, { status: 204 });

    const url = new URL(request.url);
    if (url.pathname === "/api/health" && request.method === "GET") {
      return json({
        ok: true,
        provider: env.AI_PROVIDER || "gemini",
        gemini_configured: Boolean(env.GEMINI_API_KEY),
        openai_configured: Boolean(env.OPENAI_API_KEY),
        openai_enabled: env.ENABLE_OPENAI_API === "true",
        youtube_configured: Boolean(env.YOUTUBE_API_KEY),
        youtube_api_optional: true,
        youtube_rss_watchlist: true,
        video_api_enabled: env.ENABLE_VIDEO_API === "true",
        gemini_model: env.GEMINI_TEXT_MODEL || "gemini-3.8-flash",
        gemini_daily_app_guard: Number(env.GEMINI_DAILY_CALL_GUARD || "40")
      });
    }

    if (!url.pathname.startsWith("/api/")) return env.ASSETS.fetch(request);

    const denied = auth(request, env);
    if (denied) return denied;

    if (url.pathname === "/api/jobs" && request.method === "POST") {
      const body = (await request.json()) as {
        message?: string;
        mode?: string;
        reference_image_data_url?: string | null;
      };

      const message = String(body.message || "").trim();
      if (!message) return json({ error: "message is required" }, { status: 400 });
      if (message.length > 12000) return json({ error: "message is too long" }, { status: 400 });

      const image = body.reference_image_data_url || null;
      if (image && image.length > 1400000) return json({ error: "reference image is too large; use a smaller image" }, { status: 413 });

      const jobId = crypto.randomUUID();
      const mode = normalizeMode(body.mode);
      const now = new Date().toISOString();

      await env.DB.prepare(
        "INSERT INTO jobs(id, mode, request, status, created_at, updated_at) VALUES (?, ?, ?, 'queued', ?, ?)"
      ).bind(jobId, mode, message, now, now).run();

      const instance = await env.BRAIN_WORKFLOW.create({
        id: jobId,
        params: {
          jobId,
          message,
          mode,
          referenceImageDataUrl: image
        }
      });

      return json({ ok: true, job_id: instance.id, status: "queued" }, { status: 202 });
    }

    const match = url.pathname.match(/^\/api\/jobs\/([^/]+)$/);
    if (match && request.method === "GET") {
      const id = decodeURIComponent(match[1]);
      const job = await env.DB.prepare(
        "SELECT id, mode, request, status, result_json, error, created_at, updated_at FROM jobs WHERE id = ?"
      ).bind(id).first();
      if (!job) return json({ error: "Job not found" }, { status: 404 });
      return json(job);
    }

    if (url.pathname === "/api/memory" && request.method === "GET") {
      const result = await env.DB.prepare(
        "SELECT label, content, created_at FROM memories ORDER BY id DESC LIMIT 50"
      ).all();
      return json({ memory: result.results || [] });
    }

    if (url.pathname === "/api/memory" && request.method === "POST") {
      const body = (await request.json()) as { label?: string; content?: string };
      const label = String(body.label || "").trim();
      const content = String(body.content || "").trim();
      if (!label || !content) return json({ error: "label and content are required" }, { status: 400 });
      await env.DB.prepare(
        "INSERT INTO memories(label, content, created_at) VALUES (?, ?, ?)"
      ).bind(label.slice(0, 80), content.slice(0, 20000), new Date().toISOString()).run();
      return json({ ok: true });
    }

    if (url.pathname === "/api/watchlist" && request.method === "GET") {
      const rows = await env.DB.prepare(
        "SELECT id, channel_id, label, enabled, created_at FROM watchlists ORDER BY id DESC LIMIT 50"
      ).all();
      return json({ watchlist: rows.results || [] });
    }

    if (url.pathname === "/api/watchlist" && request.method === "POST") {
      const body = (await request.json()) as { channel_id?: string; label?: string; enabled?: boolean };
      const channelId = String(body.channel_id || "").trim();
      if (!/^UC[\w-]{20,}$/.test(channelId)) {
        return json({ error: "Use a valid YouTube channel ID beginning with UC." }, { status: 400 });
      }
      await env.DB.prepare(
        "INSERT INTO watchlists(channel_id, label, enabled, created_at) VALUES (?, ?, ?, ?) ON CONFLICT(channel_id) DO UPDATE SET label=excluded.label, enabled=excluded.enabled"
      ).bind(channelId, String(body.label || "").slice(0, 120), body.enabled === false ? 0 : 1, new Date().toISOString()).run();
      return json({ ok: true, channel_id: channelId });
    }

    if (url.pathname === "/api/metrics" && request.method === "GET") {
      const rows = await env.DB.prepare(
        "SELECT * FROM metrics ORDER BY created_at DESC LIMIT 100"
      ).all();
      return json({ metrics: rows.results || [] });
    }

    if (url.pathname === "/api/metrics" && request.method === "POST") {
      const body = (await request.json()) as Record<string, unknown>;
      await env.DB.prepare(
        "INSERT INTO metrics(video_id,title,published_at,impressions,views,ctr,avg_view_duration_seconds,avg_percentage_viewed,likes,comments,notes,created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
      ).bind(
        String(body.video_id || "").slice(0, 80) || null,
        String(body.title || "").slice(0, 500) || null,
        String(body.published_at || "").slice(0, 80) || null,
        numberOrNull(body.impressions),
        numberOrNull(body.views),
        numberOrNull(body.ctr),
        numberOrNull(body.avg_view_duration_seconds),
        numberOrNull(body.avg_percentage_viewed),
        numberOrNull(body.likes),
        numberOrNull(body.comments),
        String(body.notes || "").slice(0, 4000) || null,
        new Date().toISOString()
      ).run();
      return json({ ok: true });
    }

    if (url.pathname === "/api/quota" && request.method === "GET") {
      const day = new Date().toISOString().slice(0, 10);
      const provider = (env.AI_PROVIDER || "gemini").toLowerCase();
      const row = await env.DB.prepare(
        "SELECT calls FROM usage WHERE day = ? AND provider = ?"
      ).bind(day, provider).first<{ calls: number }>();
      const calls = Number(row?.calls || 0);
      const limit = Number(env.GEMINI_DAILY_CALL_GUARD || "40");
      return json({ day, provider, calls, app_guard: limit, remaining_by_guard: Math.max(0, limit - calls) });
    }

    return json({ error: "Not found" }, { status: 404 });
  }
} satisfies ExportedHandler<Env>;
