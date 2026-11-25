import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class MemoryStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._lock, self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS observations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cycle_num INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    rationale TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS consolidated_knowledge (
                    topic TEXT PRIMARY KEY,
                    summary TEXT NOT NULL,
                    item_count INTEGER NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS hypotheses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    claim TEXT NOT NULL,
                    status TEXT NOT NULL,
                    evidence_score REAL NOT NULL,
                    updated_at TEXT NOT NULL
                );
            """)

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def add_observation(self, source: str, payload: dict[str, Any]) -> int:
        with self._lock, self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO observations (source, payload_json, created_at) VALUES (?, ?, ?)",
                (source, json.dumps(payload, ensure_ascii=False), self._now()),
            )
            return int(cur.lastrowid)

    def recent_observations(self, limit: int = 25) -> list[dict[str, Any]]:
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                "SELECT id, source, payload_json, created_at FROM observations ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        result: list[dict[str, Any]] = []
        for row in rows:
            result.append({
                "id": row["id"],
                "source": row["source"],
                "payload": json.loads(row["payload_json"]),
                "created_at": row["created_at"],
            })
        return result

    def add_decision(self, cycle_num: int, action: str, rationale: str, confidence: float) -> int:
        with self._lock, self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO decisions (cycle_num, action, rationale, confidence, created_at) VALUES (?, ?, ?, ?, ?)",
                (cycle_num, action, rationale, confidence, self._now()),
            )
            return int(cur.lastrowid)

    def recent_decisions(self, limit: int = 20) -> list[dict[str, Any]]:
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                "SELECT id, cycle_num, action, rationale, confidence, created_at FROM decisions ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def consolidate_topic(self, topic: str, summary: str, item_count: int) -> None:
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO consolidated_knowledge (topic, summary, item_count, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(topic) DO UPDATE SET
                    summary = excluded.summary,
                    item_count = consolidated_knowledge.item_count + excluded.item_count,
                    updated_at = excluded.updated_at
                """,
                (topic, summary, item_count, self._now()),
            )

    def get_knowledge(self) -> list[dict[str, Any]]:
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                "SELECT topic, summary, item_count, updated_at FROM consolidated_knowledge ORDER BY updated_at DESC"
            ).fetchall()
        return [dict(row) for row in rows]

    def record_hypothesis(self, claim: str, status: str, evidence_score: float) -> None:
        with self._lock, self._connect() as conn:
            conn.execute(
                "INSERT INTO hypotheses (claim, status, evidence_score, updated_at) VALUES (?, ?, ?, ?)",
                (claim, status, evidence_score, self._now()),
            )

    def recent_hypotheses(self, limit: int = 15) -> list[dict[str, Any]]:
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                "SELECT id, claim, status, evidence_score, updated_at FROM hypotheses ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]
