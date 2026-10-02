import sqlite3
from datetime import datetime, timezone
from pathlib import Path


class MemoryStore:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init(self):
        with self._connect() as db:
            db.execute(
                """CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    label TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )"""
            )
            db.execute(
                """CREATE TABLE IF NOT EXISTS runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mode TEXT NOT NULL,
                    request TEXT NOT NULL,
                    output TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )"""
            )
            db.commit()

    def add_memory(self, label: str, content: str) -> None:
        with self._connect() as db:
            db.execute(
                "INSERT INTO memories(label, content, created_at) VALUES (?, ?, ?)",
                (label, content, datetime.now(timezone.utc).isoformat()),
            )
            db.commit()

    def context(self, limit: int = 20) -> str:
        with self._connect() as db:
            rows = db.execute(
                "SELECT label, content, created_at FROM memories ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        if not rows:
            return "No saved project memories yet."
        return "\n\n".join(
            f"[{label}] {content} ({created_at})"
            for label, content, created_at in rows
        )

    def log_run(self, mode: str, request: str, output: str) -> None:
        with self._connect() as db:
            db.execute(
                "INSERT INTO runs(mode, request, output, created_at) VALUES (?, ?, ?, ?)",
                (mode, request, output, datetime.now(timezone.utc).isoformat()),
            )
            db.commit()
