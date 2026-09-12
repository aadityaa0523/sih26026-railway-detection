"""
EventLog: a SHA-256 hash-chained, tamper-evident record of every alert this device raises.

Every alert is potential NDPS-prosecution evidence, so the log itself has to answer a
courtroom question, not just an engineering one: "can you prove nobody edited this after
the fact?" Each record's hash commits to the previous record's hash plus its own payload
(the same structure a blockchain uses for the same reason), so editing any stored payload
breaks the chain at that point and .verify_chain() catches it -- no hardware or sync I/O here.
"""
import hashlib
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class EventRecord:
    id: int
    timestamp: str
    payload: dict
    prev_hash: str
    hash: str
    synced: bool


class EventLog:
    GENESIS_HASH = "0" * 64

    def __init__(self, db_path: str | Path):
        self._connection = sqlite3.connect(db_path)
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                payload TEXT NOT NULL,
                prev_hash TEXT NOT NULL,
                hash TEXT NOT NULL,
                synced INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        self._connection.commit()

    def record(self, event: dict) -> EventRecord:
        prev_hash = self._last_hash()
        timestamp = datetime.now(timezone.utc).isoformat()
        record_hash = self._compute_hash(prev_hash, event)
        cursor = self._connection.execute(
            "INSERT INTO events (timestamp, payload, prev_hash, hash, synced) VALUES (?, ?, ?, ?, 0)",
            (timestamp, self._canonical_json(event), prev_hash, record_hash),
        )
        self._connection.commit()
        return EventRecord(
            id=cursor.lastrowid,
            timestamp=timestamp,
            payload=event,
            prev_hash=prev_hash,
            hash=record_hash,
            synced=False,
        )

    def pending(self) -> list[EventRecord]:
        rows = self._connection.execute(
            "SELECT id, timestamp, payload, prev_hash, hash, synced FROM events WHERE synced = 0 ORDER BY id"
        ).fetchall()
        return [self._to_record(row) for row in rows]

    def mark_synced(self, record_id: int) -> None:
        self._connection.execute("UPDATE events SET synced = 1 WHERE id = ?", (record_id,))
        self._connection.commit()

    def verify_chain(self) -> bool:
        expected_prev_hash = self.GENESIS_HASH
        rows = self._connection.execute(
            "SELECT id, timestamp, payload, prev_hash, hash, synced FROM events ORDER BY id"
        ).fetchall()
        for row in rows:
            record = self._to_record(row)
            if record.prev_hash != expected_prev_hash:
                return False
            if self._compute_hash(record.prev_hash, record.payload) != record.hash:
                return False
            expected_prev_hash = record.hash
        return True

    def _last_hash(self) -> str:
        row = self._connection.execute("SELECT hash FROM events ORDER BY id DESC LIMIT 1").fetchone()
        return row[0] if row else self.GENESIS_HASH

    @staticmethod
    def _canonical_json(payload: dict) -> str:
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))

    @classmethod
    def _compute_hash(cls, prev_hash: str, payload: dict) -> str:
        digest_input = prev_hash + cls._canonical_json(payload)
        return hashlib.sha256(digest_input.encode("utf-8")).hexdigest()

    @staticmethod
    def _to_record(row: tuple) -> EventRecord:
        record_id, timestamp, payload_json, prev_hash, record_hash, synced = row
        return EventRecord(
            id=record_id,
            timestamp=timestamp,
            payload=json.loads(payload_json),
            prev_hash=prev_hash,
            hash=record_hash,
            synced=bool(synced),
        )
