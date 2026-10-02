import { productionPackSchema, qualitySchema, researchSchema } from "./schema";

type AIJson = Record<string, unknown>;

const GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models";

function readModel(env: Env): string {
  return env.GEMINI_TEXT_MODEL || "gemini-3.8-flash";
}

function maxTokens(env: Env): number {
  const raw = Number(env.GEMINI_MAX_OUTPUT_TOKENS || "7000");
  return Number.isFinite(raw) ? Math.max(512, Math.min(raw, 12000)) : 7000;
}

async function callGemini(
  env: Env,
  prompt: string,
  schema: Record<string, unknown>,
  imageDataUrl?: string | null
): Promise<AIJson> {
  const model = readModel(env);
  const parts: Array<Record<string, unknown>> = [{ text: prompt }];

  if (imageDataUrl) {
    const match = imageDataUrl.match(/^data:(image\/[^;]+);base64,(.+)$/);
    if (match && match[2].length <= 1400000) {
      parts.push({
        inlineData: {
          mimeType: match[1],
          data: match[2]
        }
      });
    }
  }

  const response = await fetch(
    `${GEMINI_ENDPOINT}/${encodeURIComponent(model)}:generateContent`,
    {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-goog-api-key": env.GEMINI_API_KEY
      },
      body: JSON.stringify({
        contents: [{ role: "user", parts }],
        generationConfig: {
          responseMimeType: "application/json",
          responseSchema: schema,
          maxOutputTokens: maxTokens(env),
          thinkingConfig: { thinkingLevel: "high" }
        }
      })
    }
  );

  const payload = (await response.json()) as {
    error?: { message?: string };
    candidates?: Array<{ content?: { parts?: Array<{ text?: string }> } }>;
  };

  if (!response.ok) {
    throw new Error(payload.error?.message || `Gemini API returned HTTP ${response.status}`);
  }

  const text = payload.candidates?.[0]?.content?.parts?.map(p => p.text || "").join("") || "";
  if (!text) throw new Error("Gemini returned an empty response.");

  try {
    return JSON.parse(text) as AIJson;
  } catch {
    throw new Error("Gemini returned invalid JSON despite structured-output mode.");
  }
}

async function callOpenAI(
  env: Env,
  prompt: string,
  schema: Record<string, unknown>
): Promise<AIJson> {
  if (env.ENABLE_OPENAI_API !== "true") {
    throw new Error(
      "OPENAI_API_KEY is disabled by the $0 safety guard. Set ENABLE_OPENAI_API=true only when you intentionally want to use the paid OpenAI API."
    );
  }
  if (!env.OPENAI_API_KEY) throw new Error("OPENAI_API_KEY is not configured.");

  const model = env.OPENAI_MODEL || "gpt-5.6-luna";
  const response = await fetch("https://api.openai.com/v1/responses", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      authorization: `Bearer ${env.OPENAI_API_KEY}`
    },
    body: JSON.stringify({
      model,
      input: prompt,
      text: {
        format: {
          type: "json_schema",
          name: "maher_content_brain_output",
          strict: true,
          schema
        }
      }
    })
  });

  const payload = (await response.json()) as {
    error?: { message?: string };
    output_text?: string;
    output?: Array<{ content?: Array<{ text?: string }> }>;
  };

  if (!response.ok) throw new Error(payload.error?.message || `OpenAI API returned HTTP ${response.status}`);

  const text =
    payload.output_text ||
    payload.output?.flatMap(x => x.content || []).map(x => x.text || "").join("") ||
    "";

  if (!text) throw new Error("OpenAI returned an empty response.");
  return JSON.parse(text) as AIJson;
}

export async function generateJson(
  env: Env,
  prompt: string,
  schema: Record<string, unknown>,
  imageDataUrl?: string | null
): Promise<AIJson> {
  const provider = (env.AI_PROVIDER || "gemini").toLowerCase();
  if (provider === "openai") return callOpenAI(env, prompt, schema);
  return callGemini(env, prompt, schema, imageDataUrl);
}

export { productionPackSchema, researchSchema, qualitySchema };
