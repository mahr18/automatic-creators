interface Env {
  DB: D1Database;
  BRAIN_WORKFLOW: {
    create(options: { id?: string; params: unknown }): Promise<{ id: string }>;
    get(id: string): Promise<{ status(): Promise<unknown> }>;
  };
  GEMINI_API_KEY: string;
  BRAIN_ACCESS_TOKEN: string;
  AI_PROVIDER?: string;
  GEMINI_TEXT_MODEL?: string;
  GEMINI_MAX_OUTPUT_TOKENS?: string;
  GEMINI_DAILY_CALL_GUARD?: string;
  ENABLE_OPENAI_API?: string;
  OPENAI_API_KEY?: string;
  OPENAI_MODEL?: string;
  OPENAI_WEB_SEARCH?: string;
  YOUTUBE_API_KEY?: string;
  ENABLE_VIDEO_API?: string;
}
