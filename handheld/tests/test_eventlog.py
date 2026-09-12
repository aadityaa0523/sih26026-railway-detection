"""
Seam under test: EventLog(db_path) -- .record(), .pending(), .mark_synced(), .verify_chain()

Every alert this device raises is potential evidence in an NDPS prosecution. A log a defense
lawyer can plausibly claim was edited after the fact is worthless -- so each record's hash
chains to the previous record's hash (sha256(prev_hash + payload)), the same structure a
blockchain uses for the same reason. verify_chain() is the courtroom-facing question: "can
you prove nobody touched this?" These tests verify the chain logic against a real (temp)
SQLite file, not the hardware sync path.
"""
import sqlite3

from handheld.eventlog import EventLog


def test_record_chains_each_hash_to_the_previous_records_hash(tmp_path):
    log = EventLog(tmp_path / "events.db")

    first = log.record({"label": "clean", "confidence": 0.97})
    second = log.record({"label": "terpene_cannabis", "confidence": 0.91})

    assert first.prev_hash == EventLog.GENESIS_HASH
    assert second.prev_hash == first.hash
    assert first.hash != second.hash


def test_pending_lists_unsynced_records_until_marked_synced(tmp_path):
    log = EventLog(tmp_path / "events.db")
    first = log.record({"label": "clean"})
    second = log.record({"label": "terpene_cannabis"})

    assert [r.id for r in log.pending()] == [first.id, second.id]

    log.mark_synced(first.id)

    assert [r.id for r in log.pending()] == [second.id]


def test_verify_chain_is_true_for_an_untampered_log(tmp_path):
    log = EventLog(tmp_path / "events.db")
    log.record({"label": "clean"})
    log.record({"label": "terpene_cannabis", "confidence": 0.91})

    assert log.verify_chain() is True


def test_verify_chain_detects_a_record_mutated_directly_in_the_database(tmp_path):
    db_path = tmp_path / "events.db"
    log = EventLog(db_path)
    log.record({"label": "clean"})
    second = log.record({"label": "terpene_cannabis", "confidence": 0.91})

    # Simulate tampering: someone opens the raw SQLite file and edits a payload in place,
    # bypassing EventLog entirely -- exactly the attack this hash chain exists to catch.
    connection = sqlite3.connect(db_path)
    connection.execute(
        "UPDATE events SET payload = ? WHERE id = ?",
        ('{"label": "clean", "confidence": 0.91}', second.id),
    )
    connection.commit()
    connection.close()

    assert log.verify_chain() is False
