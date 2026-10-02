declare module "cloudflare:workers" {
  export class WorkflowEntrypoint<Env = unknown, Params = unknown> {
    protected env: Env;
    constructor(ctx: unknown, env: Env);
  }

  export interface WorkflowEvent<T = unknown> {
    payload: T;
  }

  export interface WorkflowStep {
    do<T>(name: string, callback: () => Promise<T>): Promise<T>;
    do<T>(name: string, options: unknown, callback: () => Promise<T>): Promise<T>;
    sleep(name: string, duration: string): Promise<void>;
  }
}

interface D1PreparedStatement {
  bind(...values: unknown[]): D1PreparedStatement;
  run(): Promise<unknown>;
  first<T = Record<string, unknown>>(): Promise<T | null>;
  all<T = Record<string, unknown>>(): Promise<{ results?: T[] }>;
}

interface D1Database {
  prepare(query: string): D1PreparedStatement;
}

interface Env {
  ASSETS: { fetch(request: Request): Promise<Response> };
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

interface ExportedHandler<Environment = unknown> {
  fetch(
    request: Request,
    env: Environment,
    ctx: ExecutionContext
  ): Response | Promise<Response>;
}

interface ExecutionContext {
  waitUntil(promise: Promise<unknown>): void;
  passThroughOnException(): void;
}
