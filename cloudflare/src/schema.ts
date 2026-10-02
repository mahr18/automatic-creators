export const productionPackSchema = {
  type: "object",
  properties: {
    concept: { type: "string" },
    viewer_question: { type: "string" },
    hook: { type: "string" },
    script: { type: "string" },
    title_options: { type: "array", items: { type: "string" } },
    thumbnail_concept: { type: "string" },
    long_form: { type: "string" },
    shorts_cut: { type: "string" },
    visual_style: { type: "string" },
    continuity_rules: { type: "array", items: { type: "string" } },
    shots: {
      type: "array",
      minItems: 1,
      maxItems: 20,
      items: {
        type: "object",
        properties: {
          shot_id: { type: "string" },
          duration_seconds: { type: "integer", enum: [4, 6, 8] },
          purpose: { type: "string" },
          prompt: { type: "string" },
          negative_constraints: { type: "array", items: { type: "string" } },
          transition: { type: "string" }
        },
        required: [
          "shot_id",
          "duration_seconds",
          "purpose",
          "prompt",
          "negative_constraints",
          "transition"
        ]
      }
    }
  },
  required: [
    "concept",
    "viewer_question",
    "hook",
    "script",
    "title_options",
    "thumbnail_concept",
    "long_form",
    "shorts_cut",
    "visual_style",
    "continuity_rules",
    "shots"
  ]
} as const;

export const researchSchema = {
  type: "object",
  properties: {
    summary: { type: "string" },
    signals: { type: "array", items: { type: "string" } },
    gaps: { type: "array", items: { type: "string" } },
    risks: { type: "array", items: { type: "string" } },
    sources: {
      type: "array",
      items: {
        type: "object",
        properties: {
          title: { type: "string" },
          url: { type: "string" },
          note: { type: "string" }
        },
        required: ["title", "url", "note"]
      }
    }
  },
  required: ["summary", "signals", "gaps", "risks", "sources"]
} as const;

export const qualitySchema = {
  type: "object",
  properties: {
    qa: {
      type: "object",
      properties: {
        hook: { type: "integer" },
        visual_novelty: { type: "integer" },
        clarity: { type: "integer" },
        continuity: { type: "integer" },
        feasibility: { type: "integer" },
        repetition: { type: "integer" }
      },
      required: ["hook", "visual_novelty", "clarity", "continuity", "feasibility", "repetition"]
    },
    failures: { type: "array", items: { type: "string" } },
    repairs: { type: "array", items: { type: "string" } },
    final_pack: productionPackSchema
  },
  required: ["qa", "failures", "repairs", "final_pack"]
} as const;
