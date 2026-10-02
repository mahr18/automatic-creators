CREATE TABLE IF NOT EXISTS jobs (
  id TEXT PRIMARY KEY,
  mode TEXT NOT NULL,
  request TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'queued',
  result_json TEXT,
  output TEXT,
  error TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at);

CREATE TABLE IF NOT EXISTS memories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  label TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_memories_created_at ON memories(created_at);

CREATE TABLE IF NOT EXISTS ideas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  fingerprint TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_ideas_created_at ON ideas(created_at);

CREATE TABLE IF NOT EXISTS sources (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id TEXT,
  source_type TEXT NOT NULL,
  title TEXT,
  url TEXT,
  metadata_json TEXT,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sources_job_id ON sources(job_id);

CREATE TABLE IF NOT EXISTS usage (
  day TEXT NOT NULL,
  provider TEXT NOT NULL,
  calls INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY(day, provider)
);

CREATE TABLE IF NOT EXISTS watchlists (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  channel_id TEXT NOT NULL UNIQUE,
  label TEXT NOT NULL DEFAULT '',
  enabled INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_watchlists_enabled ON watchlists(enabled);

CREATE TABLE IF NOT EXISTS metrics (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  video_id TEXT,
  title TEXT,
  published_at TEXT,
  impressions INTEGER,
  views INTEGER,
  ctr REAL,
  avg_view_duration_seconds REAL,
  avg_percentage_viewed REAL,
  likes INTEGER,
  comments INTEGER,
  notes TEXT,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_metrics_created_at ON metrics(created_at);
